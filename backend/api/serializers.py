from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, Image, UploadedFile, DummyData
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
# from .models import Image
# from .models import UploadedFile
# from .models import DummyData 

CustomUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        
        if password:
            user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')




class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = ['id', 'title', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'original_name', 'file_size', 'file_type', 'uploaded_at']
        read_only_fields = ['original_name', 'file_size', 'file_type', 'uploaded_by', 'uploaded_at']

    def validate_file(self, value):
        # Example validation: Limit file size to 10MB
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(f"File too large. Max size is {max_size/1024/1024}MB.")
        return value






class DummyDataSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    created_at = serializers.DateField(format="%Y-%m-%d")
    
    class Meta:
        model = DummyData
        fields = [
            'id', 'name', 'category', 'category_display', 
            'value', 'quantity', 'status', 'status_display',
            'location', 'rating', 'is_active', 'stock_status',
            'profit_margin', 'created_at'
        ]
    
    def get_stock_status(self, obj):
        return obj.stock_status()
    
    def get_profit_margin(self, obj):
        return obj.profit_margin()