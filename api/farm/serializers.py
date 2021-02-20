from rest_framework import serializers
from django.contrib.gis.geos import Point
from rest_framework_gis.serializers import GeoModelSerializer, GeometrySerializerMethodField

from .models import Farm, FarmLocation, Crop
from api.auth_user.serializers import UserInfoSerializer
from api.farmer.serializers import FarmerSerializer

class FarmLocationSerializer(GeoModelSerializer):
    address = serializers.CharField()
    country = serializers.CharField()
    administrative_area = serializers.CharField()

    class Meta:
        model = FarmLocation
        fields = ('point', 'address', 'country', 'administrative_area', 'location_metadata', )
        geo_field = "point"
        extra_kwargs = {'location_metadata': {'write_only': True}}

    def validate(self, data):
        farmer = self.context.get('farmer')
        if farmer:
            if data['administrative_area'] != farmer.location.administrative_area:
                raise serializers.ValidationError("Farm must be within the farmer's location")
        return data

class CropSerializer(serializers.ModelSerializer):
    created_by = UserInfoSerializer(read_only=True)
    class Meta:
        model = Crop
        fields = ('id', 'name', 'created_by')

    def create(self, validated_data):
        user = self.context['request'].user
        crop = Crop.objects.create(created_by=user, **validated_data)

        return crop


class FarmSerializer(serializers.ModelSerializer):
    location = FarmLocationSerializer()
    crop = CropSerializer(read_only=True)
    farmer = FarmerSerializer(read_only=True)
    created_by = UserInfoSerializer(read_only=True)
    class Meta:
        model = Farm
        fields = ('id', 'size', 'deed_number', 'location', 'crop', 'farmer', 'created_by',)

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        user = self.context['request'].user
        farmer = self.context['farmer']
        crop = self.context['crop']
        farm = Farm.objects.create(created_by=user, farmer=farmer, crop=crop, **validated_data)
        FarmLocation.objects.create(farm=farm, **location_data)
        return farm

    def update(self, instance, validated_data):
        location_data = validated_data.get('location')
        instance.size = validated_data.get('name', instance.size)
        instance.deed_number = validated_data.get('deed_number', instance.deed_number)
        crop = self.context['crop']
        instance.crop_id = crop.id
        instance.save()

        if location_data:
            instance.location.point = location_data.get('point', instance.location.point)
            instance.location.address = location_data.get('address', instance.location.address)
            instance.location.country = location_data.get('country', instance.location.country)
            instance.location.administrative_area = location_data.get('administrative_area', instance.location.administrative_area)
            instance.location.save()

        return instance
