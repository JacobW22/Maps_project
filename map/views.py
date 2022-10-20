from django.shortcuts import render,HttpResponseRedirect
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from folium.plugins import MarkerCluster, LocateControl
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import folium
import requests
import re 

from map import python_soup_fully 
from map.models import Shop
from map.python_soup_fully import list_of_shops_in_dict
from map.serializers import ShopSerializer

# Create your views here.        

class ShoplistAPIView(generics.ListAPIView):
    """

    Get all the shops

    Shows all shops in the project database, 50 shops per page

    """
    queryset = Shop.objects.all().order_by('city')
    serializer_class = ShopSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ShopSerializer(queryset, many=True)
        return Response(serializer.data)



class ShopFinderAPIView(APIView):
    """

    Get chosen shops

    Only one parameter is required to work, shows shop details

    """

    city = openapi.Parameter(
        'city', 
        openapi.IN_QUERY, 
        type=openapi.TYPE_STRING,
        required=False,
        description="Name of the city, starts with capital letter, no spaces e.g. 'BielanyWrocławskie'"
    )

    name = openapi.Parameter(
        'name', 
        openapi.IN_QUERY, 
        type=openapi.TYPE_STRING, 
        required=False,
        description="Name of the shop, starts with capital letter, no spaces e.g. 'MediaExpert'"

    )

    @swagger_auto_schema(manual_parameters=[city,name])


    def get(self, request):
        if 'city' in request.GET and 'name' in request.GET:

            param = request.GET.get('city')
            param2 = request.GET.get('name')
            
            Shops = Shop.objects.filter(city=param, name=param2)

            if not Shops:
                raise Http404

            location_serializer = ShopSerializer(Shops, many=True)

            return Response({
                    'Shops': location_serializer.data
                })


        elif 'city' in request.GET:

            param = request.GET.get('city')

            Shops = Shop.objects.filter(city=param)

            if not Shops:
                raise Http404

            location_serializer = ShopSerializer(Shops, many=True)

            return Response({
                    'Shops': location_serializer.data
                })
        

        elif 'name' in request.GET: 

            param = request.GET.get('name')
            Shops = Shop.objects.filter(name=param)

            if not Shops:
                raise Http404

            location_serializer = ShopSerializer(Shops, many=True)

            return Response({
                'Shops': location_serializer.data
            })

        else:

            raise Http404

def AboutApp(request):
    return render(request, 'AboutApp.html')



def index(request):

    m = folium.Map(location=[52,19],zoom_start=5.2)
    mCluster = MarkerCluster(name="Selected shop")
    mCluster2 = MarkerCluster(name="Selected city")
    
    latitude = []
    longtitude = []
    nie_znalezione = []
    nie_znalezione_do_html = []
    markers_location = []
    list_of_cities = []

    dict_from_other_file = list_of_shops_in_dict
    empty_list = ""
    number_of_shops = 0
    number_of_shops_in_city = 0
    select_value = 'default'
    select_value_city = 'Choose your shop'
    ilosc_nieznalezionych = 0
  


    if request.method == "POST": 

        if request.POST.get('select_city'):

            select_value_city = request.POST.get('select_city') 
            shop_list = Shop.objects.filter(city = select_value_city).order_by('city')
            number_of_shops_in_city = shop_list.count()

            for one_shop in shop_list:
                    if one_shop.city == "empty":
                        empty_list = "Brak sklepów stacjonarnych"

                    elif one_shop.open_hours == "cant_find":
                        information_about_address =  one_shop.address + ", " + one_shop.city + ", " + one_shop.name
                        nie_znalezione_do_html.append(information_about_address) 


                    else:
                        info = "<center>" + one_shop.address + "<br><br>" + "<div style='width: 100%; height: 20px; border-top: 1px solid black; border-bottom: 1px solid black; text-align: center'>" + one_shop.name + "</div>" + "<div style='width: 100%; height: 20px; border-bottom: 1px solid black; text-align: center'>" + one_shop.city + "</div><br>" + one_shop.open_hours + "</center>"
                        
                        folium.Marker(
                            [one_shop.latitude,one_shop.longitude], 
                            tooltip = one_shop.name, 
                            popup = info,
                            icon = folium.Icon(icon="fa-shopping-cart", prefix="fa")
                            ).add_to(mCluster2)
        mCluster2.add_to(m)


        if request.POST.get('select_shop'):

            select_value = request.POST.get('select_shop') 


            if select_value == 'default':
                pass
            else:
                name_of_the_shop = dict_from_other_file[int(select_value)]
                name_of_the_shop = re.sub(' +', '', name_of_the_shop)


                shop_list = Shop.objects.filter(name = name_of_the_shop.strip()).order_by('city')
                number_of_shops = shop_list.count()
                
                for one_shop in shop_list:
                    if one_shop.city == "empty":
                        empty_list = "Brak sklepów stacjonarnych"

                    elif one_shop.open_hours == "cant_find":
                        information_about_address =  one_shop.address + ", " + one_shop.city + ", " + one_shop.name
                        nie_znalezione_do_html.append(information_about_address) 


                    else:
                        info = "<center>" + one_shop.address + "<br><br>" + "<div style='width: 100%; height: 20px; border-top: 1px solid black; border-bottom: 1px solid black; text-align: center'>" + one_shop.name + "</div><br>" + one_shop.open_hours + "</center>"
                        
                        folium.Marker(
                            [one_shop.latitude,one_shop.longitude], 
                            tooltip = one_shop.city, 
                            popup = info,
                            icon = folium.Icon(icon="fa-shopping-cart", prefix="fa")
                            ).add_to(mCluster)
            mCluster.add_to(m)
            

        
        
        if request.POST['submit'] == 'reset':


            Shop.objects.all().delete()
            
            for i in range(10,11):
            # for i in range(0, len(dict_from_other_file)):

                lista_z_pliku = python_soup_fully.main(i)
            
                # Create Map Object and representation in HTML
            
                if lista_z_pliku[0] == "Nie znaleziono adresów":
                        data = Shop(name=lista_z_pliku[1], city = "empty", latitude=0, longitude=0)
                        data.save()
                else:        
                    for i in lista_z_pliku:
                        print("Loading data...")
                        locator = Nominatim(user_agent="myGeocoder")

                        location = locator.geocode(i[0], timeout = 10)
                    
                
                        if location is not None:
                            try:
                                latitude.append(location.latitude)
                                longtitude.append(location.longitude)
                                
                                description = i[1].replace(",","<br>")
                                data = Shop(name=i[-1], city=i[-2], address=i[0], latitude=location.latitude, longitude=location.longitude,open_hours=description)
                                data.save()

                            except GeocoderTimedOut as e:
                                nie_znalezione.append(i[0])
                                print("nie znalazłem",len(nie_znalezione), nie_znalezione)
                        else: 
                            nie_znalezione.append(i[0])
                            data = Shop(name=i[-1], address=i[0], open_hours="cant_find", city=i[-2], longitude = 0, latitude = 0)
                            data.save()
            
            data = Shop(name="Nie znalezione sklepy ogółem", address=len(nie_znalezione), city="empty", longitude=0, latitude=0)
            data.save()
                        
        

    # get from database

    f = open("static/nie_znalezione_adresy.txt", "w")

    f.write("Nieznalezione adresy: \n")

    ilosc_nieznalezionych = len(nie_znalezione_do_html)

    for i in nie_znalezione_do_html:
        f.write("-> " + i + "\n")

    f.close()


    shop_list = Shop.objects.filter().all()

    list_of_cities.append("Choose your city")

    for i in shop_list:
        if i.city != '' or i.city != 'empty':
            list_of_cities.append(i.city)

    list_of_cities = list(dict.fromkeys(list_of_cities))

    

    # for lat, lng, name in zip(latitude, longtitude, name):
    #     feature_group.add_child(folium.Marker(location=[lat,lng], tooltip="Click for more", popup=name))

   
    

    
    dict_of_shops = list_of_shops_in_dict.items()

    if select_value != 'default':
        select_value = int(select_value)


    folium.LayerControl(collapsed=False).add_to(m)
    LocateControl().add_to(m)

    m = m._repr_html_()
    
    context = {
        'm' : m,
        'dict_of_shops' : dict_of_shops,
        'empty_list' : empty_list,
        'nie_znalezione_do_html' : nie_znalezione_do_html,
        'number_of_shops' : number_of_shops,
        'number_of_shops_in_city' : number_of_shops_in_city,
        'select_value' : select_value,
        'select_value_city' : select_value_city,
        'ilosc_nieznalezionych' : ilosc_nieznalezionych,
        'list_of_cities' : list_of_cities,
    }



    return render(request, 'index.html', context)