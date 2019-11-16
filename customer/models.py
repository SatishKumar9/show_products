from django.forms import ValidationError
from django.db import models
from django.contrib.auth.models import User
from vendor.models import Product
from django.db.models.signals import post_save


def phone_number_validation(ph_num):
    if len(str(ph_num)) != 10:
        raise ValidationError('The phone number must have 10 digits only')
    elif ph_num < 0:
        raise ValidationError('The phone number must be positive')


class CustomerProfile(models.Model):
    Customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cus')
    prod = models.ManyToManyField(Product, blank=True)
    phone_number = models.IntegerField(null=True, validators=[phone_number_validation])
    address = models.TextField(null=True)

    def __str__(self):
        return self.Customer.username


def post_save_customerprofile_create(sender, instance, created, *args, **kwargs):
    if created:
        CustomerProfile.objects.get_or_create(Customer=instance)


post_save.connect(post_save_customerprofile_create, sender=User)
