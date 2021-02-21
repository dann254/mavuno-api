from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from annoying.functions import get_object_or_None
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.utils._validate_url_param import validate_pk
from PIL import Image
import hashlib
from datetime import datetime

from .models import Harvest, Photo
from .serializers import HarvestSerializer, PhotoSerializer
from api.farm.models import Farm
from api.farmer.models import Farmer

class HarvestViewSet(viewsets.ViewSet):
    serializer_class = HarvestSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Harvest.objects.all()
    lookup_field = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, farmer_pk=None, farm_pk=None):
        queryset = self.queryset

        data = request.data

        first_photo = request.data.get('photo_1')
        second_photo = request.data.get('photo_2')
        third_photo = request.data.get('photo_3')

        farm = get_object_or_None(Farm, id=farm_pk, farmer_id=farmer_pk)
        if not farm:
            return Response({"errors": [{"field": "url: farm_id", "message": "Farmer not found"}]}, status=status.HTTP_404_NOT_FOUND)

        if not first_photo or not second_photo or not third_photo:
            return Response({"errors": [{"field": "photo", "message": "You must submit 3 photos"}]}, status=status.HTTP_400_BAD_REQUEST)

        hash_list = []
        for key, value in request.FILES.items():
            md5_hash = hashlib.md5(Image.open(value).tobytes())
            pic = get_object_or_None(Photo, md5_hash = md5_hash.hexdigest())

            if md5_hash.hexdigest() not in hash_list and not pic:
                hash_list.append(md5_hash.hexdigest())
            else:
                return Response({"errors": [{"field": "photo", "message": "Uploded photos must be unique"}]}, status=status.HTTP_400_BAD_REQUEST)

        harvest = get_object_or_None(Harvest, farm_id = farm_pk, year = datetime.utcnow().year)
        if harvest:
            return Response({"message": "Farm already has a harvest record for this year"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data, context={'request': request, 'farm': farm})
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Harvest Created',
                'harvest': serializer.data
            }

            return Response(response, status=status_code)

    def list(self, request, farmer_pk=None, farm_pk=None):
        queryset = self.queryset
        harvests = queryset.filter(farm_id = farm_pk, farm__farmer_id=farmer_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None, farmer_pk=None, farm_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk, farm_id = farm_pk, farm__farmer_id=farmer_pk)
        serializer = self.serializer_class(farmer)
        return Response(serializer.data)

    def partial_update(self, request, pk=None, farmer_pk=None, farm_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset


        harvest = get_object_or_404(queryset, pk=pk, farm_id = farm_pk, farm__farmer_id=farmer_pk)
        serializer = self.serializer_class(harvest, data=request.data, context={'request': request}, partial=True)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Harvest Updated',
                'farmer': serializer.data
            }

            return Response(response, status=status_code)

    def destroy(self, request, pk=None, farmer_pk=None, farm_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk, farm_id = farm_pk, farm__farmer_id=farmer_pk)
        farmer.delete()
        return Response({"message": "Harvest deleted"}, status=status.HTTP_202_ACCEPTED)

    def pk_error(self):
        return Response({"errors": [{"field": "url:farmer_id", "message": "Farmer ID should be integer"}]}, status=status.HTTP_400_BAD_REQUEST)
