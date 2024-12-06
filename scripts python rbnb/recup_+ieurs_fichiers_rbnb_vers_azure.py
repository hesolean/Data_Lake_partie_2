import json
import os
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import requests
from connexion_azure import connexion_azure
from bs4 import BeautifulSoup

# Charger la configuration existante depuis config.json (si elle existe)
try:
    with open("config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError:
    config = {}

'''
SE CONNECTER SUR AZURE POUR CHARGER LE FICHIER DANS LE CONTENEUR
'''
# Informations sur le Service Principal 1 (pour accéder au Blob Storage)
tenant_id = config["tenant_id"]
client_id_sp2 = config["client_id_sp2"]
client_secret_sp2 = config["client_secret_sp2"]

# URL du Blob Storage et nom du conteneur
blob_storage_url = config["blob_storage_url"]
container_name = config["container_name"]
local_file_path = config["local_file_path"]
blob_name = config["blob_name"]

# Informations sur le Service Principal 1 (récupérées via le secret)
client_id_sp1 = config["client_id_sp1"]
client_secret_sp1 = connexion_azure()

# Créer les credentials pour le Service Principal 1
sp1_credential = ClientSecretCredential(tenant_id, client_id_sp1, client_secret_sp1)

# Connexion au Blob Storage
blob_service_client = BlobServiceClient(account_url=blob_storage_url, credential=sp1_credential)

# Accéder au conteneur spécifique
container_client = blob_service_client.get_container_client(container_name)

'''
CHARGER DES FICHIERS RBNB
'''
# URL de la page où se trouve le fichier
url = "https://insideairbnb.com/get-the-data/"

# Envoyer une requête GET pour obtenir la page HTML
response = requests.get(url)
response.raise_for_status()  # Vérifie si la requête a réussi (200 OK)

# Analyser la page HTML avec BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Trouver les liens vers les fichiers Espagne
file_links = []

for h3_tag in soup.find_all('h3'):
    if 'Spain' in h3_tag.text:  # Vérifie si "Spain" est dans le texte de l'h3
        print(f"Texte trouvé : '{h3_tag.text.strip()}'")  # Affiche tout le texte des balises h3

        # Liste temporaire pour les fichiers associés à cet h3
        temp_file_links = []

        # Parcourir les balises suivantes
        for sibling in h3_tag.find_next_siblings():
            if sibling.name == 'h4':
                # Sauter les balises h4 entre h3 et la table
                continue
            elif sibling.name == 'table':
                # Vérifier qu'on est dans la table avant de chercher tous les a
                for a_tag in sibling.find_all('a', href=True):
                    # Vérifiez si le lien est un fichier CSV
                    if '.csv' in a_tag['href']:
                        temp_file_links.append(a_tag['href'])
                        print(f"Lien ajouté : {a_tag['href']} sous '{h3_tag.text.strip()}'")
                #break  # Arrêtez après avoir trouvé la table liée à cet h3

        # Ajouter les fichiers trouvés pour cet h3 à la liste principale
        file_links.extend(temp_file_links)

print("Liste finale des fichiers CSV collectés :", file_links)

'''
CHARGEMENT DES FICHIERS SUR AZURE
'''
for file in file_links:
    # Si le lien est trouvé, télécharger le fichier
    file_url = file if file.startswith('http') else f"https://insideairbnb.com{file}"

    try:
        # Télécharger le fichier
        file_response = requests.get(file_url, stream=True)
        file_response.raise_for_status()  # Vérifie si la requête a réussi
        file_name = os.path.basename(file_url)
        # Créer un BlobClient pour gérer l'upload
        blob_client = container_client.get_blob_client(file_url)

        try:
            # Ouvrir le fichier local et charger son contenu dans le Blob
            blob_client.upload_blob(file_response.raw, overwrite=True)  # overwrite=True pour écraser le blob si existe déjà
            print(f"Fichier {file_url} téléchargé avec succès vers le Blob.")
        except Exception as e:
            print(f"Erreur lors de l'upload du fichier : {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")
