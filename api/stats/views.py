from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.utils._permissions import IsSupervisor

from api.harvest.models import Harvest
from api.farmer.models import Farmer
from api.farm.models import Farm, Crop


class StatsView(views.APIView):
    permission_classes = (IsAuthenticated, IsSupervisor)


    def generate_harvest_stats(self):
        harvests = Harvest.objects.all()

        total_harvests = harvests.count()

        h_crops = []

        for h in harvests:
            if h.farm.crop not in h_crops:
                h_crops.append(h.farm.crop)

        harvested_crops = len(h_crops)



        response = {
            'total_harvests': total_harvests,
            'harvested_crops': harvested_crops
        }
        return response

    def generate_farm_stats(self):
        farms = Farm.objects.all()

        total_farms = farms.count()

        response = {
            'total_farms': total_farms
        }
        return response

    def generate_farmer_stats(self):
        farmers = Farmer.objects.all()

        total_farmers = farmers.count()
        response = {
            'total_farmers': total_farmers
        }
        return response

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        stats = {
            'harvest_stats': self.generate_harvest_stats(),
            'farm_stats': self.generate_farm_stats(),
            'farmer_stats': self.generate_farmer_stats(),
        }
        return Response(stats)
