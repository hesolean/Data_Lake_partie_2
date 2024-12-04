import json
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Charger la configuration existante depuis config.json (si elle existe)
try:
    with open("config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError:
    config = {}

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
client_secret_sp1 = config["client_secret_sp1"]

# Créer les credentials pour le Service Principal 1
sp1_credential = ClientSecretCredential(tenant_id, client_id_sp1, client_secret_sp1)

# Connexion au Blob Storage
blob_service_client = BlobServiceClient(account_url=blob_storage_url, credential=sp1_credential)

# Accéder au conteneur spécifique
container_client = blob_service_client.get_container_client(container_name)

# Créer un BlobClient pour gérer l'upload
blob_client = container_client.get_blob_client(blob_name)

try:
    # Ouvrir le fichier local et charger son contenu dans le Blob
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)  # overwrite=True pour écraser le blob si existe déjà
    print(f"Fichier {local_file_path} téléchargé avec succès vers le Blob {blob_name}.")
except Exception as e:
    print(f"Erreur lors de l'upload du fichier : {e}")

# Supprime le mot de passe dans config.json
config["client_secret_sp1"] = ""
with open("config.json", "w") as file:
    json.dump(config, file, indent=4)