from rest_framework import serializers
from django.contrib.gis.geos import Point
from rest_framework_gis.serializers import GeoModelSerializer, GeometrySerializerMethodField

from .models import Farmer, FarmerLocation
from api.auth_user.serializers import UserInfoSerializer

class FarmerLocationSerializer(GeoModelSerializer):
    address = serializers.CharField()
    country = serializers.CharField()
    administrative_area = serializers.CharField()

    class Meta:
        model = FarmerLocation
        fields = ('point', 'address', 'country', 'administrative_area', 'location_metadata', )
        geo_field = "point"
        extra_kwargs = {'location_metadata': {'write_only': True}}


class FarmerSerializer(serializers.ModelSerializer):
    location = FarmerLocationSerializer()
    created_by = UserInfoSerializer(read_only=True)
    class Meta:
        model = Farmer
        fields = ('id', 'name', 'id_number', 'location', 'created_by', 'created_at', )

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        user = self.context['request'].user
        farmer = Farmer.objects.create(created_by=user, **validated_data)
        FarmerLocation.objects.create(farmer=farmer, **location_data)
        return farmer

    def update(self, instance, validated_data):
        location_data = validated_data.get('location')
        instance.name = validated_data.get('name', instance.name)
        instance.id_number = validated_data.get('id_number', instance.id_number)
        instance.save()

        if location_data:
            instance.location.point = location_data.get('point', instance.location.point)
            instance.location.address = location_data.get('address', instance.location.address)
            instance.location.country = location_data.get('country', instance.location.country)
            instance.location.administrative_area = location_data.get('administrative_area', instance.location.administrative_area)
            instance.location.save()

        return instance
