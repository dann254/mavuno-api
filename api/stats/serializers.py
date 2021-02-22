from rest_framework import serializers

from api.harvest.models import Harvest
from api.farmer.models import Farmer
from api.farm.models import Farm


class HarvestStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = ('total_harvests', 'harvested_crops', 'crop_yields', 'crop_harvests')
