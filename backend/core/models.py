from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Job(models.Model):
    position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    position_url = models.URLField(max_length=255)
    company_url = models.URLField(max_length=255)
    published_date = models.CharField(null=True, blank=True)
    end_date = models.CharField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hr_ge'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()
    interests = models.ManyToManyField('Interest', blank=True)

    def __str__(self):
        return self.email

class Interest(models.Model):
    name = models.CharField(max_length=100)
    icon_path = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.icon_path:
            
            name_map = {
                "პროგრამირება": "images/icons/programming-icon.svg",
                "UI/UX დიზაინი": "images/icons/designer-icon.svg",
                "ქსელები": "images/icons/network-icon.svg",
                "გაყიდვები": "images/icons/sales-icon.svg",
                "მარკეტინგი": "images/icons/marketing-icon.svg",
                "არქიტექტურა": "images/icons/architecture-icon.svg",
            }
            self.icon_path = name_map.get(self.name, "icons/default.png")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name