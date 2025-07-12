from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import UserSerializer, UserLoginSerializer, ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import re
from .models import Image
from .models import DummyData   
from .serializers import ImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadedFile
from .serializers import FileUploadSerializer, DummyDataSerializer
import os
from django.utils import timezone
from datetime import timedelta
import random

from django.conf import settings

from django.http import HttpResponse



CustomUser = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Registration failed",
                    "errors": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                    "status": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Registration failed",
                    "error": str(e),
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Login failed",
                    "errors": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "status": status.HTTP_200_OK,
            }
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            {
                "success": True,
                "message": "Profile retrieved successfully",
                "user": serializer.data,
                "status": status.HTTP_200_OK,
            }
        )


class ProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "Profiles retrieved successfully",
                "data": serializer.data,
                "count": len(serializer.data),
                "status": status.HTTP_200_OK,
            }
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Profile creation failed",
                    "errors": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(created_by=request.user)
        return Response(
            {
                "success": True,
                "message": "Profile created successfully",
                "data": serializer.data,
                "status": status.HTTP_201_CREATED,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "success": True,
                "message": "Profile retrieved successfully",
                "data": serializer.data,
                "status": status.HTTP_200_OK,
            }
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Profile update failed",
                    "errors": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data,
                "status": status.HTTP_200_OK,
            }
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "success": True,
                "message": "Profile deleted successfully",
                "status": status.HTTP_204_NO_CONTENT,
            },
            status=status.HTTP_204_NO_CONTENT,
        )




class IFSCLookupView(APIView):
    permission_classes = [permissions.AllowAny]  # Corrected from AllowAll to AllowAny
    
    def get(self, request, ifsc_code):
        try:
            # Razorpay IFSC API endpoint
            url = f"https://ifsc.razorpay.com/{ifsc_code}"
            
            # Make the request to Razorpay's API
            response = requests.get(url)
            
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "IFSC code not found or invalid"},
                    status=response.status_code
                )
                
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to connect to IFSC service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )





class ImageUploadView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class ImageListView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}

class ImageDownloadView(generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.image:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # For direct file response
        file_path = instance.image.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='image/jpeg')  # Adjust content type as needed
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)







class SetAuthCookieView(APIView):
    def post(self, request):
        refresh = RefreshToken.for_user(request.user)
        response = Response({
            "success": True,
            "message": "Authentication cookies set successfully",
        })
        
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=False,  # False for development
            samesite='Lax',
            domain='localhost',
            max_age=24 * 3600  # 1 day
        )
        return response

class CheckAuthCookiesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "has_access_token": request.COOKIES.get('access_token') is not None,
            "has_refresh_token": request.COOKIES.get('refresh_token') is not None,
            "status": status.HTTP_200_OK,
        })

class ClearAuthCookiesView(APIView):
    def post(self, request):
        response = Response({
            "success": True,
            "message": "Cookies cleared successfully",
        })
        response.delete_cookie('access_token', domain='localhost')
        return response

class FileUploadView(generics.CreateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file_obj = self.request.FILES['file']
        serializer.save(
            uploaded_by=self.request.user,
            original_name=file_obj.name,
            file_size=file_obj.size,
            file_type=file_obj.content_type
        )

class UserFilesListView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UploadedFile.objects.filter(uploaded_by=self.request.user)

class FileDownloadView(generics.RetrieveAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.uploaded_by != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        file_path = instance.file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=instance.file_type)
                response['Content-Disposition'] = f'attachment; filename="{instance.original_name}"'
                return response
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)







class DummyDataTableView(generics.ListAPIView):
    serializer_class = DummyDataSerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed
    
    def get_queryset(self):
        # Check if dummy data exists
        if not DummyData.objects.exists():
            self.create_dummy_data()
        return DummyData.objects.all()
    
    def create_dummy_data(self):
        categories = {
            'tech': ['Laptop', 'Smartphone', 'Tablet', 'Smartwatch', 'Headphones'],
            'health': ['Vitamins', 'Protein Powder', 'Fitness Tracker', 'Yoga Mat', 'Massage Gun'],
            'finance': ['Investment Plan', 'Insurance Policy', 'Credit Card', 'Loan Package', 'Savings Account'],
            'education': ['Online Course', 'Textbook', 'E-Learning Subscription', 'Workshop', 'Certification'],
            'home': ['Furniture', 'Appliances', 'Decor', 'Lighting', 'Cookware']
        }
        
        statuses = ['in_stock', 'low_stock', 'out_of_stock', 'discontinued']
        locations = ['Warehouse A', 'Warehouse B', 'Store Front', 'Online Only']
        
        for i in range(50):  # Generate 50 diverse records
            category = random.choice(list(categories.keys()))
            product_name = random.choice(categories[category])
            variation = random.choice(['Pro', 'Plus', 'Max', 'Lite', 'Standard'])
            
            # Use Decimal for the value field
            min_val = Decimal('10') if category == 'education' else Decimal('50')
            max_val = Decimal('500') if category == 'tech' else Decimal('1000')
            random_value = min_val + (max_val - min_val) * Decimal(str(random.random()))
            
            DummyData.objects.create(
                name=f"{product_name} {variation}",
                category=category,
                value=round(random_value, 2),
                quantity=random.randint(0, 200),
                status=random.choice(statuses),
                location=random.choice(locations),
                rating=Decimal(str(round(random.uniform(1, 5), 1))),
                is_active=random.choices([True, False], weights=[70, 30])[0],
                created_at=timezone.now() - timedelta(days=random.randint(0, 730))
            )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "success": True,
            "message": "Dummy data retrieved successfully",
            "data": serializer.data,
            "count": queryset.count(),
            "status": status.HTTP_200_OK
        })