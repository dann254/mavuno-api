import uuid

from django.db import models
from datetime import datetime
from django.utils import timezone
from api.auth_user.models import User
from api.farm.models import Farm


class Harvest(models.Model):
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    wet_weight = models.PositiveIntegerField(blank=False)
    dry_weight = models.PositiveIntegerField(blank=False)
    harvest_metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    year = models.IntegerField(blank=False, null=False, default=datetime.utcnow().year)

    farm = models.ForeignKey(Farm, null=True, related_name='harvests', on_delete=models.CASCADE)
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
        unique_together = ['farm', 'year']



class Photo(models.Model):
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    photo = models.ImageField(upload_to='harvests')
    md5_hash = models.CharField(max_length=128, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    harvest = models.ForeignKey(Harvest, related_name='photos', null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering =['created_at']

    def __str__(self):
        return self.md5_hash
