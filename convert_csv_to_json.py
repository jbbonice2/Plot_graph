import json
import os
import sys
import re

def convert_csv_to_json(csv_file_path, json_file_path):
    data = []
    message_id = 1
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        # Lire l'en-tête
        header = f.readline().strip().strip('"').split(';')
        
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Nettoyer et diviser la ligne
            parts = line.strip('"').split(';')
            if len(parts) < 8:
                continue
                
            # Extraire les données de base
            try:
                # Extraire SNR et RSSI du champ data s'ils sont disponibles
                data_str = ';'.join(parts[8:]) if len(parts) > 8 else ''
                rssi = None
                snr = None
                
                # Essayer d'extraire depuis le champ data
                rssi_match = re.search(r'"RSSI"\s*:\s*(-?\d+)', data_str)
                snr_match = re.search(r'"SNR"\s*:\s*(-?\d+)', data_str)
                
                if rssi_match:
                    rssi = int(rssi_match.group(1))
                else:
                    rssi = int(parts[4]) if parts[4].lstrip('-').isdigit() else None
                    
                if snr_match:
                    snr = int(snr_match.group(1))
                else:
                    snr = int(parts[3]) if parts[3].lstrip('-').isdigit() else None
                
                if rssi is None or snr is None:
                    continue
                    
                entry = {
                    "_id": {"$oid": str(message_id)},
                    "snr": snr,
                    "rssi": rssi,
                    "cr": int(parts[5]) if parts[5].isdigit() else 5,
                    "datarate": parts[6],
                    "time": parts[7],
                    "gateway_eui": parts[1],
                    "node_eui": parts[2]
                }
                data.append(entry)
                message_id += 1
                
            except Exception as e:
                print(f"Erreur ligne {message_id}: {e}")
                continue
    
    if not data:
        print(f"Aucune donnée valide trouvée dans {csv_file_path}")
        return False
    
    # Créer le répertoire de destination si nécessaire
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    # Écrire les données dans un fichier JSON
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Conversion réussie : {os.path.basename(csv_file_path)} -> {os.path.basename(json_file_path)} ({len(data)} messages)")
    return True

def process_directory(directory_path):
    # Créer un sous-dossier pour les fichiers JSON s'il n'existe pas
    json_dir = os.path.join(directory_path, 'json')
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    
    # Parcourir tous les fichiers CSV du répertoire
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.csv'):
            csv_path = os.path.join(directory_path, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(json_dir, json_filename)
            
            print(f"Traitement de {filename}...")
            convert_csv_to_json(csv_path, json_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_csv_to_json.py <chemin_vers_fichier_ou_dossier>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isdir(path):
        process_directory(path)
    elif os.path.isfile(path) and path.lower().endswith('.csv'):
        json_path = os.path.splitext(path)[0] + '.json'
        convert_csv_to_json(path, json_path)
    else:
        print("Le chemin doit être un fichier .csv ou un dossier contenant des fichiers .csv")
        sys.exit(1)
