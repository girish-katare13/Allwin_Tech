from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import register_user,login_user, upload_images, get_user

urlpatterns = [
    path("api/register",register_user,name="registe"),
    path("api/login",login_user,name="login"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/upload_images',upload_images,name="upload_images"),
    path('api/get_user/', get_user, name='get_user'),
]
