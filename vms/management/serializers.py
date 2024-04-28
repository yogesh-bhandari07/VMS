from dataclasses import fields
from rest_framework import serializers
from management.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import *
import re
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name'] 
    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        return data['first_name']+" "+data['last_name']






class UserRegistrationSerializer(serializers.ModelSerializer):
   


    class Meta:
        model = User
        fields ='__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def validate(self, data):
       
        password = data.get('password')
        if password is None:
            raise serializers.ValidationError(
                "Password required")
 

        return data

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email","password"]



class VendorSerializer(serializers.ModelSerializer):
    average_response_time = serializers.SerializerMethodField()
    class Meta:
        model = Vendor
        fields = '__all__'





    def get_average_response_time(self, obj):
        avg_response_seconds = obj.average_response_time
        if avg_response_seconds:
            days, remainder = divmod(avg_response_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            return {
                'days': int(days),
                'hours': int(hours),
                'minutes': int(minutes),
                'seconds': int(seconds)
            }
        else:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.updated_at.strftime("%d/%m/%Y, %I:%M %p").lower()
        representation['updated_at'] = instance.updated_at.strftime("%d/%m/%Y, %I:%M %p").lower()
        return representation

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime("%d/%m/%Y, %I:%M %p").lower() if instance.created_at is not None else None
        representation['updated_at'] = instance.updated_at.strftime("%d/%m/%Y, %I:%M %p").lower() if instance.updated_at is not None else None
        representation['delivery_date'] = instance.delivery_date.strftime("%d/%m/%Y, %I:%M %p").lower() if instance.delivery_date is not None else None
        representation['order_date'] = instance.order_date.strftime("%d/%m/%Y, %I:%M %p").lower() if instance.order_date is not None else None
        representation['acknowledgment_date'] = instance.acknowledgment_date.strftime("%d/%m/%Y, %I:%M %p").lower() if instance.acknowledgment_date is not None else None
        return representation