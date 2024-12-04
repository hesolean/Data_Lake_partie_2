from azure.identity import ClientSecretCredential
from dotenv import load_dotenv
import os
from azure.keyvault.secrets import SecretClient

def connexion_azure():
    # Charger les variables d'environnement
    load_dotenv()

    # Informations sur le Service Principal 1 (pour accéder au Blob Storage)
    tenant_id = os.getenv("TENANT_ID")
    client_id_sp2 = os.getenv("CLIENT_ID_SP2")
    client_secret_sp2 = os.getenv("CLIENT_SECRET_SP2")

    # URL du Blob Storage et nom du conteneur
    blob_storage_url = os.getenv("BLOB_STORAGE_URL")
    container_name = os.getenv("CONTAINER_NAME")

    # Informations sur le Service Principal 1 (récupérées via le secret)
    client_id_sp1 = os.getenv("CLIENT_ID_SP1")
    
    # URL du Key Vault et nom du secret
    key_vault_url = os.getenv("KEY_VAULT_URL")
    secret_name = os.getenv("SECRET_NAME")

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
