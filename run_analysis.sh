#!/bin/bash

# Activer l'environnement virtuel si nécessaire
# source venv/bin/activate

# Installer les dépendances requises
pip install pandas matplotlib

# Convertir les fichiers CSV en JSON
echo "Conversion des fichiers CSV en JSON..."
python3 convert_csv_to_json.py Data/Max/
python3 convert_csv_to_json.py Data/Min/
python3 convert_csv_to_json.py Data/Moy/

# Créer un dossier pour les graphiques
mkdir -p graphs

# Analyser les fichiers JSON générés
echo "\nAnalyse des données..."
for dir in Data/Max/json Data/Min/json Data/Moy/json; do
    if [ -d "$dir" ]; then
        echo "Traitement du dossier $dir"
        for json_file in "$dir"/*.json; do
            if [ -f "$json_file" ]; then
                echo "  Analyse de $json_file"
                python3 analyse_lorawan.py "$json_file"
                # Déplacer les graphiques générés
                mv ./*.png graphs/ 2>/dev/null || true
            fi
        done
    fi
done

echo "\nAnalyse terminée ! Les graphiques ont été enregistrés dans le dossier 'graphs/'"
