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
        # Ajouter ou mettre à jour le mot de passe de SP1 dans le fichier de configuration
        config["client_secret_sp1"] = sp1_password

        # Sauvegarder les informations de configuration dans config.json
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4)

        print("Le mot de passe du Service Principal 1 a été enregistré dans config.json.")
    except Exception as e:
        print(f"Erreur lors de la récupération du secret : {e}")
        exit()

    # Informations sur le Service Principal 1 (récupérées via le secret)
    client_id_sp1 = config["client_id_sp1"]
    tenant_id_sp1 = tenant_id  # Identique au Service Principal 2

    # Créer les credentials pour le Service Principal 1
    sp1_credential = ClientSecretCredential(tenant_id_sp1, client_id_sp1, sp1_password)

    # URL du compte Blob Storage
    blob_storage_url = config["blob_storage_url"]
    container_name = config["container_name"]

    # Connexion au Blob Storage
    try:
        blob_service_client = BlobServiceClient(account_url=blob_storage_url, credential=sp1_credential)

        # Lister les blobs dans un conteneur
        container_client = blob_service_client.get_container_client(container_name)
        print(f"Blobs dans le conteneur '{container_name}':")
        for blob in container_client.list_blobs():
            print(f"- {blob.name}")
    except Exception as e:
        print(f"Erreur lors de la connexion au Blob Storage : {e}")
    
    return sp1_password
