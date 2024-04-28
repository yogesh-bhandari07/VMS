from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from management.serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from .models import *
from django.shortcuts import get_object_or_404
import os
from datetime import datetime,timedelta
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from django.db.models import  F, Value, CharField
from django.http import HttpResponse

import requests
from django.db.models import Max
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        
        serializer = UserRegistrationSerializer(data=request.data)
       
        
        if serializer.is_valid():

            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'message': 'Registration Successfull','data':{"user":serializer.data,"token":token}},  status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Validation Error','data':serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserLoginView(APIView):
   

    def post(self, request, format=None):

        if request.data['email'] is not None:
            if User.objects.filter(email=request.data['email']).filter(is_active=True).exists():
                email = request.data['email']
                password = request.data['password']
                user = authenticate(email=email, password=password)
                
                if user is not None:
                    token = get_tokens_for_user(user)
                    return Response({'message': 'Login Success', 'data': {'user':model_to_dict(user),"token":token},"error":False,"status_code":200}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "Invalid username or password","data":None,"error":True,"status_code":400}, status=status.HTTP_200_OK)
     
            else:
            
                return Response({'message': "Invalid username or password","data":None,"error":True,"status_code":404}, status=status.HTTP_200_OK)
     
   



class VendorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = VendorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Vendor has been created', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':True,'data':None}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        try:
            if pk is not None:
                vendor = Vendor.objects.get(id=pk)
                serializer = VendorSerializer(vendor)
                return Response({"message": 'Data Fetched', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
            else:
                vendors = Vendor.objects.filter(status=True)
                serializer = VendorSerializer(vendors, many=True)
                return Response({"message": 'Data Fetched', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"message": 'Vendor not found', "status": 404,'error':False,'data':None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':False,'data':None}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            vendor = Vendor.objects.get(id=pk)
            serializer = VendorSerializer(vendor, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Data updated', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"message": 'Vendor not found', "status": 404,'error':True,'data':None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':True,'data':None}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        try:
            vendor = Vendor.objects.get(id=pk)
            serializer = VendorSerializer(vendor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Data updated partially', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"message": 'Vendor not found', "status": 404,'error':True,'data':None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':True,'data':None}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            vendor = Vendor.objects.get(id=pk)
          
            vendor.delete()
            return Response({"message": "Vendor has been deleted", "status": 200,'error':False,'data':None}, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"message": 'Vendor not found', "status": 404,'error':True,'data':None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':True,'data':None}, status=status.HTTP_400_BAD_REQUEST)






class PurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = PurchaseOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Purchase Order has been created', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'error':False,'data':None}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        try:
            if pk is not None:
                purchaseOrder = PurchaseOrder.objects.get(id=pk)
                serializer = PurchaseOrderSerializer(purchaseOrder)
                return Response({"message": 'Data Fetched', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
            else:
                purchaseOrders = PurchaseOrder.objects.filter(status=True)
                serializer = PurchaseOrderSerializer(purchaseOrders, many=True)
                return Response({"message": 'Data Fetched', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": 'PurchaseOrder not found', "status": 404,'data':None,'error':True}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'data':None,'error':True}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            purchaseOrder = PurchaseOrder.objects.get(id=pk)
            serializer = PurchaseOrderSerializer(purchaseOrder, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Data updated', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": 'PurchaseOrder not found', "status": 404,'data':None,'error':False}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'data':None,'error':False}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        try:
            purchaseOrder = PurchaseOrder.objects.get(id=pk)
            serializer = PurchaseOrderSerializer(purchaseOrder, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": 'Data updated partially', "status": 200, "data": serializer.data,'error':False}, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": 'PurchaseOrder not found', "status": 404,'data':None,'error':False}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'data':None,'error':False}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            purchaseOrder = PurchaseOrder.objects.get(id=pk)
            purchaseOrder.delete()
            return Response({"message": "PurchaseOrder has been deleted", "status": 200,'data':None,'error':False}, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": 'PurchaseOrder not found', "status": 404,'data':None,'error':False}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400,'data':None,'error':False}, status=status.HTTP_400_BAD_REQUEST)


class VendorPerformanceView(APIView):
    def get(self, request, pk=None, format=None):
        try:
            vendor = get_object_or_404(Vendor, pk=pk)
            on_time_delivery_rate = vendor.on_time_delivery_rate
            quality_rating_avg = vendor.quality_rating_avg
            fulfillment_rate = vendor.fulfillment_rate

         
            average_response_time_seconds = vendor.average_response_time
            average_response_time_timedelta = timedelta(seconds=average_response_time_seconds)

            
            response_time_days = average_response_time_timedelta.days
            response_time_hours, remainder = divmod(average_response_time_timedelta.seconds, 3600)
            response_time_minutes, _ = divmod(remainder, 60)

            response_time_str = f"{response_time_days} days, {response_time_hours} hours, {response_time_minutes} minutes"

            return Response({
                "message": 'Data Fetched',
                'data': {
                    'on_time_delivery_rate': on_time_delivery_rate,
                    'quality_rating_avg': quality_rating_avg,
                    'average_response_time': response_time_str,
                    'fulfillment_rate': fulfillment_rate
                },
                'error': False,
                "status": 200
            }, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"message": 'Vendor not found', "status": status.HTTP_404_NOT_FOUND, 'error': False, 'data': None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": status.HTTP_400_BAD_REQUEST, 'error': False, 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        

class AcknowledgePurchaseOrder(APIView):
    def post(self, request, po_id, format=None):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)

            if purchase_order.acknowledgment_date is not None:

                return Response({"message": 'Already acknowledged', "status": 200,'data':None,'error':False}, status=status.HTTP_200_OK)

            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.save()
            return Response({"message": 'Purchase order acknowledged successfully', "status": 200,'data':None,'error':False}, status=status.HTTP_200_OK)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": 'Purchase order not found', "status": 404,'data':None,'error':True}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": 400}, status=status.HTTP_400_BAD_REQUEST)