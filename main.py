import os
import subprocess
import time

# ✅ En Render no se necesita load_dotenv, las variables ya están en el entorno
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
else:
    print("⚙️ Using environment variables from Render...")

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

processes = []

print("🚀 Starting Nuvix Suite Pro v2...\n")

for folder, token_var in bots:
    token = os.getenv(token_var)
    if not token:
        print(f"⚠️ Skipping {folder} — no token found for {token_var}")
        continue

    path = os.path.join(os.getcwd(), folder, "bot.py")
    print(f"✅ Launching {folder} ...")
    p = subprocess.Popen(["python", path])
    processes.append(p)
    time.sleep(2)  # Espera breve entre lanzamientos

print("\n✨ All available bots launched successfully.")
print("💡 Press CTRL + C to stop all bots.\n")

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all bots...")
    for p in processes:
        p.terminate()
    print("✅ All bots stopped cleanly.")
