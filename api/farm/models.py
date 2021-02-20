import uuid
from django.contrib.gis.db import models
from datetime import datetime
from django.utils import timezone
from api.auth_user.models import User
from api.farmer.models import Farmer

class Crop(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering =['name']

    def __str__(self):
        return self.name

class Farm(models.Model):
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    size = models.PositiveIntegerField(blank=False)
    deed_number = models.PositiveIntegerField(unique=True, blank=False)
    farm_metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    crop = models.ForeignKey(Crop, null=True, on_delete=models.SET_NULL)
    farmer = models.ForeignKey(Farmer, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    @property
    def created_by_user(self):
        if self.created_by:
            return self.created_by.email
        return None

    def __str__(self):
        return self.name

    class Meta:
        ordering =['created_at']


class FarmLocation(models.Model):
    point = models.PointField(blank=False)
    address = models.CharField(max_length=1200, blank=False)
    country = models.CharField(max_length=255, blank=False)
    administrative_area = models.CharField(max_length=1200, blank=False)
    location_metadata = models.JSONField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    farm = models.OneToOneField(Farm, related_name='location', null=True, on_delete=models.CASCADE)

    @property
    def longitude(self):
        return self.point[0]

    @property
    def latitude(self):
        return self.point[1]

    def __str__(self):
        return self.country

    class Meta:
        ordering =['created_at']
