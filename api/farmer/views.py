from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.utils._validate_url_param import validate_pk

from .models import Farmer, FarmerLocation
from .serializers import FarmerSerializer, FarmerLocationSerializer

class FarmerViewSet(viewsets.ViewSet):
    serializer_class = FarmerSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Farmer.objects.all()
    lookup_field = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request):
        queryset = self.queryset

        serializer = self.serializer_class(data=request.data, context={'request': request})
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Farmer Created',
                'farmer': serializer.data
            }

            return Response(response, status=status_code)

    def list(self, request):
        queryset = Farmer.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(farmer)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(farmer, data=request.data, context={'request': request}, partial=True)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()

            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Farmer Updated',
                'farmer': serializer.data
            }

            return Response(response, status=status_code)

    def destroy(self, request, pk=None):
        if not validate_pk(pk):
            return self.pk_error()

        queryset = self.queryset
        farmer = get_object_or_404(queryset, pk=pk)
        farmer.delete()
        return Response({"message": "Farmer deleted successfully"}, status=status.HTTP_202_ACCEPTED)

    def pk_error(self):
        return Response({"errors": [{"field": "url:farmer_id", "message": "Farmer ID should be integer"}]}, status=status.HTTP_400_BAD_REQUEST)
