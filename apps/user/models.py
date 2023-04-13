from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MaxValueValidator,MinValueValidator
from slugify import slugify
from django.db.models.signals import post_save
import requests
from django.conf import settings
activecampaign_url = settings.ACTIVE_CAMPAIGN_URL
activecampaign_key = settings.ACTIVE_CAMPAIGN_KEY
from djoser.signals import  user_registered
import uuid,json
# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY
import requests
from core.producer import producer
import re

pattern_special_characters = r'\badmin\b|[!@#$%^&*()_+-=[]{}|;:",.<>/?]|\s'


# from apps.product.models import ProductsLibrary, WishlistProductsLibrary

def user_profile_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    profile_pic_name = 'users/{0}/profile.jpg'.format(str(uuid.uuid4()))

def user_banner_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    banner_pic_name = 'users/{0}/banner.jpg'.format(str(uuid.uuid4()))


class UserAccountManager(BaseUserManager):


    def create_user(self, email, password=None, **extra_fields):
        
        def create_slug(username):
            pattern_special_characters = r'\badmin\b|[!@#$%^~&*()_+-=[]{}|;:",.<>/?]|\s'
            if re.search(pattern_special_characters, username):
                raise ValueError('Username contains invalid characters')
            username = re.sub(pattern_special_characters, '', username)
            return slugify(username)
            
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        extra_fields['slug'] = create_slug(extra_fields['username'])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Send HTTP Request to Cart microservice containing the user data so cart microservice can create a cart for this user
        item={}
        item['id']=str(user.id)
        item['email']=user.email
        item['username']=user.username
        producer.produce(
            'user_registered',
            key='create_user',
            value=json.dumps(item).encode('utf-8')
        )
        producer.flush()

        if user.agreed:
            # Send HTTP Request to Cart microservice containing the user data so cart microservice can create a cart for this user
            item={}
            item['id']=str(user.id)
            item['email']=user.email
            item['username']=user.username
            item['first_naame']=user.first_name
            item['last_name']=user.last_name
            producer.produce(
                'user_registered',
                key='user_agreed',
                value=json.dumps(item).encode('utf-8')
            )
            producer.flush()

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.role="Admin"
        user.verified=True
        user.become_seller=True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    roles = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('helper', 'Helper'),
        ('editor', 'Editor'),
    )

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)

    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    agreed = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    become_seller = models.BooleanField(default=False)
    sellerAcceptedTerms = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=roles, default='customer')
    verified = models.BooleanField(default=False)

    rating =                        models.ManyToManyField('Rate',blank=True, related_name='courseRating')
    student_rating =                models.IntegerField(default=0, blank=True, null=True)
    students =                      models.IntegerField(default=0, blank=True)
    courses =                      models.IntegerField(default=0, blank=True)
    products =                      models.IntegerField(default=0, blank=True)
    buyers =                      models.IntegerField(default=0, blank=True)
    earned =                      models.FloatField(default=0, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'agreed']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        counter = 1
        while UserAccount.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{counter}"
            counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
    def get_rating(self):
        ratings=self.rating.all()
        rate=0
        for rating in ratings:
            rate+=rating.rate_number
        try:
            rate/=len(ratings)
        except ZeroDivisionError:
            rate=0
        return rate

    def get_no_rating(self):
        return len(self.rating.all())


class Rate(models.Model):
    rate_number =               models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    user =                      models.UUIDField(blank=True, null=True)
    instructor =                    models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='rate_belongs_to_instructor', blank=True, null=True)



# def post_user_confirmed(request, user ,*args, **kwargs):
#     #1. Definir usuario que ser registra
#     user = user
#     #2. Crear cliente en stripe
#     stripe_customer = stripe.Customer.create(
#         email=user.email,
#         name=user.first_name+" "+user.last_name
#     )
#     #3 Agegar Stripe Customer ID a Modelo de Usuario
#     user.stripe_customer_id = stripe_customer["id"]
#     user.save()

#     #4 Crear Stripe Connect Account ID
#     connect_account = stripe.Account.create(
#         type = "express",
#         capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
#     )
#     user.stripe_account_id = connect_account["id"]
#     user.save()
# user_registered.connect(post_user_confirmed)