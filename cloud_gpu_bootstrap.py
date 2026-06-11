# =====================================================================
#  BOOTSTRAP GPU CLOUD -> VS CODE   (Kaggle ou Colab)
# ---------------------------------------------------------------------
#  Colle TOUT ce fichier dans UNE cellule du notebook cloud, execute,
#  puis copie l'URL affichee dans VS Code (Select Kernel > Existing
#  Jupyter Server). Relançable sans risque (nettoie l'ancien etat).
#
#  Pre-requis :
#    - Kaggle : panneau de droite > Accelerator = GPU  ET  Internet = On
#    - Colab  : Execution > Modifier le type d'execution > T4 GPU
#
#  Procedure complete : voir GPU_CLOUD_SETUP.md
# =====================================================================

import os, re, time, subprocess
from IPython import get_ipython

TOKEN = "fastbook"   # mot de passe du serveur (a recopier dans VS Code)
PORT  = 8899         # port dedie (8888 est pris par le Jupyter interne Kaggle)

# --- 1) Verifie le GPU ------------------------------------------------
gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                      "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
print("GPU :", gpu or "!!! AUCUN GPU -> active l'accelerateur dans les reglages du notebook")

# --- 2) Dependances (idempotent : ne reinstalle pas si deja la) -------
if not os.path.exists("cloudflared"):
    os.system("wget -q https://github.com/cloudflare/cloudflared/releases/latest/"
              "download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared")
os.system("pip -q install jupyterlab fastbook 2>/dev/null")

# --- 3) Nettoie tout etat precedent (rend la cellule rejouable) -------
os.system("pkill -f cloudflared 2>/dev/null")
os.system(f"pkill -f 'port={PORT}' 2>/dev/null")
time.sleep(2)

# --- 4) Lance Jupyter sur le port dedie -------------------------------
get_ipython().system_raw(
    f'jupyter lab --ip=0.0.0.0 --port={PORT} --no-browser '
    f'--ServerApp.base_url=/ --ServerApp.token="{TOKEN}" '
    f'--ServerApp.allow_origin="*" --ServerApp.disable_check_xsrf=True &'
)

# attend que le serveur reponde en local (max ~30 s)
for _ in range(30):
    time.sleep(1)
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        f"http://127.0.0.1:{PORT}/api/status"], capture_output=True, text=True)
    if r.stdout.strip() == "200":
        break
print("Jupyter local :", "OK (200)" if r.stdout.strip() == "200" else f"PAS PRET ({r.stdout})")

# --- 5) Ouvre le tunnel public ----------------------------------------
get_ipython().system_raw(f'./cloudflared tunnel --url http://localhost:{PORT} > clog.txt 2>&1 &')
url = None
for _ in range(20):
    time.sleep(1)
    m = re.search(r"https://[-\w]+\.trycloudflare\.com", open("clog.txt").read())
    if m:
        url = m.group(0)
        break

# --- 6) Affiche l'URL a coller dans VS Code ---------------------------
print("\n==================== A COLLER DANS VS CODE ====================")
print(f"{url}/?token={TOKEN}" if url else "URL non trouvee -> relance CETTE cellule")
print("===============================================================")
print("VS Code : Select Kernel > Existing Jupyter Server > colle l'URL ci-dessus")
