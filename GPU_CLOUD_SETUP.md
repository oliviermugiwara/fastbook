# 🚀 Utiliser un GPU cloud (Kaggle) depuis VS Code

Ton Mac (Intel, sans GPU NVIDIA ni Apple Silicon) ne peut pas entraîner de
modèles sur GPU en local. Cette procédure te permet de **coder dans VS Code**
tout en exécutant le calcul sur le **GPU gratuit de Kaggle** (Tesla T4).

Principe : Kaggle lance un serveur Jupyter sur son GPU → un tunnel public
(`cloudflared`) l'expose → VS Code s'y connecte comme « kernel distant ».

---

## 🔁 Procédure à refaire à chaque session (~2 min)

### 1. Démarrer un notebook Kaggle avec GPU
1. Va sur https://www.kaggle.com → `Create → New Notebook`.
2. Panneau de droite (icône ⋮ / *Session options*) :
   - **Accelerator** → `GPU T4 x2`
   - **Internet** → `On` ✅ (sinon le tunnel ne peut pas sortir)
3. (Une seule fois sur ton compte) **Phone Verification** dans *Settings*,
   obligatoire pour débloquer GPU + Internet.

### 2. Lancer le serveur + tunnel
1. Ouvre le fichier **`cloud_gpu_bootstrap.py`** (dans ce dépôt), copie tout.
2. Colle dans **une cellule** Kaggle → exécute (Shift+Entrée).
3. Attends ~30 s. En bas s'affiche :
   ```
   ==================== A COLLER DANS VS CODE ====================
   https://xxxx-xxxx-xxxx.trycloudflare.com/?token=fastbook
   ===============================================================
   ```
4. **Copie cette URL.** Laisse l'onglet Kaggle ouvert et actif.

### 3. Connecter VS Code
1. Ouvre ton notebook (ex. `01_intro.ipynb`).
2. En haut à droite : **Select Kernel**.
3. **Existing Jupyter Server...** (*Sélectionner un serveur Jupyter existant*).
4. **Colle l'URL** copiée → Entrée → accepte le nom → kernel **Python 3 (ipykernel)**.

### 4. Vérifier le GPU
Dans une cellule du notebook VS Code :
```python
import torch
print(torch.cuda.is_available())      # -> True
print(torch.cuda.get_device_name(0))  # -> Tesla T4
```

---

## ⚠️ À savoir

| Point | Détail |
|---|---|
| **Fichiers** | Le kernel tourne sur Kaggle : `untar_data(...)` télécharge dans `/kaggle/working`, **pas sur ton Mac**. Tes fichiers locaux ne sont pas visibles. |
| **URL change** | À chaque nouvelle session Kaggle, l'URL `trycloudflare` change. Relance la cellule (étape 2) → nouvelle URL → reconnecte VS Code. |
| **Session** | Kaggle coupe après ~20-40 min d'inactivité, 12 h max. Garde l'onglet actif. |
| **Quota GPU** | 30 h/semaine (compteur dans Settings). |
| **Port 8888** | Déjà pris par le Jupyter interne de Kaggle → on utilise **8899** (déjà géré par le script). |

---

## 🩺 Dépannage

**« URL non trouvée »** → relance simplement la cellule (le script est rejouable).

**404 dans VS Code / curl** → le tunnel pointe sur le mauvais serveur. Vérifie
que le script utilise bien `PORT = 8899` et `--ServerApp.base_url=/`.

**Tester le tunnel depuis le Mac** (remplace l'URL) :
```bash
curl -s -H "Authorization: token fastbook" \
  "https://xxxx.trycloudflare.com/api/status"
# doit renvoyer un JSON {"connections":...}
```

**Erreurs pip rouges** au lancement (`dask-cuda`, `numba-cuda`...) → **inoffensives**,
ce sont des conflits entre paquets CUDA pré-installés non utilisés.

---

## 💡 Alternative plus stable (si usage intensif)

Louer une VM GPU (vast.ai / Lambda ~0,2-0,5 $/h, ou crédits GCP/Paperspace)
et utiliser l'extension **Remote - SSH** de VS Code : pas de tunnel, persistant,
vrai environnement Linux. Plus confortable pour des entraînements longs/répétés.
