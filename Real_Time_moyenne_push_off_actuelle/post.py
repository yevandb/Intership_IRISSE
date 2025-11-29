import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Lecture du fichier CSV ===
file_path = r"C:\Users\irisse-q\Desktop\Yevan\Real_Time\1_vitesse_auto\data\09_07_2025\test_1.csv"
df = pd.read_csv(file_path)

# === Extraction des colonnes ===
EMG_G = df["EMG_Gauche"].to_numpy()
GRF_G = df["GRF_Gauche"].to_numpy()
VERT_G = df["VERT_Gauche"].to_numpy()
EMG_D = df["EMG_Droite"].to_numpy()
GRF_D = df["GRF_Droite"].to_numpy()
VERT_D = df["VERT_Droite"].to_numpy()
X_Mean_G = df["X_Mean_G"].to_numpy() if "X_Mean_G" in df else np.array([])
Y_Mean_G = df["Y_Mean_G"].to_numpy() if "Y_Mean_G" in df else np.array([])
X_Mean_D = df["X_Mean_D"].to_numpy() if "X_Mean_D" in df else np.array([])
Y_Mean_D = df["Y_Mean_D"].to_numpy() if "Y_Mean_D" in df else np.array([])
X_Mean_G_brute = df["X_Mean_G_brute"].to_numpy() if "X_Mean_G_brute" in df else np.array([])
Y_Mean_G_brute = df["Y_Mean_G_brute"].to_numpy() if "Y_Mean_G_brute" in df else np.array([])
X_Mean_D_brute = df["X_Mean_D_brute"].to_numpy() if "X_Mean_D_brute" in df else np.array([])
Y_Mean_D_brute = df["Y_Mean_D_brute"].to_numpy() if "Y_Mean_D_brute" in df else np.array([])
idx_fin_droite= df["Index_fin_droite"].to_numpy() if "Index_fin_droite" in df else np.array([])
idx_debut_droite= df["Index_debut_droite"].to_numpy() if "Index_debut_droite" in df else np.array([])
idx_fin_gauche= df["Index_fin_gauche"].to_numpy() if "Index_fin_gauche" in df else np.array([])
idx_debut_gauche= df["Index_debut_gauche"].to_numpy() if "Index_debut_gauche" in df else np.array([])

print(len(EMG_G), len(GRF_G), len(VERT_G))


def remove_nans(signal):
    return [x for x in signal if not np.isnan(x)]


Y_Mean_G_no_nan = remove_nans(Y_Mean_G)
Y_Mean_D_no_nan = remove_nans(Y_Mean_D)
X_Mean_G_no_nan = remove_nans(X_Mean_G)
X_Mean_D_no_nan = remove_nans(X_Mean_D)
Y_Mean_G_no_nan_brute = remove_nans(Y_Mean_G_brute)
Y_Mean_D_no_nan_brute = remove_nans(Y_Mean_D_brute)
X_Mean_G_no_nan_brute = remove_nans(X_Mean_G_brute)
X_Mean_D_no_nan_brute = remove_nans(X_Mean_D_brute)

GRF_G = GRF_G * 1e3
VERT_G = VERT_G * 1e3
GRF_D = GRF_D * 1e3
VERT_D = VERT_D * 1e3
EMG_D = EMG_D
EMG_G = EMG_G

taille_moy_gauche = np.count_nonzero(~np.isnan(Y_Mean_G))
taille_moy_droite = np.count_nonzero(~np.isnan(Y_Mean_D))
print("nombre de moyenne calculé jambe gauche", taille_moy_gauche)
print("nombre de moyenne calculé jambe droite ", taille_moy_droite)

from collections import deque


def moving_average(data, window_size):
    buf = deque(maxlen=window_size)
    ma = []
    for x in data:
        buf.append(x)
        ma.append(sum(buf) / len(buf))
    return ma


smooth_values = moving_average(Y_Mean_G_no_nan, 5)
print(len(smooth_values))
# === Création du graphe côte à côte ===
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)


def two_stride_average(raw_means):

    avg2 = []
    indices = []
    n = len(raw_means)
    # On itère par pas de 2
    for k in range(0, n - 1, 2):
        pair = raw_means[k], raw_means[k + 1]
        avg2.append(sum(pair) / 2.0)
        # indice de groupe : k//2 + 1
        t = X_Mean_G_no_nan[k]
        indices.append(t // 2 + 1)
    return indices, avg2


x_2, Y_Mean_G_2_strides = two_stride_average(Y_Mean_G_no_nan)
x_3 = np.arange(1, taille_moy_gauche, 2)


seuil_max_gauche = 175

# --- Jambe Gauche ---
# ax_left.hlines(seuil_max_gauche,xmin=0,xmax=len(EMG_G))
ax_left.plot(EMG_G, label="EMG Gauche", color="lightgray")
ax_left.plot(GRF_G, label="GRF Gauche", color="orange")
ax_left.plot(VERT_G, label="VERT Gauche", color="green")
if X_Mean_G.size > 0 and Y_Mean_G.size > 0:
    ax_left.plot(X_Mean_G_no_nan,Y_Mean_G_no_nan,label="Moyenne Push-Off Gauche",marker="o",color="black",)
    ax_left.plot(X_Mean_G_no_nan_brute,Y_Mean_G_no_nan_brute,label="Moyenne brute gauche ",marker='x',color="red")
    #ax_left.vlines(idx_debut_gauche, ymin=-400, ymax=1000, color="blue",
                   #linestyles="dashed", label="debut droite")
    #ax_left.vlines(idx_fin_gauche, ymin=-400, ymax=1000, color="black",
                   #linestyles="dashed",label="fin droite")



ax_left.set_title("Jambe Gauche")
ax_left.set_xlabel("Échantillons")
ax_left.set_ylabel("Amplitude")
ax_left.grid(True)
ax_left.legend()


seuil_max_droite = 134
# --- Jambe Droite ---
# ax_right.hlines(seuil_max_droite,xmin=0,xmax=len(EMG_D))
ax_right.plot(EMG_D, label="EMG Droite", color="lightgray")
ax_right.plot(GRF_D, label="GRF Droite", color="cyan")
ax_right.plot(VERT_D, label="VERT Droite", color="red")
if X_Mean_D.size > 0 and Y_Mean_D.size > 0:
    ax_right.plot(X_Mean_D_no_nan,Y_Mean_D_no_nan,label="Moyenne Push-Off Droite",marker="o",color="green",)
    ax_right.plot(X_Mean_D_no_nan_brute,Y_Mean_D_no_nan_brute,label="Moyenne brute droite",marker='x',color="black")
   # ax_right.vlines(idx_debut_droite, ymin=-400, ymax=1000, color="blue",
                   #linestyles="dashed", label="debut droite")
   # ax_right.vlines(idx_fin_droite, ymin=-400, ymax=1000, color="black",
                   #linestyles="dashed",label="fin droite")

ax_right.set_title("Jambe Droite")
ax_right.set_xlabel("Échantillons")
ax_right.grid(True)
ax_right.legend()

#ax_left.set_ylim(0,200)
#ax_right.set_ylim(0,200)

# === Moyennes affichées en console ===
moyenne_gauche = np.nanmean(Y_Mean_G_no_nan[10:-10])
moyenne_droite = np.nanmean(Y_Mean_D_no_nan[10:-10])
print("Seuil jambe gauche :", moyenne_gauche)
print("Seuil jambe droite :", moyenne_droite)

plt.tight_layout()
plt.show()
