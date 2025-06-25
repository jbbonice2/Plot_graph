# Analyse des Données LoRaWAN

Ce projet permet d'analyser des données expérimentales LoRaWAN et de générer des visualisations pertinentes pour évaluer les performances du réseau.

## 📋 Prérequis

- Python 3.6 ou supérieur
- Bibliothèques Python :
  - pandas
  - matplotlib
  - numpy
  - re
  - os
  - sys
  - datetime

## 🚀 Installation

1. Cloner le dépôt :
   ```bash
   git clone [URL_DU_REPO]
   cd Draw_graphique
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Structure du Projet

```
Draw_graphique/
├── Data/
│   ├── Max/          # Données avec puissance d'émission maximale
│   ├── Min/          # Données avec puissance d'émission minimale
│   └── Moy/          # Données avec puissance d'émission moyenne
├── graphs/           # Dossier de sortie pour les graphiques
├── analyse_lorawan.py    # Script d'analyse principal (obsolète - format JSON)
├── analyse_csv_lorawan.py # Script principal pour l'analyse des CSV
├── generate_summary_report.py  # Génération de rapports synthétiques
└── README.md          # Ce fichier
```

## 🛠 Utilisation

### Analyse des fichiers CSV

Pour analyser un dossier contenant des fichiers CSV :

```bash
python analyse_csv_lorawan.py chemin/vers/le/dossier
```

Exemple :
```bash
python analyse_csv_lorawan.py Data/Max/
```

### Génération d'un rapport synthétique

Pour générer un rapport complet avec des graphiques synthétiques :

```bash
python generate_summary_report.py chemin/vers/le/dossier
```
Exemple :
```bash
python generate_summary_report.py Data/Max/
```


## 📈 Visualisations Générées

Pour chaque fichier CSV analysé, les graphiques suivants sont générés dans le dossier `graphs/` :

1. **Graphiques temporels** :
   - Évolution du SNR en fonction de l'heure
   - Évolution du RSSI en fonction de l'heure
   - Évolution du PDR (Packet Delivery Ratio) en fonction de l'heure

2. **Graphiques synthétiques** (via `generate_summary_report.py`) :
   - Taux de livraison par Spreading Factor et taille de payload
   - Nombre de messages reçus par configuration
   - Tableau récapitulatif des performances

## 📝 Format des Fichiers d'Entrée

Les fichiers CSV doivent suivre le format suivant :
```
type;gateway_eui;node_eui;snr;rssi;cr;datarate;time;data
"rx";"1234567890ABCDEF";"1234567890ABCDEF";7.5;-85;"4/5";"SF7BW500";"2025-06-07T10:08:44.123Z";"{\"rssi\":-85,\"snr\":7.5}"
```

## 📊 Métriques Analysées

- **SNR** (Signal-to-Noise Ratio) : Rapport signal sur bruit en dB
- **RSSI** (Received Signal Strength Indicator) : Puissance du signal reçu en dBm
- **PDR** (Packet Delivery Ratio) : Taux de livraison des paquets en %

## 📅 Historique des Versions

- **1.0.0** (25/06/2025)
  - Version initiale avec support des fichiers CSV
  - Génération de graphiques temporels
  - Rapports synthétiques

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
