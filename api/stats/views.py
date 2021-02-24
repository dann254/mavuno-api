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

    def get_crop_yields(self):
        crops = Crop.objects.all()
        harvests = Harvest.objects.all()

        crop_harvests = {}
        year_harvests = {}

        for h in harvests:
            name = h.farm.crop.name
            year = h.year
            if name in crop_harvests:
                crop_harvests[name]['harvest_count'] += 1
                crop_harvests[name]['total_wet_weight'] += h.wet_weight
                crop_harvests[name]['total_dry_weight'] += h.dry_weight
            else:
                crop_harvests[name] = {}
                crop_harvests[name]['name'] = name
                crop_harvests[name]['harvest_count'] = 1
                crop_harvests[name]['total_wet_weight'] = h.wet_weight
                crop_harvests[name]['total_dry_weight'] = h.dry_weight

            if year in year_harvests:
                year_harvests[year]['harvest_count'] += 1
            else:
                year_harvests[year] = {}
                year_harvests[year]['year'] = year
                year_harvests[year]['harvest_count'] = 1


        for name, value in crop_harvests.items():
            wet_yield = 0
            dry_yield = 0



            wet_yield = crop_harvests[name]['total_wet_weight']/crop_harvests[name]['harvest_count']
            dry_yield = crop_harvests[name]['total_dry_weight']/crop_harvests[name]['harvest_count']

            crop_harvests[name]['avg_wet_yield'] = wet_yield
            crop_harvests[name]['avg_dry_yield'] = dry_yield

        return (crop_harvests, year_harvests)

    def generate_harvest_stats(self):
        harvests = Harvest.objects.all()

        total_harvests = harvests.count()

        h_crops = []

        for h in harvests:
            if h.farm.crop not in h_crops:
                h_crops.append(h.farm.crop)

        harvested_crops = len(h_crops)

        crop_harvests, year_harvests = self.get_crop_yields()

        response = {
            'total_harvests': total_harvests,
            'harvested_crops': harvested_crops,
            'crop_harvests': crop_harvests,
            'year_harvests': year_harvests
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
