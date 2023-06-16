import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

###################### Création d'une liste pour les années ############################################
annees = []
for annee in range(2000, 2022):
    annees.append(annee)
print(annees)

###################### Création d'une liste pour les stations ############################################
# URL de la page web
url2 = "https://www.infoclimat.fr/stations-meteo/analyses-mensuelles.php"

# Envoyer une requête GET pour récupérer le contenu HTML de la page
response = requests.get(url2)
html_content = response.text

# Utiliser BeautifulSoup pour analyser le contenu HTML
soup2 = BeautifulSoup(html_content, "html.parser")

# Trouver la liste déroulante dans le HTML
dropdown = soup2.find("select", {"name": "staid"})

# Parcourir les options de la liste déroulante et extraire leur contenu
options = dropdown.find_all("option")
liste_station = []
for option in options:
    liste_station.append(option.text)


###################### Boucle pour interroger chaque année de chaque station ############################################

# Créer une liste pour stocker les DataFrames
df_list = []

for annee in annees :
    # URL de la page web contenant le tableau
    url = 'https://www.infoclimat.fr/climatologie/annee/{annee}/limoges-bellegarde/valeurs/07434.html'

    # Effectuer la requête HTTP et lire le contenu de la page
    response = urlopen(url)
    html_content = response.read()

    # Créer un objet BeautifulSoup à partir du contenu HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Trouver le tableau dans le contenu HTML
    soup.find("table", id="tableau-releves")

    # Extraire les en-têtes de colonne (balises <th>)
    table = soup.find("table", {"id": "tableau-releves"})
    if table is not None:
        header_cells = table.find_all("th")
        headers = [header.get_text() for header in header_cells[:14]]  # Sélection des éléments de 1 à 14
        print(headers)
    else:
        print("Aucun tableau avec l'ID spécifié n'a été trouvé.")

    # Extraire les données des cellules (balises <td>) dans chaque ligne
    data = []
    for row in table.find_all("tr"):
        row_data = []
        for cell in row.find_all("td"):
            for a in cell.find_all("a"):
                a.extract()  # Supprimer les balises <a>
            cell_data = cell.get_text(strip=True)
            row_data.append(cell_data)
        if row_data:  # Ignorer les lignes vides sans données
            data.append(row_data)
    # Créer le DataFrame Pandas
    df = pd.DataFrame(data, columns=headers)
    # Transposer le dataframe
    df_transposed = df.transpose()
    df_transposed.reset_index(drop=True, inplace=True)
    print(df_transposed)

    # Trouver la balise <div> avec un attribut id spécifique
    div_id = 'header-table-station'  # Remplacez par l'attribut id de la balise <div> souhaitée
    div_element = soup.find('div', id=div_id)

    # Trouver toutes les balises <li> de la page
    liste_contenu = []
    balises_li = div_element.find_all('li')
    balises_h1 = div_element.find_all('h1')

    # Parcourir chaque balise <li> et ajouter son contenu à la liste
    for balise_li in balises_li:
        #for a in cell.find_all("span"):
            #a.extract()  # Supprimer les balises <span>
        contenu = balise_li.get_text(strip=True).replace('Fuseau horaire', '')
        contenu = balise_li.get_text(strip=True).replace('Département ', '').replace('Altitude', '').replace('Coordonnées', '').replace('Début des archives', '').replace('Type de station', '')
        liste_contenu.append(contenu)

    # Parcourir chaque balise <h1> et ajouter son contenu à la liste
    for balise_h1 in balises_h1:
        #for a in cell.find_all("span"):
        contenu1 = balise_h1.get_text(strip=True).replace('Station météorologique de','')
        liste_contenu.append(contenu1)

    # Ajout de nouvelles colonnes au dataframe
    df_transposed['Département'] = liste_contenu[0]
    df_transposed['Altitude'] = liste_contenu[1]
    df_transposed['Coordonnées'] = liste_contenu[2]
    df_transposed['Début des archives'] = liste_contenu[3]
    df_transposed['Type de station'] = liste_contenu[5]
    df_transposed['Station'] = liste_contenu[6]

    df_transposed[['Nom station','Num station']] = df_transposed['Station'].str.split(':',expand=True)
    df_transposed.drop('Station', axis=1, inplace=True)
    # Ajouter le DataFrame à la liste
    df_list.append(df_transposed)
    # Ajouter le délai de 1 seconde entre chaque itération de la boucle
    time.sleep(20)

# Concaténer les DataFrames en un seul DataFrame final
df_concatenated = pd.concat(df_list, ignore_index=True)

# Afficher le DataFrame final
print(df_concatenated)

