# utils/gmail.py
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Scopes necesarios para enviar correo
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    token_path = 'utils/token.json'
    creds_path = 'utils/credentials.json'

    # Cargar token ya generado
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        # Autenticación inicial manual
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        # Guardar el token para próximas veces
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email_via_gmail_api(to, subject, message_text):
    service = get_gmail_service()

    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    body = {'raw': raw}
    try:
        send_message = service.users().messages().send(userId='me', body=body).execute()
        return send_message
    except Exception as e:
        print("Error enviando correo:", e)
        return None