
import os
import shutil
import datetime
import paramiko
import logging
import requests

# 🔹 Configurações do Backup 🔹
FONTE = "/etc"  # Pasta a ser copiada
DESTINO_LOCAL = "/backup"
SERVIDOR_SFTP = "192.168.1.100"
USUARIO_SFTP = "admin"
SENHA_SFTP = "senha123"
DESTINO_REMOTO = "/home/backupserver/"

# 🔹 Configurações do Telegram 🔹
TOKEN_TELEGRAM = "SEU_BOT_TOKEN"
CHAT_ID = "SEU_CHAT_ID"

# 🔹 Configuração de Logs 🔹
logging.basicConfig(filename="backup.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Função para enviar alertas via Telegram
def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Erro ao enviar alerta no Telegram: {e}")

# Função para criar backup
def criar_backup():
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_file = f"{DESTINO_LOCAL}/backup_{data_atual}.zip"

    # Criando backup local
    try:
        shutil.make_archive(backup_file.replace(".zip", ""), 'zip', FONTE)
        logging.info(f"Backup criado com sucesso: {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"Erro ao criar backup: {e}")
        enviar_alerta(f"❌ Erro ao criar backup: {e}")
        return None

# Função para enviar backup via SFTP
def enviar_backup_sftp(backup_file):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVIDOR_SFTP, username=USUARIO_SFTP, password=SENHA_SFTP)
        
        sftp = ssh.open_sftp()
        sftp.put(backup_file, DESTINO_REMOTO + os.path.basename(backup_file))
        sftp.close()
        ssh.close()
        
        logging.info("✅ Backup enviado com sucesso para o servidor remoto!")
        enviar_alerta(f"✅ Backup enviado com sucesso: {backup_file}")

    except Exception as e:
        logging.error(f"❌ Erro ao enviar backup via SFTP: {e}")
        enviar_alerta(f"❌ Erro ao enviar backup: {e}")

# Executando backup
if __name__ == "__main__":
    arquivo_backup = criar_backup()
    if arquivo_backup:
        enviar_backup_sftp(arquivo_backup)



