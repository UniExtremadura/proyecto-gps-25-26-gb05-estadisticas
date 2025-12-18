import math
import os

import interface
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_PROJECT_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
admin_email: str = os.getenv("ADMIN_ESTADISTICAS_CORREO")
admin_pass: str = os.getenv("ADMIN_ESTADISTICAS_PASSWORD")

supabase: Client = create_client(url, key)

class DataToken:

    accessToken: str
    refreshToken: str
    expiresAt: int

    def __init__(self):
        """Constructor"""
        self.accessToken = ""
        self.refreshToken = ""
        self.expiresAt = 0

        self.refresh_token()

    def refresh_token(self):
        # Hacemos el login
        session = supabase.auth.sign_in_with_password({
            "email": admin_email,
            "password": admin_pass
        })
        # Extraemos el token JWT de la sesión
        self.accessToken = session.session.access_token
        self.refreshToken = session.session.refresh_token
        self.expiresAt = session.session.expires_at


    def is_token_expiring(self) -> bool:
        currentTime = math.floor(int(datetime.now().timestamp()) / 1000)
        timeUntilExpire = self.expiresAt - currentTime
        return timeUntilExpire < 60

    def get_token(self):
        if self.is_token_expiring(): self.refresh_token()
        return self.accessToken

gestor_token = DataToken()