import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin
from account.models import User, UserDetails 
from account.renderers import UserRenderer
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserProfileUpdateSerializer, UserRegistrationSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken



#Generate Token manually 
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class AdminUserLists(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        users = User.objects.all()
        print (" \n \n",type(users)," \n \n")
        data = []
        for user in users:
            print ( user.id,user.name, user.email, user.created_at, user.updated_at, user.is_active,user.is_admin)
            print("\n")
            details = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "joined_on": user.created_at,
                "updated_at": user.updated_at,
                "active":user.is_active,
                "admin": user.is_admin
                
                
            }
            data.append(details)
        print( data)
        return data



class AdminUserList(APIView):
    renderer_class = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request,format=None):
        users = User.objects.all()
        # print (" \n \n",type(users)," \n \n")
        data = []
        for user in users:
            # print ( user.id,user.name, user.email, user.created_at, user.updated_at, user.is_active,user.is_admin)
            # print("\n")
            profile = UserDetails.objects.get(id =1)
            print("\n profile",profile.profile)
            details = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "joined_on": user.created_at,
                "updated_at": user.updated_at,
                "active":user.is_active,
                "admin": user.is_admin,
                "profile": profile.profile
                
                
            }
            
            data.append(details)
        # print( data)
        return Response({"data": data}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    renderer_class = [UserRenderer]
    def post(self, request, format=None):
        serializer  = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'msg':'Registeration successfull', 'token':token}, status=status.HTTP_201_CREATED)
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    

class UserLoginView(APIView):
    renderer_class = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None :
                token = get_tokens_for_user(user)
                return Response({'token': token,'msg':'login successfull'}, status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_fields_errors':['email or password not valid']}}, status=status.HTTP_404_NOT_FOUND)

        

class UserChangePasswordView(APIView):
    renderer_class = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'password change successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class SendPasswordResetEmailView(APIView):
    renderer_class = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'password reset link send please check your email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)

# class UserDetails(APIView):
#     renderer_classes = [UserRenderer]
    
#     def get(self,request,pk=None,format=None):
#         print("User", request.user)
            


class UserProfileView(APIView):
    renderer_class = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        if UserDetails.objects.filter(user=request.user).exists():
            serializer = UserProfileSerializer(request.user)
            user  = User.objects.get(email=request.user)
            user_details = UserDetails.objects.get(user=user)
            print('\n \n  \n  user', user.name,user.email,user.is_active,user.created_at,user.updated_at, serializer.data ,"\n \n ")
            details = {"user_id":user_details.id,"name":user.name, "email":user.email, "is_active":user.is_active, "created_at":user.created_at, "updated_at":user.updated_at,"details":serializer.data}
            return Response({ "details":details},status=status.HTTP_200_OK)
        return Response({"msg":"doesn't exist","details":False})

    def post(self,request, format=None):
        # profile = request.FILE('profile')
        # print("\n profile",request.data['file'],"\n")
        # print("\n profile",request.data['profile'],"\n")
        serializer =  UserProfileSerializer(data=request.data,context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return  Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    # def put(self, request,format=None):
    #     user_details = UserDetails.objects.get(pk=1)
    #     print("puting user details",user_details)
    #     serializer = UserProfileSerializer(user_details,data=request.data,context={'user': request.user})
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response({'msg':'Complete Data Update'}, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    # def patch(self, request,format=None):
    #     user_details = UserDetails.objects.get(pk=1)
    #     # user_details = 'hello'
    #     print("patch user details",request.user)
    #     print("patch user details",user_details)
    #     serializer = UserProfileSerializer(user_details,data=request.data,context={'user': request.user}, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response({'msg':'Complete Data Update'}, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        
    def delete(self, request, format=None):
        user_details = UserDetails.objects.get(user=request.user)
        user_details.delete()
        return Response({'msg':'Complete Data Delete'}, status=status.HTTP_200_OK)


class UpdateUserDetails(GenericAPIView,UpdateModelMixin):
    queryset = UserDetails.objects.all()
    serializer_class = UserProfileUpdateSerializer

    # def get_queryset(self):
    #     print (" \n \n get_queryset \n \n", self.request.user.id)
    #     return UserDetails.objects.filter(pk = self.request.user.id)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)