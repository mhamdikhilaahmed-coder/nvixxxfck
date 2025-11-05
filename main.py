import os
import subprocess
import time
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

# Lista de bots: carpeta y variable de token asociada
bots = [
    ("nuvix_ai", "NUVIX_AI_TOKEN"),
    ("nuvix_apps", "NUVIX_APPS_TOKEN"),
    ("nuvix_backup", "NUVIX_BACKUP_TOKEN"),
    ("nuvix_information", "NUVIX_INFORMATION_TOKEN"),
    ("nuvix_invoices", "NUVIX_INVOICES_TOKEN"),
    ("nuvix_machine", "NUVIX_MACHINE_TOKEN"),
    ("nuvix_management", "NUVIX_MANAGEMENT_TOKEN"),
    ("nuvix_sanctions", "NUVIX_SANCTIONS_TOKEN"),
    ("nuvix_system", "NUVIX_SYSTEM_TOKEN"),
    ("nuvix_tickets", "NUVIX_TICKETS_TOKEN"),
]

# Ejecutar cada bot
processes = []

print("🚀 Starting Nuvix Suite Pro v2...\n")

for folder, token_var in bots:
    token = os.getenv(token_var)
    if not token:
        print(f"⚠️ Skipping {folder} — no token found in .env for {token_var}")
        continue

    path = os.path.join(os.getcwd(), folder, "bot.py")
    print(f"✅ Launching {folder} ...")
    p = subprocess.Popen(["python", path])
    processes.append(p)
    time.sleep(2)  # Espera breve entre lanzamientos

print("\n✨ All available bots launched successfully.")
print("💡 Press CTRL + C to stop all bots.\n")

try:
    # Mantiene los procesos activos hasta que se detengan manualmente
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all bots...")
    for p in processes:
        p.terminate()
    print("✅ All bots stopped cleanly.")
