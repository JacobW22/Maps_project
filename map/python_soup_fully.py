from bs4 import BeautifulSoup

import requests
import re 
import unidecode

# Wyswietl wszystkie sklepy oraz ich adresy


url = "https://www.promoceny.pl/sklepy/"


result = requests.get(url)


doc = BeautifulSoup(result.text, "html.parser")


tag = doc.find_all('ul', class_="col-md-4")


dict = {}	# Słownik nazwa_sklepu = klucz, link = wartość
dict_name_of_shops = {}	# Słownik number = klucz, nazwa_sklepu = wartość
dict_name_of_shops['default'] = 'Choose your shop'


key = 0

# Stwórz słownik zawierający numer i nazwę sklepu

for i in tag:
	for a in i.find_all('a', href=True):
		name = a.find("strong")

		if name == None:	# wyszukaj nazwę sklepu w przypadku tagu span
			span = a.find("span")
			# print(span.text)
			dict[span.text] = a['href']
			dict_name_of_shops[key] = span.text


		else:				# wyszukaj nazwę sklepu w przypadku tagu strong
			# print(name.text)
			dict[name.text] = a['href']
			dict_name_of_shops[key] = name.text

		key += 1

		

# Wybierz sklep

del dict_name_of_shops[2]
list_of_shops_in_dict = dict_name_of_shops


def main(shop_number):
	def scraping(url):

		# Wybierz rekordy z tabeli umieszczonej na stronie

		result = requests.get(url)
		doc = BeautifulSoup(result.text, "html.parser")

		shops = doc.find_all('tr')

		text = ""

		for row in doc.find_all('tr'):
			text += row.text
			


		text = re.sub(' +', '', text)	# Usuń białe znaki

		tabela = text.split()	# Umieść tekst w liście


		del tabela[:7]	# Usun nagłówki tabeli


		# Usuń niepotrzebne rekordy

		do_usuniecia = []
		do_dodania = []
		do_dodania2 = []


		for i in tabela:	
			if "Niedziela" in i:
				do_dodania.append(i)
				do_usuniecia.append(i)

			if "," not in i:
				do_usuniecia.append(i)
				do_dodania2.append(i)
			
			if "," == i[0]:
				do_usuniecia.append(i)
				do_dodania2.append(i)
			
			if "(" in i:
				do_usuniecia.append(i)

			if "tel" in i:
				do_usuniecia.append(i)
				
			if "tel." in i:
				do_usuniecia.append(i)


		for i in do_dodania2:
			if "Tel" in i:
				do_dodania2.remove(i)
			if "tel" in i:
				do_dodania2.remove(i)


		for i in do_usuniecia:
			if "(" in i and "," not in i:
				do_usuniecia.remove(i)

			if "tel" in i:
				do_usuniecia.remove(i)



		for i in do_usuniecia:
			tabela.remove(i)
			


		location = []
		data = []
		iteration = 0
		iteration2 = 0
		sum_of_upper = 0
		new_string = ""

		tabela = list(dict.fromkeys(tabela))
		
		for i in tabela:
			index = tabela.index(i)


			i = i.split(",")

			# i[0] = unidecode.unidecode(i[0])
			i[0] = i[0].replace("Zwirkii","Zwirki i")
			i[0] = i[0].replace("Nikodemai", "Nikodema i")
			i[0] = i[0].replace("-", " ")

			if "III" not in i[0]:
				i[0] = (re.sub(r"(\w)([A-ZĄĆĘŁŃÓŚŹŻ])", r"\1 \2",i[0]))	# Space before capital letter	
			else:
				i[0] = i[0].replace("III"," III ")	

			i[0] = (re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", i[0]).strip()  + "," + i[1]) # Add space before number appears
			i[0] = re.sub(r'(?<=[.,])(?=[^\s])', r' ', i[0])


			i.remove(i[1])
			if len(i) > 1:
				i.remove(i[1])


			# print(len(do_dodania2))
			# print(do_dodania2[index])
			# print(i, index)

			i.append(do_dodania[index])
			
	

			if (index+1) < len(do_dodania2):
				i.append(do_dodania2[0::2][index])
				i.append(do_dodania2[1])

			else:
				i.append(do_dodania2[index])
			
			
			data.append(i)

		return data

	
	selected_shop = dict[dict_name_of_shops[int(shop_number)]]	# wyszukaj link do wybranego sklepu


	url = "https://www.promoceny.pl"

	url = url + selected_shop + "p/1"



	# sprawdz ilosc stron ze sklepami



	result = requests.get(url)
	doc = BeautifulSoup(result.text, "html.parser")


	number_of_sites = doc.find_all('ul', class_="pagination")


	strony = ""
	lista = []


	for i in number_of_sites:
		strony += i.text

	lista_sklepow = []


	# Utwórz zakres pętli w oparciu o ilość dostępnych stron

	if strony == "":
		print(url)
		lista = scraping(url)

		if lista != []:
			lista_sklepow.extend(lista)
		else:
			lista_sklepow.append("Nie znaleziono adresów")
			lista_sklepow.append(dict_name_of_shops[int(shop_number)])
	else:
		strony = re.sub(' +', '', strony)
		lista = strony.split()
		elem = [ lista[0], lista[-1] ] 
		elem[0] = elem[0].replace("(obecnie)", "")

		zakres = [ int(x) for x in elem ]



	# wyswietl adresy sklepow


		print(zakres)
		print()


		for i in range(zakres[0],zakres[-1]+1):	# Wybierz pierwsza i ostatnią stronę jako zakres
			replacementStr = str(i)

			if i < 10:	# Utwórz linki dla dostępnych stron
				url = url[:-1] + replacementStr
			elif i == 10:
				url = url[:-2] + "/" + replacementStr
			elif i > 100:
				url = url[:-4] + "/" + replacementStr
			else: 
				url = url[:-3] + "/" + replacementStr

			print(url)
			lista_sklepow.extend(scraping(url))	# Dodaj adresy sklepów z obecnej strony


		print()
	return lista_sklepow 	# Wyświetl wszystkie adresy sklepu


