from map.models import Shop
from rest_framework import serializers


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop                                                                        
        fields = ['id','name','city','address','longitude','latitude','open_hours']



