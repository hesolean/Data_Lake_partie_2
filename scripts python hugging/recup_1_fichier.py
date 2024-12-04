import requests
import os
from bs4 import BeautifulSoup
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from connexion_azure import connexion_azure

# Charger les variables d'environnement
load_dotenv()

# URL de la page où se trouve le fichier
url = "https://huggingface.co/datasets/Marqo/amazon-products-eval/tree/main/data"

# Envoyer une requête GET pour obtenir la page HTML
response = requests.get(url)
response.raise_for_status()  # Vérifie si la requête a réussi (200 OK)

# Analyser la page HTML avec BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Charger le premier fichier parquet trouvé
file_link = None
for a_tag in soup.find_all('a', href=True):
    if '.parquet' in a_tag['href']:
        file_link = a_tag['href']
        break

if file_link:
    # Si le lien est trouvé, télécharger le fichier
    file_url = file_link if file_link.startswith('http') else f"https://huggingface.co{file_link}"
    
    print(f"File URL : {file_url}")
    try:
        # Télécharger le fichier
        file_response = requests.get(file_url, stream=True)
        file_response.raise_for_status()  # Vérifie si la requête a réussi
        print(f"Fichier téléchargé : {file_response.raw}")

        local_file_path = f"./{os.path.basename(file_url)}"
        with open(local_file_path, "wb") as f:
            for chunk in file_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Fichier sauvegardé localement : {local_file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")

'''
SE CONNECTER SUR AZURE POUR CHARGER LE FICHIER DANS LE CONTENEUR
'''
# Informations sur le Service Principal 1 (pour accéder au Blob Storage)
tenant_id = os.getenv("TENANT_ID")
client_id_sp2 = os.getenv("CLIENT_ID_SP2")
client_secret_sp2 = os.getenv("CLIENT_SECRET_SP2")

# URL du Blob Storage et nom du conteneur
blob_storage_url = os.getenv("BLOB_STORAGE_URL")
container_name = os.getenv("CONTAINER_NAME")

# Informations sur le Service Principal 1 (récupérées via le secret)
client_id_sp1 = os.getenv("CLIENT_ID_SP1")
client_secret_sp1 = connexion_azure()

# Créer les credentials pour le Service Principal 1
sp1_credential = ClientSecretCredential(tenant_id, client_id_sp1, client_secret_sp1)

# Connexion au Blob Storage
blob_service_client = BlobServiceClient(account_url=blob_storage_url, credential=sp1_credential)

# Accéder au conteneur spécifique
container_client = blob_service_client.get_container_client(container_name)
        
'''
CHARGEMENT DES FICHIERS SUR AZURE
'''
try:
    # Récupérer le nom du fichier
    file_name = os.path.basename(file_url)

    # Créer un BlobClient pour gérer l'upload
    blob_client = container_client.get_blob_client(file_url)

    # Ouvrir le fichier local et l'uploader
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        
    print(f"Fichier {file_url} chargé sur azure")
except requests.exceptions.RequestException as e:
    print(f"Erreur lors du téléchargement du fichier : {e}")
