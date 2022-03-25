from rest_framework import serializers
from account.models import User, UserDetails
from django.utils.encoding import smart_str, force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from account.utils import Util

class UserSerializer(serializers.Serializer):
  class Meta:
    model = User
    fields = ['email','name','password', 'is_active','is_admin','created_at','updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','name','password', 'password2']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm password not match")
        return attrs
    
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['date_of_birth','gender','profile','is_verified']
   
    def validate(self, attrs):
      user = self.context.get('user')
      date_of_birth= attrs.get('date_of_birth')
      gender = attrs.get('gender')
      profile = attrs.get('profile')
      is_verified = attrs.get('is_verified')
      user_details = UserDetails(user=user)
      if date_of_birth is not None:
        user_details.date_of_birth = date_of_birth
      if gender is not None:
        user_details.gender = gender
      if profile is not None:
        user_details.profile = profile
      if is_verified is not None:
        user_details.is_verified = is_verified     
      user_details.save()
      return attrs

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['date_of_birth','gender','profile','is_verified']
  
        

class UserChangePasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    user = self.context.get('user')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user.set_password(password)
    user.save()
    return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer): 
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid =  urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'https://localhost:8000/api/user/reset/'+uid+'/'+token
            body = 'Click Following Link to Reset Your Password '+link
            data = {
            'subject':'Reset Your Password',
            'body':body,
            'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        
        else:
            raise serializers.ValidationError('You are not Register User')

class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      password2 = attrs.get('password2')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != password2:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = User.objects.get(id=id)
      print("user",user ,id)
      print("\n \n")
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')
    
    
  