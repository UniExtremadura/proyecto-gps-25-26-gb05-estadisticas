import os

from artistStats import getArtistStats
from roleChecker import RoleChecker
from userStats import getUserStats
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import redis
import json

load_dotenv()

r = redis.Redis(host=os.getenv("ESTADISTICAS_SERVICE_BASE_URL"), port=int(os.getenv("ESTADISTICAS_SERVICE_PORT")), decode_responses=True, username=(os.getenv("ESTADISTICAS_USER")), password=(os.getenv("ESTADISTICAS_PASSWORD")),)
app = FastAPI()

EXPIRACION = 600  # segundos (10 minutos)


@app.get("/artists/stats")
def artistStats(current_user: dict = Depends(RoleChecker(["artist"]))):
    key = f"artist_stats:{current_user['user'].id}"

    cached = r.get(key)
    if cached:
        return json.loads(cached)

    stats = getArtistStats(current_user["user"].id)
    r.set(key, json.dumps(stats), ex=EXPIRACION)

    return stats


@app.get("/users/stats")
def userStats(current_user: dict = Depends(RoleChecker(["user"]))):
    key = f"user_stats:{current_user['user'].id}"

    cached = r.get(key)
    if cached:
        return json.loads(cached)

    stats = getUserStats(current_user["user"].id)
    r.set(key, json.dumps(stats), ex=EXPIRACION)

    return stats