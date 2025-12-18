import os
import requests
from typing import List
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.supabaseAuth import gestor_token

load_dotenv()
url: str = os.getenv("SUPABASE_PROJECT_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)
USUARIOS_SERVICE_URL = os.getenv("USUARIOS_SERVICE_BASE_URL")

# Esquema de seguridad
security = HTTPBearer()

class RoleChecker:

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, creds: HTTPAuthorizationCredentials = Depends(security)):
        token = creds.credentials

        # 1. Validar Token en Supabase
        try:
            user_response = supabase.auth.get_user(token)
            user = user_response.user

            if not user:
                raise Exception("Usuario no encontrado")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self.allowed_roles:
            return {"user": user, "role": "user"}


        try:
            # Obtenemos el token de servicio
            service_token = gestor_token.get_token()

            # Llamada al microservicio de usuarios (requests library)
            response = requests.get(
                f"{USUARIOS_SERVICE_URL}/users/{user.id}",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                user_role = data.get("role")
            else:
                print(f"Error en microservicio usuarios: {response.status_code}")
                raise HTTPException(status_code=500)

        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return {"user": user, "role": user_role}