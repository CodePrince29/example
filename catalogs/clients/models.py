from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
from users.models import UserProfile
from catalogs.price_list.models import PriceList
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime


class Client(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=150, null=False, blank=False)
    username = models.CharField(verbose_name=_('Customer User Name'), max_length=150, null=False, blank=False)
    password = models.CharField(verbose_name=_('Password'), max_length=150, null=False, blank=False)
    client_code = models.CharField(verbose_name=_('Client Code'), max_length=150, null=False, blank=False)
    contact_name = models.CharField(verbose_name=_('Contact Name'), max_length=150, null=False, blank=False)
    contact_phone = models.CharField(verbose_name=_('Contact Phone'), max_length=30, default="")
    email = models.CharField(verbose_name=_('Email'), max_length=150, null=False, blank=False)
    price_list = models.ForeignKey(PriceList, null=True)
    user = models.ForeignKey("users.UserProfile", null=True,on_delete=models.SET_NULL)
    barcoderead = models.BooleanField(verbose_name=_('Bar Code'), default=False)
    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('client-list')

    def get_products(self):
        return self.product_set.all()

    def get_product_family(self):
        from catalogs.product_family.models import ProductFamily
        from django.db.models import Prefetch
        product = Client.objects.first().product_set.all().prefetch_related(Prefetch("product_family"))
        queryset = ProductFamily.objects.filter(product__in=product).distinct()
        return queryset
    @property
    def can_delete(self):
        from catalogs.product.models import Product
        product = Product.objects.filter(customer=self)
        if len(product) >0:
            return True
        else:
            return False
        


@receiver(pre_save,sender=Client)
def create_user_for_customer(sender,**kwargs):
    import ast
    obj = kwargs['instance']
    users = UserProfile.objects.filter(username=obj.username)
    if not users.exists():
        user = UserProfile(
            email= ast.literal_eval(obj.email)[0],
            username = obj.username,
            is_staff=False,
            is_superuser=False,
            is_active=True
            # date_joined=datetime.now()
            )
        user.set_password(obj.password)
        user.save()
    # else:
    #     user = users.first()
    #     user.email= ast.literal_eval(obj.email)[0]
    #     user.username = obj.username
    #     user.set_password(obj.password)
    #     user.save()
        obj.user = user

