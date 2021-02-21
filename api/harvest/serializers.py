from rest_framework import serializers
from django.contrib.gis.geos import Point
from rest_framework_gis.serializers import GeoModelSerializer, GeometrySerializerMethodField
from PIL import Image
import hashlib

from .models import Harvest, Photo
from api.auth_user.serializers import UserInfoSerializer
from api.farm.serializers import FarmSerializer

class PhotoSerializer(serializers.ModelSerializer):
    created_by = UserInfoSerializer(read_only=True)
    class Meta:
        model = Photo
        fields = ('id', 'photo', 'md5_hash', 'created_by')

    def create(self, validated_data):
        user = self.context['request'].user
        photos = Photo.objects.create(created_by=user, **validated_data)

        return photos


class HarvestSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    farm = FarmSerializer(read_only=True)
    created_by = UserInfoSerializer(read_only=True)
    class Meta:
        model = Harvest
        fields = ('id', 'dry_weight', 'wet_weight', 'farm', 'photos', 'created_by',)

    def create(self, validated_data):
        photos_data = self.context['request'].FILES
        user = self.context['request'].user
        farm = self.context['farm']
        harvest = Harvest.objects.create(created_by=user, farm=farm, **validated_data)

        for key, value in photos_data.items():
            md5_hash = hashlib.md5(Image.open(value).tobytes())
            Photo.objects.create(created_by=user, harvest=harvest, photo=value, md5_hash= md5_hash.hexdigest())

        return harvest

    def update(self, instance, validated_data):
        instance.wet_weight = validated_data.get('wet_weight', instance.wet_weight)
        instance.dry_weight = validated_data.get('dry_weight', instance.dry_weight)
        instance.save()

        return instance

    def validate(self, data):
        dry = data.get('dry_weight')
        if dry:
            if data['wet_weight'] <= data['dry_weight']:
                raise serializers.ValidationError("Harvest dry weight should not be higher than wet weight")
        return data
