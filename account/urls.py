from django.contrib import admin
from django.urls import path, include
from .views import SendPasswordResetEmailView, UpdateUserDetails, UserChangePasswordView, UserLoginView, UserPasswordResetView, UserProfileView, UserRegistrationView
urlpatterns = [
path('register/',UserRegistrationView.as_view(), name='register'),
path('login/',UserLoginView.as_view(), name='login'),
path('profile/',UserProfileView.as_view(), name='profile'),
path('profileupdate/<int:pk>/',UpdateUserDetails.as_view(), name='profileupdate'),
path('profileupdate/',UpdateUserDetails.as_view(), name='profileupdate'),
path('changepassword/',UserChangePasswordView.as_view(), name='changepassword'),
path('reset-password-email/',SendPasswordResetEmailView.as_view(), name='resetpasswordlink'),
path('reset-password/<uid>/<token>/',UserPasswordResetView.as_view(), name='reset-password'),

]
