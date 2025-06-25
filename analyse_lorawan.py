# import json
# import pandas as pd
# import matplotlib.pyplot as plt
# import sys

# # Vérifie qu’un argument est bien passé
# if len(sys.argv) != 2:
#     print("Usage : python analyse_lorawan.py <fichier_json>")
#     sys.exit(1)

# json_file = sys.argv[1]

# # Charger les données JSON
# with open(json_file, 'r') as f:
#     data = json.load(f)

# # Convertir en DataFrame
# df = pd.DataFrame(data)

# # Extraire le message_id depuis _id
# df['message_id'] = df['_id'].apply(lambda x: x['$oid'])

# # Extraire le spreading factor depuis datarate (ex : "SF12BW125" -> "SF12")
# df['spreading_factor'] = df['datarate'].apply(lambda x: x.split('BW')[0])

# # Trier les messages dans l'ordre d'apparition (optionnel)
# df = df.sort_values('message_id').reset_index(drop=True)

# # === 1. Graphique SNR par message_id ===
# plt.figure(figsize=(12, 6))
# for sf, group in df.groupby('spreading_factor'):
#     plt.plot(group['message_id'], group['snr'], label=sf)
# plt.xticks(rotation=90, fontsize=6)
# plt.xlabel("Message ID")
# plt.ylabel("SNR (dB)")
# plt.title("SNR par Spreading Factor")
# plt.legend()
# plt.tight_layout()
# plt.savefig("snr_par_sf.png")
# plt.close()

# # === 2. Graphique RSSI par message_id ===
# plt.figure(figsize=(12, 6))
# for sf, group in df.groupby('spreading_factor'):
#     plt.plot(group['message_id'], group['rssi'], label=sf)
# plt.xticks(rotation=90, fontsize=6)
# plt.xlabel("Message ID")
# plt.ylabel("RSSI (dBm)")
# plt.title("RSSI par Spreading Factor")
# plt.legend()
# plt.tight_layout()
# plt.savefig("rssi_par_sf.png")
# plt.close()

# # === 3. Taux de livraison ===
# nb_total_messages = 200
# group_size = 10
# steps = range(group_size, len(df) + group_size, group_size)

# delivery_rates = []
# x_axis = []

# for i in steps:
#     delivered = min(i, len(df))
#     rate = delivered / nb_total_messages
#     delivery_rates.append(rate)
#     x_axis.append(i)

# plt.figure(figsize=(10, 6))
# plt.hist(x_axis, weights=delivery_rates, bins=len(x_axis), edgecolor='black')
# plt.xlabel("Nombre de messages (par pas de 10)")
# plt.ylabel("Taux de livraison")
# plt.title("Taux de Livraison de Paquets")
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.savefig("taux_livraison.png")
# plt.close()

# print("✅ Graphiques générés :")
# print(" - snr_par_sf.png")
# print(" - rssi_par_sf.png")
# print(" - taux_livraison.png")

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Vérifie qu’un argument est bien passé
if len(sys.argv) != 2:
    print("Usage : python analyse_lorawan.py <fichier_json>")
    sys.exit(1)

json_file = sys.argv[1]

# Charger les données JSON
with open(json_file, 'r') as f:
    data = json.load(f)

# Convertir en DataFrame
df = pd.DataFrame(data)

# Extraire le message_id depuis _id
df['message_id'] = df['_id'].apply(lambda x: x['$oid'])

# Extraire le spreading factor depuis datarate (ex : "SF12BW125" -> "SF12")
df['spreading_factor'] = df['datarate'].apply(lambda x: x.split('BW')[0])

# Trier les messages dans l'ordre d'apparition (optionnel)
df = df.sort_values('message_id').reset_index(drop=True)

# Fonction pour ajouter des statistiques au graphique
def add_stats(ax, values, xpos=0.02, ypos=0.98):
    stats = f"Moyenne: {values.mean():.2f}\n" \
            f"Médiane: {values.median():.2f}\n" \
            f"Min: {values.min():.2f}\n" \
            f"Max: {values.max():.2f}"
    ax.text(xpos, ypos, stats, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# === 1. Graphique SNR par message_id ===
plt.figure(figsize=(14, 7))
ax = plt.gca()

# Tracer chaque groupe de SF
for sf, group in df.groupby('spreading_factor'):
    # Convertir les message_id en numéros de séquence
    x = range(1, len(group) + 1)
    plt.plot(x, group['snr'], 'o-', label=f'{sf} (n={len(group)})', markersize=4, linewidth=1)

plt.xticks(rotation=45, fontsize=8)
plt.xlabel("Numéro de séquence du message")
plt.ylabel("SNR (dB)")
plt.title(f"SNR par Spreading Factor - {os.path.basename(json_file)}")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Ajouter des statistiques globales
add_stats(ax, df['snr'])

# Sauvegarder avec une meilleure résolution
plt.savefig("snr_par_sf.png", dpi=150, bbox_inches='tight')
plt.close()

# === 2. Graphique RSSI par message_id ===
plt.figure(figsize=(14, 7))
ax = plt.gca()

for sf, group in df.groupby('spreading_factor'):
    x = range(1, len(group) + 1)
    plt.plot(x, group['rssi'], 'o-', label=f'{sf} (n={len(group)})', markersize=4, linewidth=1)

plt.xticks(rotation=45, fontsize=8)
plt.xlabel("Numéro de séquence du message")
plt.ylabel("RSSI (dBm)")
plt.title(f"RSSI par Spreading Factor - {os.path.basename(json_file)}")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Ajouter des statistiques
add_stats(ax, df['rssi'])

plt.savefig("rssi_par_sf.png", dpi=150, bbox_inches='tight')
plt.close()

# === 3. Taux de livraison ===
nb_total_messages = 200
group_size = 10

# Calculer le taux de livraison cumulatif
df_sorted = df.sort_values('time')
delivery_rates = []
x_axis = []

for i in range(1, len(df_sorted) + 1):
    rate = (i / nb_total_messages) * 100  # en pourcentage
    delivery_rates.append(rate)
    x_axis.append(i)

# Tracer le taux de livraison cumulatif
plt.figure(figsize=(12, 6))
plt.plot(x_axis, delivery_rates, 'b-', linewidth=2, label='Taux de livraison')
plt.axhline(y=100, color='r', linestyle='--', label='100% de livraison')
plt.axvline(x=len(df), color='g', linestyle='--', alpha=0.5, label=f'Messages reçus: {len(df)}')

plt.xlabel("Nombre de messages reçus")
plt.ylabel("Taux de livraison (%)")
plt.title(f"Taux de Livraison de Paquets - {os.path.basename(json_file)}")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Afficher le taux de livraison final
plt.text(0.02, 0.12, f"Taux final: {delivery_rates[-1]:.1f}%\n"
                     f"Messages reçus: {len(df)}/{nb_total_messages}",
         transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))

plt.savefig("taux_livraison.png", dpi=150, bbox_inches='tight')
plt.close()

print("✅ Graphiques générés :")
print(" - snr_par_sf.png")
print(" - rssi_par_sf.png")
print(" - taux_livraison.png")