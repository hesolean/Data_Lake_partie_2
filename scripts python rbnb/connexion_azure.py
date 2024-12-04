import json
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

def connexion_azure():
    # Charger la configuration existante depuis config.json (si elle existe)
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {}

    # Vérifier si les clés nécessaires sont présentes
    required_keys = ["tenant_id", "client_id_sp2", "client_secret_sp2", "key_vault_url", "secret_name", "blob_storage_url", "container_name"]

    for key in required_keys:
        if key not in config:
            print(f"Clé manquante dans le fichier config.json : {key}")
            exit()

    # Informations sur le Service Principal 2 (pour accéder au Key Vault)
    tenant_id = config["tenant_id"]
    client_id_sp2 = config["client_id_sp2"]
    client_secret_sp2 = config["client_secret_sp2"]

    # URL du Key Vault et nom du secret
    key_vault_url = config["key_vault_url"]
    secret_name = config["secret_name"]

    # Créer les credentials pour le Service Principal 2
    sp2_credential = ClientSecretCredential(tenant_id, client_id_sp2, client_secret_sp2)

    # Connexion au Key Vault
    key_vault_client = SecretClient(vault_url=key_vault_url, credential=sp2_credential)

    # Récupérer le secret contenant le mot de passe de Service Principal 1
    try:
        secret = key_vault_client.get_secret(secret_name)
        sp1_password = secret.value
        print("Mot de passe récupéré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la récupération du secret : {e}")
        exit()
    
    return sp1_password
