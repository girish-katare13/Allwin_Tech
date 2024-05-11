from django.shortcuts import render
from .serializers import UserRegistrationSerializer, UserLoginSerializer,ImageUploadSerializer, ImageSerializer,UserWithImagesSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Image,UserProfile

# Create your views here.
@csrf_exempt
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':"User registered successfully"}, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data= request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(request,username=username,password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({'refresh':str(refresh),'access':str(refresh.access_token)},status= status.HTTP_200_OK)
            return Response({'message':'invalid credentential'},status= status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_images(request):
    if request.method == 'POST':
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            images_data = serializer.validated_data['images']
            uploaded_images = []
            for image_data in images_data:
                # Create a new Image instance associated with the logged-in user
                new_image = Image.objects.create(user=user_profile, image=image_data)
                uploaded_images.append(new_image.image.url)
            # Return a response with success message and image URLs
            last_uploaded_image = uploaded_images[-1] if uploaded_images else None
            return Response({"message": "Images uploaded successfully", "last_uploaded_image_url": last_uploaded_image})
        # Return a response with serializer errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])  
@permission_classes([IsAuthenticated])          
def get_user(request):
    if request.method == 'GET':
        # Retrieve the profile of the logged-in user
        user = request.user
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        # Serialize the user profile along with all associated images
        serializer = UserWithImagesSerializer(user_profile)
        return Response(serializer.data)  