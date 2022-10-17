from django.db import models
from django.contrib import admin

# Create your models here.


class Shop(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    longitude = models.FloatField()
    latitude = models.FloatField()
    open_hours = models.CharField(max_length=200)
