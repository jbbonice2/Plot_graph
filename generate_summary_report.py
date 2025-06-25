import os
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

def extract_metadata(filename):
    """Extrait les métadonnées du nom de fichier"""
    pattern = r'received_data_experience-\d{2}-\d{2}-\d{4}_\d{2}h\d{2}-\d{2}h\d{2}_SF(\d+)_BW(\d+)_CR(\d+)_(\d+)\.csv'
    match = re.search(pattern, filename)
    if match:
        sf, bw, cr, payload = match.groups()
        return {
            'SF': int(sf),
            'BW': int(bw),
            'CR': int(cr),
            'Payload': int(payload),
            'File': filename
        }
    return None

def analyze_data_files(directory):
    """Analyse tous les fichiers CSV du répertoire et retourne un DataFrame avec les résultats"""
    results = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            metadata = extract_metadata(filename)
            if not metadata:
                continue
                
            # Compter le nombre de lignes dans le fichier (moins l'en-tête)
            with open(os.path.join(directory, filename), 'r') as f:
                line_count = sum(1 for _ in f) - 1
                
            # Ajouter les résultats
            results.append({
                'SF': metadata['SF'],
                'BW': metadata['BW'],
                'CR': metadata['CR'],
                'Payload': metadata['Payload'],
                'Messages_Received': line_count,
                'File': metadata['File']
            })
    
    return pd.DataFrame(results)

def generate_summary_plots(df, output_dir='graphs'):
    """Génère des graphiques de synthèse"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculer le taux de livraison (on suppose 200 messages attendus par expérience)
    df['Delivery_Rate'] = (df['Messages_Received'] / 200) * 100
    
    # Trier par SF et par taille de payload
    df_sorted = df.sort_values(['SF', 'Payload'])
    
    # 1. Graphique à barres groupées du PDR
    plt.figure(figsize=(14, 8))
    
    # Paramètres du graphique
    bar_width = 0.25
    index = range(len(df['SF'].unique()))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Bleu, Orange, Vert
    
    # Créer les barres groupées pour chaque taille de payload
    for i, payload in enumerate(sorted(df['Payload'].unique())):
        payload_data = df_sorted[df_sorted['Payload'] == payload]
        positions = [x + i * bar_width for x in index]
        
        bars = plt.bar(
            positions,
            payload_data['Delivery_Rate'],
            bar_width,
            label=f'{payload} octets',
            color=colors[i],
            edgecolor='black',
            linewidth=0.7,
            alpha=0.8
        )
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 1,  # Légèrement au-dessus de la barre
                f'{height:.1f}%',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )
    
    # Configuration du graphique
    plt.xlabel('Spreading Factor (SF)', fontsize=12, labelpad=10)
    plt.ylabel('Taux de livraison (%)', fontsize=12, labelpad=10)
    plt.title('Taux de livraison (PDR) par Spreading Factor et taille de payload', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Définir les étiquettes de l'axe X (SF)
    plt.xticks([x + bar_width for x in index], sorted(df['SF'].unique()))
    
    # Ajouter une légende
    plt.legend(title='Taille de la payload', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Ajouter une grille pour une meilleure lisibilité
    plt.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
    
    # Ajuster les limites de l'axe Y
    plt.ylim(0, 110)  # 0-100% avec un peu de marge pour les étiquettes
    
    # Ajouter un fond de couleur légèrement gris pour les barres
    plt.gca().set_facecolor('#f9f9f9')
    
    # Ajuster les marges
    plt.tight_layout()
    
    # Sauvegarder le graphique
    plt.savefig(os.path.join(output_dir, 'delivery_rate_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Nombre de messages reçus par configuration
    plt.figure(figsize=(14, 8))
    
    # Créer des barres groupées par SF et par taille de payload
    bar_width = 0.25
    index = range(len(df['SF'].unique()))
    
    for i, payload in enumerate(sorted(df['Payload'].unique())):
        payload_data = df[df['Payload'] == payload]
        plt.bar([x + i*bar_width for x in index], 
                payload_data['Messages_Received'], 
                bar_width, 
                label=f'{payload} octets')
    
    plt.xlabel('Spreading Factor (SF)')
    plt.ylabel('Nombre de messages reçus')
    plt.title('Nombre de messages reçus par configuration')
    plt.xticks([x + bar_width for x in index], sorted(df['SF'].unique()))
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'messages_received_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Tableau récapitulatif
    summary_df = df.pivot_table(
        index=['SF', 'BW', 'CR'],
        columns='Payload',
        values='Delivery_Rate',
        aggfunc='first'
    ).round(1)
    
    # Sauvegarder le tableau récapitulatif
    plt.figure(figsize=(12, 6))
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    # Créer le tableau
    table = plt.table(
        cellText=summary_df.values,
        rowLabels=summary_df.index.map(lambda x: f"SF{x[0]} BW{x[1]} CR{x[2]}"),
        colLabels=[f"{col} octets" for col in summary_df.columns],
        cellLoc='center',
        loc='center',
        colColours=['#f3f3f3']*len(summary_df.columns),
        rowColours=['#f3f3f3']*len(summary_df)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    plt.title('Taux de livraison (%) par configuration', y=0.8, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'delivery_rate_table.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_html_report(df, output_dir='graphs'):
    """Génère un rapport HTML"""
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rapport d'analyse LoRaWAN</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .summary {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .images {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
            .image-container {{ flex: 1; min-width: 300px; }}
            .image-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
            .image-container p {{ text-align: center; font-style: italic; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rapport d'analyse LoRaWAN</h1>
            <p>Généré le {date_str}</p>
            
            <div class="summary">
                <h2>Résumé des configurations testées</h2>
                <p>Nombre total d'expériences analysées : {len(df)}</p>
                <p>Spreading Factors testés : {', '.join(map(str, sorted(df['SF'].unique())))}</p>
                <p>Tailles de payload testées : {', '.join(map(str, sorted(df['Payload'].unique())))} octets</p>
            </div>
            
            <h2>1. Taux de livraison par configuration</h2>
            <div class="images">
                <div class="image-container">
                    <img src="delivery_rate_summary.png" alt="Taux de livraison">
                    <p>Figure 1: Taux de livraison par Spreading Factor et taille de payload</p>
                </div>
            </div>
            
            <h2>2. Nombre de messages reçus</h2>
            <div class="images">
                <div class="image-container">
                    <img src="messages_received_summary.png" alt="Messages reçus">
                    <p>Figure 2: Nombre de messages reçus par configuration</p>
                </div>
            </div>
            
            <h2>3. Tableau récapitulatif</h2>
            <div class="images">
                <div class="image-container">
                    <img src="delivery_rate_table.png" alt="Tableau récapitulatif">
                    <p>Figure 3: Taux de livraison (%) par configuration</p>
                </div>
            </div>
            
            <h2>4. Détails par expérience</h2>
            <table>
                <tr>
                    <th>Fichier</th>
                    <th>SF</th>
                    <th>BW</th>
                    <th>CR</th>
                    <th>Payload (octets)</th>
                    <th>Messages reçus</th>
                    <th>Taux de livraison</th>
                </tr>
    """
    
    # Trier les données par SF et par taille de payload
    df_sorted = df.sort_values(['SF', 'Payload'])
    
    # Ajouter les lignes du tableau
    for _, row in df_sorted.iterrows():
        html_content += f"""
                <tr>
                    <td>{row['File']}</td>
                    <td>{row['SF']}</td>
                    <td>{row['BW']}</td>
                    <td>{row['CR']}</td>
                    <td>{row['Payload']}</td>
                    <td>{row['Messages_Received']}/200</td>
                    <td>{row['Delivery_Rate']:.1f}%</td>
                </tr>
        """
    
    # Fin du document HTML
    html_content += """
            </table>
            
            <div class="footer" style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #777; font-size: 0.9em;">
                <p>Rapport généré automatiquement</p>
            </div>
        </div>
    </body>
    </html>
    """.format(date=datetime.now().strftime("%d/%m/%Y à %H:%M"))
    
    # Écrire le fichier HTML
    with open(os.path.join(output_dir, 'lorawan_analysis_report.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # Répertoire contenant les données
    data_dir = 'Data/Max'
    output_dir = 'graphs'
    
    # Analyser les fichiers
    print(f"Analyse des fichiers dans {data_dir}...")
    df = analyze_data_files(data_dir)
    
    # Générer les graphiques de synthèse
    print("\nGénération des graphiques de synthèse...")
    generate_summary_plots(df, output_dir)
    
    # Générer le rapport HTML
    print("Génération du rapport HTML...")
    generate_html_report(df, output_dir)
    
    print(f"\nAnalyse terminée. Le rapport est disponible dans {output_dir}/lorawan_analysis_report.html")

if __name__ == "__main__":
    main()
