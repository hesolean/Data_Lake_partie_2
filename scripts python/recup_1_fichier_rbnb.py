import requests

# URL du fichier à télécharger
url = "https://insideairbnb.com/get-the-data/"

# Chemin local où le fichier sera sauvegardé
output_file = "/home/helene/Documents/Brief Azure Data Lake 2/essai Rbnb.csv"

try:
    # Envoyer une requête GET pour télécharger le fichier
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Vérifie si la requête a réussi (200 OK)

    # Écrire le contenu du fichier téléchargé sur le disque
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Fichier téléchargé avec succès : {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Erreur lors du téléchargement : {e}")
