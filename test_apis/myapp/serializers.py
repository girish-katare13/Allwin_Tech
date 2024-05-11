from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Image

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    user_type = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm','user_type']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user_type = validated_data.pop('user_type')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, user_type=user_type)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField())

    def create(self, validated_data):
        user = self.context['request'].user
        images_data = validated_data.get('images', [])
        uploaded_images = []
        for image_data in images_data:
            # Create a new Image instance associated with the logged-in user
            new_image = Image.objects.create(user=user, image=image_data)
            uploaded_images.append(new_image)
        return uploaded_images

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'user']

class UserWithImagesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user_id', 'user_type', 'user_name', 'timestamp', 'images']

    def get_user_name(self, obj):
        # Fetch the user object associated with the UserProfile instance
        user = obj.user
        # Get the username from the user object
        return user.username
    
    def get_user_type(self, obj):
        # Fetch the user type from the UserProfile instance
        return obj.user.user_type if hasattr(obj.user, 'user_type') else None

    def get_images(self, obj):
        images_queryset = Image.objects.filter(user=obj)
        return ImageSerializer(images_queryset, many=True).data