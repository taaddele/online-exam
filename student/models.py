from django.db import models
from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
# custom user manager- rather than default user manger
class CustomUserManager(BaseUserManager):
    def create_user(self,id_no, password=None, **extra_fields):
        if not id_no:
            raise ValueError("id must be set")
        
        user = self.model(id_no = id_no, password = password,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,id_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(id_no, password, **extra_fields)
# custom user model
choices= {
    "M": "Male",
    "F": "Female",

}
class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    id_no = models.IntegerField(unique=True,primary_key=True) 
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    departement = models.CharField(max_length=40)
    sex = models.CharField(max_length=4,choices=choices)
    objects = CustomUserManager()
 
    USERNAME_FIELD = 'id_no'
   
    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('students')
        permissions = [
            ("can_manage_students", "Can manage students")
        ]
    def __str__(self): 
        return self.first_name

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    """def email_user(self, subject, message, from_email=None, **kwargs):
        
        #Sends an email to this User.
        
        send_mail(subject, message, from_email, [self.email], **kwargs)"""
    
