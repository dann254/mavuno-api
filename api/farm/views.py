from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from annoying.functions import get_object_or_None
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.utils._validate_url_param import validate_pk

from .models import Farm, FarmLocation, Crop
from .serializers import FarmSerializer, FarmLocationSerializer, CropSerializer
from api.farmer.models import Farmer

class FarmViewSet(viewsets.ViewSet):
    serializer_class = FarmSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Farm.objects.all()
    lookup_field = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, farmer_pk=None):
        queryset = self.queryset

        farmer = get_object_or_None(Farmer, id=farmer_pk)
        if not farmer:
            return Response({"errors": [{"field": "url: farmer_id", "message": "Farmer not found"}]}, status=status.HTTP_404_NOT_FOUND)

        crop_name = request.data.get('crop')

        crop = get_object_or_None(Crop, name__iexact=crop_name)

        #create new crop
        if not crop:
            crop_serializer = CropSerializer(data={'name': crop_name}, context={'request': request})
            crop_valid = crop_serializer.is_valid(raise_exception=True)

            if crop_valid:
                crop_serializer.save()
                crop = crop_serializer.data

        serializer = self.serializer_class(data=request.data, context={'request': request, 'farmer': farmer, 'crop': crop})
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Farm Created',
                'farm': serializer.data
            }

            return Response(response, status=status_code)

    def list(self, request, farmer_pk=None):
        queryset = self.queryset
        farms = queryset.filter(farmer_id=farmer_pk)
        serializer = self.serializer_class(farms, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None, farmer_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk, farmer_id=farmer_pk)
        serializer = self.serializer_class(farmer)
        return Response(serializer.data)

    def partial_update(self, request, pk=None, farmer_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset

        crop_name = request.data.get('crop')

        crop = get_object_or_None(Crop, name__iexact=crop_name)

        #create new crop
        if not crop:
            crop_serializer = CropSerializer(data={'name': crop_name}, context={'request': request})
            crop_valid = crop_serializer.is_valid(raise_exception=True)

            if crop_valid:
                crop_serializer.save()
                crop = crop_serializer.data

        farm = get_object_or_404(queryset, pk=pk, farmer_id=farmer_pk)
        serializer = self.serializer_class(farm, data=request.data, context={'request': request, 'crop': crop}, partial=True)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Farm Updated',
                'farmer': serializer.data
            }

            return Response(response, status=status_code)

    def destroy(self, request, pk=None, farmer_pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk, farmer_id=farmer_pk)
        farmer.delete()
        return Response({"message": "Farm deleted successfully"}, status=status.HTTP_202_ACCEPTED)

    def pk_error(self):
        return Response({"errors": [{"field": "url:farmer_id", "message": "Farmer ID should be integer"}]}, status=status.HTTP_400_BAD_REQUEST)
