from bs4 import BeautifulSoup

import requests
import re 

# Show shops and addresses


url = "https://www.promoceny.pl/sklepy/"

result = requests.get(url)

doc = BeautifulSoup(result.text, "html.parser")

tag = doc.find_all('ul', class_="col-md-4")


dict = {}	#  Dict name_of_the_shop = key, link = value
dict_name_of_shops = {}	#  Dict number = key, name_of_the_shop = value
dict_name_of_shops['default'] = 'Choose your shop'

key = 0

# Create dict from id and name of the shop

for i in tag:
	for a in i.find_all('a', href=True):
		name = a.find("strong")

		if name == None:	
			span = a.find("span")
			# print(span.text)
			dict[span.text] = a['href']
			dict_name_of_shops[key] = span.text

		else:				
			# print(name.text)
			dict[name.text] = a['href']
			dict_name_of_shops[key] = name.text

		key += 1

		
del dict_name_of_shops[2] 
list_of_shops_in_dict = dict_name_of_shops


def main(shop_number):
	def scraping(url):

		# From table on web

		result = requests.get(url)
		doc = BeautifulSoup(result.text, "html.parser")

		text = ""

		for row in doc.find_all('tr'):
			text += row.text
			


		text = re.sub(' +', '', text)	# Del white spaces

		tabela = text.split()	


		del tabela[:7]	# Delete table headers


		# Delete wrong table records

		do_usuniecia = []
		do_dodania = []
		do_dodania2 = []

		def has_numbers(inputString):
			return any(char.isdigit() for char in inputString)

		for i in tabela:	
			if "Piotrkowska252/256," == i:
				index = tabela.index(i)
				do_usuniecia.append(i)
				string = "Piotrkowska252/256," + tabela[index+1]
				tabela[index+1] = string

			if "Niedziela" in i or "niedziela" in i:
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

			if "tel" in i and has_numbers(i):
				do_usuniecia.append(i)
				
			if "tel." in i:
				do_usuniecia.append(i)

			if i.isnumeric():
				do_usuniecia.append(i)



		for i in do_dodania2:
			if "Tel" in i and has_numbers(i):
				do_dodania2.remove(i)
			if "tel" in i and has_numbers(i):
				do_dodania2.remove(i)


		for i in do_usuniecia:
			if "(" in i and "," not in i:
				do_usuniecia.remove(i)

			if "tel" in i and has_numbers(i):
				do_usuniecia.remove(i)

			if i.isnumeric():
				do_usuniecia.remove(i)


		for i in do_usuniecia:
			tabela.remove(i)
			

		data = []

		tabela = list(dict.fromkeys(tabela))
		

		# Format output of shop information

		for i in tabela:
			index = tabela.index(i)

			i = i.split(",")

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


			# To debug 
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

	
	selected_shop = dict[dict_name_of_shops[int(shop_number)]]	# Search link to selected shop


	url = "https://www.promoceny.pl"

	url = url + selected_shop + "p/1"



	# Check how many pages of shop available

	result = requests.get(url)
	doc = BeautifulSoup(result.text, "html.parser")

	number_of_sites = doc.find_all('ul', class_="pagination")

	strony = ""
	lista = []


	for i in number_of_sites:
		strony += i.text

	lista_sklepow = []


	# Create list of available shops 
	# Show page info

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


		print(zakres)
		print()

		# Range from first page and last
		for i in range(zakres[0],zakres[-1]+1):  
			replacementStr = str(i)

			if i < 10:	# Create urls for pages
				url = url[:-1] + replacementStr
			elif i == 10:
				url = url[:-2] + "/" + replacementStr
			elif i > 100:
				url = url[:-4] + "/" + replacementStr
			else: 
				url = url[:-3] + "/" + replacementStr

			print(url)
			lista_sklepow.extend(scraping(url))	# All addresses from page


		print()
		
	return lista_sklepow 	


