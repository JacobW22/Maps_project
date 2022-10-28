from django.shortcuts import render
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from folium.plugins import MarkerCluster, LocateControl
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import folium
import re 

from map import python_soup_fully 
from map.models import Shop
from map.python_soup_fully import list_of_shops_in_dict
from map.serializers import ShopSerializer


class ShoplistAPIView(generics.ListAPIView):
    """

    Get all the shops

    Shows all shops in the project database, 50 shops per page

    """

    queryset = Shop.objects.all().order_by('city')

    def list(self, request):
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
    
    unknown_to_html = []
    list_of_cities = []

    dict_from_other_file = list_of_shops_in_dict
    empty_list = ""
    number_of_shops = 0
    number_of_shops_in_city = 0
    select_value = 'default'
    select_value_city = 'Choose your shop'
    unknown_quantity = 0
  


    if request.method == "POST": 

        # React to selected option and add markers to map

        if request.POST.get('select_city'):

            select_value_city = request.POST.get('select_city') 
            shop_list = Shop.objects.filter(city = select_value_city).order_by('city')
            number_of_shops_in_city = shop_list.count()

            for one_shop in shop_list:
                    if one_shop.city == "empty":
                        empty_list = "Brak sklepów stacjonarnych"

                    elif one_shop.longitude == 0 and one_shop.latitude == 0:
                        information_about_address =  one_shop.address + ", " + one_shop.city + ", " + one_shop.name
                        unknown_to_html.append(information_about_address) 

                    else:
                        info = "<center>" + one_shop.address + "<br><br>" + "<div style='width: 100%; height: 20px; border-top: 1px solid black; border-bottom: 1px solid black; text-align: center'>" + one_shop.name + "</div>" + "<div style='width: 100%; height: 20px; border-bottom: 1px solid black; text-align: center'>" + one_shop.city + "</div><br>" + one_shop.open_hours + "</center>"
                        
                        folium.Marker(
                            [one_shop.latitude,one_shop.longitude], 
                            tooltip = one_shop.name, 
                            popup = info,
                            icon = folium.Icon(icon="fa-shopping-cart", prefix="fa")
                            ).add_to(mCluster2)
        mCluster2.add_to(m)


        # React to selected option and add markers to map

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

                    elif one_shop.longitude == 0 and one_shop.latitude == 0:
                        information_about_address =  one_shop.address + ", " + one_shop.city + ", " + one_shop.name
                        unknown_to_html.append(information_about_address) 

                    else:
                        info = "<center>" + one_shop.address + "<br><br>" + "<div style='width: 100%; height: 20px; border-top: 1px solid black; border-bottom: 1px solid black; text-align: center'>" + one_shop.name + "</div><br>" + one_shop.open_hours + "</center>"
                        
                        folium.Marker(
                            [one_shop.latitude,one_shop.longitude], 
                            tooltip = one_shop.city, 
                            popup = info,
                            icon = folium.Icon(icon="fa-shopping-cart", prefix="fa")
                            ).add_to(mCluster)
            mCluster.add_to(m)
            

        
        #  Sending data from scraping to database 

        if request.POST['submit'] == 'reset':

            Shop.objects.all().delete()
            
            # for i in range(16,20):
            for i in range(0, len(dict_from_other_file)):
                if i == 2:
                    pass
                else:
                    lista_z_pliku = python_soup_fully.main(i)
                                
                    if lista_z_pliku[0] == "Nie znaleziono adresów":
                            data = Shop(name=lista_z_pliku[1], city = "empty", latitude=0, longitude=0)
                            data.save()
                    else:        
                        for i in lista_z_pliku:
                            print("Loading data...")
                            locator = Nominatim(user_agent="myGeocoder")

                            location = locator.geocode(i[0]+", Polska", timeout = 10)
                        
                    
                            if location is not None:
                                try:
                                    description = i[1].replace(",","<br>")
                                    data = Shop(name=i[-1], city=i[-2], address=i[0], latitude=location.latitude, longitude=location.longitude,open_hours=description)
                                    data.save()

                                except GeocoderTimedOut as e:
                                    print(e)
                            else: 
                                data = Shop(name=i[-1], address=i[0], open_hours=description, city=i[-2], longitude = 0, latitude = 0)
                                data.save()       
        

    # Write non-included addresses to file


    f = open("static/nie_znalezione_adresy.txt", "w")

    f.write("Nieznalezione adresy: \n")

    unknown_quantity = len(unknown_to_html)
        

    for i in unknown_to_html:
        f.write("-> " + i + "\n")   

    f.close()


    # Search shops to second select options

    shop_list = Shop.objects.values_list('city',flat=True).distinct().order_by('city')

    name_of_shops = dict_from_other_file.values()

    list_of_cities.append("Choose your city")

    def has_numbers(inputString):
            return any(char.isdigit() for char in inputString)

    for city in shop_list:
        if city != "empty" and has_numbers(city) != True and city:
                list_of_cities.append((city).replace(',',''))   
                if city in name_of_shops:
                    list_of_cities.remove(city)


    list_of_cities = list(dict.fromkeys(list_of_cities))
    

    # Send to template
    
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
        'unknown_to_html' : unknown_to_html,
        'number_of_shops' : number_of_shops,
        'number_of_shops_in_city' : number_of_shops_in_city,
        'select_value' : select_value,
        'select_value_city' : select_value_city,
        'unknown_quantity' : unknown_quantity,
        'list_of_cities' : list_of_cities,
    }



    return render(request, 'index.html', context)