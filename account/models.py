from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, password2=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user







class User(AbstractBaseUser):
    email = models.EmailField(max_length=255,unique=True,verbose_name='Email')
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    def __str__(self):
        return self.email
    
    def has_perm(self, perm,obj=None):
        "Does the user have specific permission ?"
        return self.is_admin
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def is_staff(self):
        "is the user a member of staff?"
        return self.is_admin
    


class UserDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date_of_birth = models.DateTimeField(blank=True,null=True)
    gender = models.CharField(max_length=10,blank=True,null=True)
    profile = models.ImageField(upload_to='profile', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    