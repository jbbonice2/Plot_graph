import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def parse_csv_file(csv_path):
    """Parse un fichier CSV LoRaWAN et retourne un DataFrame"""
    data = []
    
    # Extraire les paramètres du nom de fichier
    filename = os.path.basename(csv_path)
    
    # Extraire SF (ex: SF7, SF12) et la taille de la payload (dernier nombre avant .csv)
    sf_match = re.search(r'SF(\d+)', filename)
    payload_match = re.search(r'_(\d+)\.csv$', filename)
    
    sf = int(sf_match.group(1)) if sf_match else 0
    payload_size = int(payload_match.group(1)) if payload_match else 0
    
    print(f"  - Fichier: {filename}")
    print(f"  - Spreading Factor: {sf}")
    print(f"  - Taille de la payload: {payload_size} octets")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Lire l'en-tête
        header = f.readline().strip().strip('"').split(';')
        
        for line_num, line in enumerate(f, 2):  # Commencer à 2 car on a déjà lu la première ligne
            try:
                line = line.strip()
                if not line:
                    continue
                    
                # Nettoyer et diviser la ligne
                parts = line.strip('"').split(';')
                if len(parts) < 8:
                    print(f"Ligne {line_num} ignorée: pas assez de champs")
                    continue
                
                # Extraire les données
                data_str = ';'.join(parts[8:]) if len(parts) > 8 else ''
                
                # Extraire SNR et RSSI
                rssi = int(parts[4]) if parts[4].lstrip('-').isdigit() else None
                snr = int(parts[3]) if parts[3].lstrip('-').isdigit() else None
                
                # Si pas trouvé, essayer de les extraire du champ data
                if rssi is None or snr is None:
                    rssi_match = re.search(r'"RSSI"\s*:\s*(-?\d+)', data_str)
                    snr_match = re.search(r'"SNR"\s*:\s*(-?\d+)', data_str)
                    
                    if rssi_match:
                        rssi = int(rssi_match.group(1))
                    if snr_match:
                        snr = int(snr_match.group(1))
                
                if rssi is None or snr is None:
                    print(f"Ligne {line_num}: Impossible d'extraire RSSI ou SNR")
                    continue
                
                # Extraire le Spreading Factor
                sf_match = re.search(r'SF(\d+)', parts[6])
                sf = int(sf_match.group(1)) if sf_match else 0
                
                # Créer l'entrée de données
                entry = {
                    'message_id': len(data) + 1,
                    'time': parts[7],
                    'rssi': rssi,
                    'snr': snr,
                    'sf': sf,
                    'datarate': parts[6],
                    'cr': int(parts[5]) if parts[5].isdigit() else 5,
                    'node_eui': parts[2],
                    'gateway_eui': parts[1]
                }
                data.append(entry)
                
            except Exception as e:
                print(f"Erreur ligne {line_num}: {e}")
                continue
    
    if not data:
        print(f"Aucune donnée valide trouvée dans {csv_path}")
        return None
    
    # Créer un DataFrame
    df = pd.DataFrame(data)
    
    # Convertir la date en datetime
    try:
        df['datetime'] = pd.to_datetime(df['time'])
        df = df.sort_values('datetime')
    except Exception as e:
        print(f"Erreur de conversion de date: {e}")
        df = df.sort_values('message_id')
    
    return df



def generate_plots(df, output_dir='graphs', prefix=''):
    """Génère les graphiques à partir du DataFrame"""
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Extraire la taille de la payload depuis le préfixe
    payload_size = 0
    payload_match = re.search(r'_(\d+)\.csv$', prefix)
    if payload_match:
        payload_size = int(payload_match.group(1))
    
    # 1. Graphique SNR par message
    plt.figure(figsize=(14, 7))
    for sf, group in df.groupby('sf'):
        plt.plot(group['message_id'], group['snr'], 'o-', label=f'SF{sf} (n={len(group)})', markersize=4, linewidth=1)
    
    plt.xlabel("Numéro de séquence du message")
    plt.ylabel("SNR (dB)")
    plt.title(f"SNR par Spreading Factor - {prefix}")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    # Ajouter des statistiques
    stats_text = f"Moyenne: {df['snr'].mean():.1f} dB\n" \
                f"Médiane: {df['snr'].median():.1f} dB\n" \
                f"Min: {df['snr'].min():.1f} dB\n" \
                f"Max: {df['snr'].max():.1f} dB"
    
    plt.gca().text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                  verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Sauvegarder
    plt.savefig(os.path.join(output_dir, f"{prefix}snr_par_message.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Graphique RSSI par message
    plt.figure(figsize=(14, 7))
    for sf, group in df.groupby('sf'):
        plt.plot(group['message_id'], group['rssi'], 'o-', label=f'SF{sf} (n={len(group)})', markersize=4, linewidth=1)
    
    plt.xlabel("Numéro de séquence du message")
    plt.ylabel("RSSI (dBm)")
    plt.title(f"RSSI par Spreading Factor - {prefix}")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    # Ajouter des statistiques
    stats_text = f"Moyenne: {df['rssi'].mean():.1f} dBm\n" \
                f"Médiane: {df['rssi'].median():.1f} dBm\n" \
                f"Min: {df['rssi'].min():.1f} dBm\n" \
                f"Max: {df['rssi'].max():.1f} dBm"
    
    plt.gca().text(0.02, 0.02, stats_text, transform=plt.gca().transAxes,
                  verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Sauvegarder
    plt.savefig(os.path.join(output_dir, f"{prefix}rssi_par_message.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Taux de livraison - Sauvegarder les données pour le graphique combiné
    nb_messages = len(df)
    nb_expected = 200  # Nombre de messages attendus
    delivery_rate = (nb_messages / nb_expected) * 100
    
    # Créer un graphique individuel pour ce fichier
    plt.figure(figsize=(10, 6))
    plt.bar(['Messages reçus', 'Messages perdus'], 
            [nb_messages, max(0, nb_expected - nb_messages)],
            color=['green', 'red'])
    
    plt.ylabel('Nombre de messages')
    plt.title(f"Taux de livraison - {prefix}\n{delivery_rate:.1f}% ({nb_messages}/{nb_expected})")
    
    # Afficher les valeurs sur les barres
    for i, v in enumerate([nb_messages, max(0, nb_expected - nb_messages)]):
        plt.text(i, v + 1, str(v), ha='center')
    
    plt.ylim(0, nb_expected * 1.1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}taux_livraison.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Retourner les données pour le graphique combiné
    return {
        'payload_size': payload_size,
        'sf': df['sf'].iloc[0] if not df.empty else 0,
        'messages_received': nb_messages,
        'delivery_rate': delivery_rate,
        'prefix': prefix
    }

def process_file(csv_path, output_dir='graphs'):
    """Traite un fichier CSV et génère les graphiques"""
    print(f"\nTraitement de {os.path.basename(csv_path)}...")
    
    # Extraire le préfixe du nom de fichier
    filename = os.path.basename(csv_path)
    prefix = os.path.splitext(filename)[0] + '_'
    
    # Parser le fichier CSV
    df = parse_csv_file(csv_path)
    if df is None or df.empty:
        print("  - Aucune donnée valide trouvée dans le fichier.")
        return None
    
    # Afficher des informations sur les données
    print(f"  - Fichier: {filename}")
    print(f"  - Spreading Factor: {df['sf'].iloc[0] if not df.empty else 'N/A'}")
    
    # Extraire la taille de la payload du nom de fichier
    payload_match = re.search(r'_(\d+)\.csv$', filename)
    if payload_match:
        payload_size = int(payload_match.group(1))
        print(f"  - Taille de la payload: {payload_size} octets")
    
    print(f"  - {len(df)} messages valides trouvés")
    print(f"  - Spreading Factors: {sorted(df['sf'].unique())}")
    print(f"  - Période: {df['time'].min()} à {df['time'].max()}")
    
    # Générer les graphiques temporels pour ce fichier
    generate_time_series_plots(df, output_dir, prefix)
    
    # Générer les autres graphiques et récupérer les données du PDR
    return generate_plots(df, output_dir, prefix)

def process_directory(directory_path, output_dir='graphs'):
    """Traite tous les fichiers CSV d'un répertoire et génère un graphique combiné du PDR"""
    print(f"\nTraitement des fichiers dans {directory_path}")
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Liste pour stocker les données de tous les fichiers
    all_pdr_data = []
    
    # Parcourir tous les fichiers CSV du répertoire
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            pdr_data = process_file(file_path, output_dir)
            if pdr_data:
                all_pdr_data.append(pdr_data)
    
    # Générer le graphique combiné du PDR si on a des données
    if all_pdr_data:
        generate_combined_pdr_plot(all_pdr_data, output_dir)


def generate_time_series_plots(df, output_dir='graphs', prefix=''):
    """Génère des graphiques temporels pour SNR, RSSI et PDR avec l'heure en abscisse"""
    if df is None or df.empty:
        return
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # S'assurer que la colonne 'time' est au format datetime
    if not pd.api.types.is_datetime64_any_dtype(df['time']):
        df['time'] = pd.to_datetime(df['time'])
    
    # Trier les données par temps
    df = df.sort_values('time')
    
    # Extraire la date et l'heure des timestamps
    date_str = df['time'].dt.strftime('%d/%m/%Y').iloc[0]  # Format: JJ/MM/AAAA
    df['hour_minute'] = df['time'].dt.strftime('%H:%M')
    
    # Créer un titre avec la date
    title_date = f" - {date_str}"
    
    # Calculer le PDR glissant sur une fenêtre de 10 messages
    window_size = 10
    df['pdr'] = df.groupby('sf')['message_id'].transform(
        lambda x: x.rolling(window=window_size, min_periods=1).count() / window_size * 100
    )
    
    # Créer une figure avec 3 sous-graphiques
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 16), sharex=True)
    
    # Couleurs pour chaque SF
    colors = {7: '#1f77b4', 9: '#ff7f0e', 12: '#d62728'}
    
    # 1. Graphique SNR
    for sf, group in df.groupby('sf'):
        ax1.plot(
            group['hour_minute'], 
            group['snr'], 
            'o-',
            markersize=4,
            linewidth=1,
            color=colors.get(sf, '#000000'),
            label=f'SF{int(sf)}',
            alpha=0.7
        )
    
    ax1.set_ylabel('SNR (dB)', fontsize=12)
    ax1.set_title('Évolution du SNR en fonction de l\'heure', fontsize=14, pad=15)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()
    
    # 2. Graphique RSSI
    for sf, group in df.groupby('sf'):
        ax2.plot(
            group['hour_minute'], 
            group['rssi'], 
            'o-',
            markersize=4,
            linewidth=1,
            color=colors.get(sf, '#000000'),
            label=f'SF{int(sf)}',
            alpha=0.7
        )
    
    ax2.set_ylabel('RSSI (dBm)', fontsize=12)
    ax2.set_title('Évolution du RSSI en fonction de l\'heure', fontsize=14, pad=15)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    
    # 3. Graphique PDR glissant
    for sf, group in df.groupby('sf'):
        ax3.plot(
            group['hour_minute'], 
            group['pdr'], 
            'o-',
            markersize=4,
            linewidth=1,
            color=colors.get(sf, '#000000'),
            label=f'SF{int(sf)}',
            alpha=0.7
        )
    
    ax3.set_xlabel('Heure (HH:MM)', fontsize=12)
    ax3.set_ylabel('PDR (%)', fontsize=12)
    ax3.set_title(f'Évolution du PDR (moyenne glissante sur 10 messages) en fonction de l\'heure{title_date}', 
                 fontsize=14, pad=15)
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend()
    
    # Rotation des étiquettes de l'axe des x pour une meilleure lisibilité
    plt.xticks(rotation=45, ha='right')
    
    # Ajuster l'espacement pour éviter que les étiquettes ne soient coupées
    plt.subplots_adjust(bottom=0.15)
    
    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()
    
    # Sauvegarder la figure
    output_path = os.path.join(output_dir, f"{prefix}time_series_metrics.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Graphiques temporels générés : {output_path}")


def generate_combined_pdr_plot(pdr_data_list, output_dir='graphs'):
    """Génère un histogramme groupé du PDR pour toutes les combinaisons SF et tailles de payload"""
    if not pdr_data_list:
        return
    
    # Créer un DataFrame à partir des données
    df = pd.DataFrame(pdr_data_list)
    
    # Trier par SF et par taille de payload
    df = df.sort_values(['sf', 'payload_size'])
    
    # Créer une figure plus large pour une meilleure lisibilité
    plt.figure(figsize=(16, 9))
    
    # Définir les positions des barres pour chaque groupe
    sf_values = sorted(df['sf'].unique())
    payload_sizes = sorted(df['payload_size'].unique())
    
    # Largeur d'une barre
    bar_width = 0.25
    
    # Position des ticks sur l'axe X
    x = np.arange(len(sf_values))
    
    # Couleurs et motifs pour chaque taille de payload
    colors = {
        20: '#1f77b4',  # Bleu
        50: '#ff7f0e',   # Orange
        80: '#d62728'    # Rouge
    }
    
    # Motifs de hachurage pour une meilleure différenciation
    patterns = {
        20: None,       # Pas de motif
        50: '////',     # Hachures diagonales
        80: '..'        # Pointillés
    }
    
    # Pour chaque taille de payload, créer un groupe de barres
    for i, payload in enumerate(payload_sizes):
        # Récupérer les valeurs de PDR pour cette taille de payload
        pdr_values = []
        for sf in sf_values:
            mask = (df['sf'] == sf) & (df['payload_size'] == payload)
            if mask.any():
                pdr_values.append(df.loc[mask, 'delivery_rate'].values[0])
            else:
                pdr_values.append(0)
        
        # Calculer la position de chaque barre dans le groupe
        x_pos = x + (i * bar_width) - (bar_width * (len(payload_sizes) - 1) / 2)
        
        # Créer les barres pour cette taille de payload
        bars = plt.bar(
            x_pos, 
            pdr_values, 
            width=bar_width,
            label=f'{payload} octets',
            color=colors.get(payload, '#8c564b'),  # Couleur par défaut si taille non reconnue
            edgecolor='black',
            linewidth=0.7,
            alpha=0.8,
            hatch=patterns.get(payload, None)  # Ajout du motif de hachurage
        )
        
        # Ajouter les étiquettes de valeur au-dessus de chaque barre
        for bar, value in zip(bars, pdr_values):
            if value > 0:  # Ne pas afficher d'étiquette pour les valeurs nulles
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + 1,  # Légèrement au-dessus de la barre
                    f'{value:.1f}%',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )
    
    # Configurer le graphique
    plt.title('Taux de livraison (PDR) par Spreading Factor et taille de payload', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Spreading Factor (SF)', fontsize=12, labelpad=10)
    plt.ylabel('Taux de livraison (%)', fontsize=12, labelpad=10)
    
    # Définir les étiquettes de l'axe X (SF)
    plt.xticks(x, [f'SF{int(sf)}' for sf in sf_values])
    
    # Ajouter une grille pour une meilleure lisibilité
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ajuster les limites de l'axe Y
    plt.ylim(0, 110)
    
    # Ajouter une légende avec un fond blanc semi-transparent
    legend = plt.legend(
        title='Taille de la payload (octets)', 
        bbox_to_anchor=(1.05, 1), 
        loc='upper left',
        frameon=True,
        fancybox=True,
        framealpha=0.9,
        edgecolor='gray'
    )
    legend.get_title().set_fontweight('bold')
    
    # Améliorer la lisibilité du titre et des axes
    plt.title('Taux de livraison (PDR) par Spreading Factor et taille de payload', 
              fontsize=14, fontweight='bold', pad=20, color='#333333')
    plt.xlabel('Spreading Factor (SF)', fontsize=12, labelpad=10, color='#333333')
    plt.ylabel('Taux de livraison (%)', fontsize=12, labelpad=10, color='#333333')
    
    # Améliorer les ticks
    plt.tick_params(axis='both', which='major', labelsize=10, colors='#333333')
    
    # Ajouter une grille plus visible
    plt.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
    
    # Ajouter un fond de couleur légèrement gris pour les barres
    plt.gca().set_facecolor('#f9f9f9')
    
    # Ajouter une bordure autour du graphique
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('#dddddd')
        spine.set_linewidth(0.5)
    
    # Ajuster les marges
    plt.tight_layout()
    
    # Sauvegarder le graphique en haute résolution
    output_path = os.path.join(output_dir, 'pdr_grouped_barchart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nHistogramme groupé du PDR généré : {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyse_csv_lorawan.py <chemin_vers_fichier_ou_dossier>")
        print("Exemple: python analyse_csv_lorawan.py Data/Max/")
        sys.exit(1)
    
    path = sys.argv[1]
    output_dir = 'graphs'
    
    if os.path.isdir(path):
        process_directory(path, output_dir)
    elif os.path.isfile(path) and path.lower().endswith('.csv'):
        process_file(path, output_dir)
    else:
        print("Le chemin doit être un fichier .csv ou un dossier contenant des fichiers .csv")
        sys.exit(1)
