from distutils.text_file import TextFile
from re import U
import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.db.models import Q
from django.db.models.signals import post_save,pre_save
from .middleware import _request_local
from django.utils import timezone
import pytz
#  Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email,first_name,last_name,  password=None):
      
        """
        Creates and saves a User with the given email, name, password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
      
        user.set_password(password)
        
        

        user.save(using=self._db)



            
        return user

    def create_superuser(self, email,mobile, first_name,last_name,  password=None):
        """
        Creates and saves a superuser with the given email, name, password.
        """
        user = self.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name, 
        password=password,
            
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#  Custom User Model
class User(AbstractBaseUser,PermissionsMixin):

    class Meta:
        db_table = 'member'

    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    password=models.CharField(max_length=250,blank=True,null=True)
    
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password=models.CharField(max_length=250,blank=True,null=True)
    is_superuser=models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name","last_name","mobile"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
  
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"

        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
   
        return self.is_admin





class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT, related_name='%(class)s_updated_by', db_column='updated_by')

    class Meta:
        abstract = True  

    def save(self, *args, **kwargs):
        try:
   
            if hasattr(_request_local, 'request') and hasattr(_request_local.request, 'updated_by'):
                updated_by_id = _request_local.request.updated_by
                if updated_by_id is not None:
                    user = User.objects.get(id=updated_by_id)
                    self.updated_by = user
                    self.updated_at = timezone.localtime(timezone.now(), pytz.timezone('Asia/Kolkata'))
        except Exception as e:
     
            pass

        super().save(*args, **kwargs)


class Vendor(BaseModel):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

class PurchaseOrder(BaseModel):
    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField(blank=True,null=True)
    items = models.JSONField()
    quantity = models.IntegerField()
    order_status = models.CharField(max_length=50,blank=True,null=True)
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(blank=True,null=True)
    acknowledgment_date = models.DateTimeField(null=True)

class HistoricalPerformance(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()


@receiver(post_save, sender=PurchaseOrder)
def update_vendor_performance(sender, instance, created, **kwargs):
    if not created:
        vendor = instance.vendor
        total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
        successful_orders = PurchaseOrder.objects.filter(vendor=vendor, order_status='completed').count()
        on_time_deliveries = PurchaseOrder.objects.filter(vendor=vendor, order_status='completed', delivery_date__lte=instance.delivery_date).count()

        vendor.on_time_delivery_rate = (on_time_deliveries / total_orders) * 100 if total_orders > 0 else 0.0
        vendor.fulfillment_rate = (successful_orders / total_orders) * 100 if total_orders > 0 else 0.0

  
        ratings = PurchaseOrder.objects.filter(vendor=vendor, order_status='completed').exclude(quality_rating__isnull=True).values_list('quality_rating', flat=True)
        vendor.quality_rating_avg = sum(ratings) / len(ratings) if ratings else 0.0


        response_times = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False).annotate(response_time=models.F('acknowledgment_date') - models.F('issue_date')).aggregate(avg_response_time=models.Avg('response_time'))
        vendor.average_response_time = response_times['avg_response_time'].total_seconds() if response_times['avg_response_time'] else 0.0

        vendor.save()

