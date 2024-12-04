import requests
from bs4 import BeautifulSoup

# URL de la page où se trouve le fichier
url = "https://insideairbnb.com/get-the-data/"

# Envoyer une requête GET pour obtenir la page HTML
response = requests.get(url)
response.raise_for_status()  # Vérifie si la requête a réussi (200 OK)

# Analyser la page HTML avec BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Trouver le lien vers le fichier spécifique reviews.csv
file_link = None
for a_tag in soup.find_all('a', href=True):
    if 'reviews.csv' in a_tag['href']:
        file_link = a_tag['href']
        break

if file_link:
    # Si le lien est trouvé, télécharger le fichier
    file_url = file_link if file_link.startswith('http') else f"https://insideairbnb.com{file_link}"
    
    # Spécifier où enregistrer le fichier
    output_file = "/home/helene/Documents/Brief Azure Data Lake 2/essai_Rbnb.csv"
    
    try:
        # Télécharger le fichier
        file_response = requests.get(file_url, stream=True)
        file_response.raise_for_status()  # Vérifie si la requête a réussi
        
        # Écrire le contenu du fichier téléchargé sur le disque
        with open(output_file, "wb") as file:
            for chunk in file_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Fichier téléchargé avec succès : {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")
else:
    print("Fichier spécifique non trouvé sur la page.")
