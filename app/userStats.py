import os
import requests
from dotenv import load_dotenv
from app.supabaseAuth import gestor_token
from fastapi import HTTPException, status

def getUserStats (uuid: str):
    load_dotenv()

    token: str = gestor_token.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # TOTAL GASTADO
    url = f"{os.getenv("COMPRAS_SERVICE_BASE_URL")}/orders"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        totalGastado = 0
        for order in data:
            orderStatus = order.get("status")
            if orderStatus != 'cancelled' and orderStatus != 'pending_payment':
                orderUserUuid = order.get("userUuid")
                if orderUserUuid == uuid:
                    totalPrice = order.get("totalPrice")
                    totalGastado += totalPrice
                    # print(totalGastado)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # MINUTOS ESCUCHADOS TOTALES
    url = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/users/{uuid}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        totalEscuchado = 0
        items = data.get("library", [])
        for product in items:
            productType = product.get("type")
            if productType == 'Song':
                item = product.get("item")
                duration = item.get("duration")
                plays = item.get("plays")
                totalEscuchado += duration * plays
                # print(totalEscuchado)
            elif productType == 'Album':
                item = product.get("item")
                songs = item.get("songs", [])
                for song in songs:
                    duration = song.get("duration")
                    plays = song.get("plays")
                    totalEscuchado += duration * plays
                    # print(totalEscuchado)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # TOP 5 CANCIONES MÁS ESCUCHADAS
    url = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/users/{uuid}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        cancionesMasEscuchadas = {}
        items = data.get("library", [])
        for product in items:
            productType = product.get("type")
            if productType == 'Song':
                item = product.get("item")
                song_id = item.get("uuid")
                duration = item.get("duration")
                plays = item.get("plays")
                cancionesMasEscuchadas[song_id] = cancionesMasEscuchadas.get(song_id, {"song": item, "total": 0})
                cancionesMasEscuchadas[song_id]["total"] += duration * plays
            elif productType == 'Album':
                item = product.get("item")
                songs = item.get("songs", [])
                for song in songs:
                    song_id = song.get("uuid")
                    duration = song.get("duration")
                    plays = song.get("plays")
                    cancionesMasEscuchadas[song_id] = cancionesMasEscuchadas.get(song_id, {"song": song, "total": 0})
                    cancionesMasEscuchadas[song_id]["total"] += duration * plays
        top5 = sorted(cancionesMasEscuchadas.values(),key=lambda x: x["total"],reverse=True)[:5]
        cancionesMasEscuchadas = [c["song"] for c in top5]

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    #TOP 5 ARTISTAS MÁS ESCUCHADOS
    url = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/users/{uuid}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        artistasMasEscuchados = {}
        items = data.get("library", [])
        for product in items:
            productType = product.get("type")
            if productType == 'Song':
                item = product.get("item")
                duration = item.get("duration")
                plays = item.get("plays")
                artist = item.get("author")
                artistasMasEscuchados[artist] = (artistasMasEscuchados.get(artist, 0) + duration * plays)
            elif productType == 'Album':
                item = product.get("item")
                songs = item.get("songs", [])
                for song in songs:
                    duration = song.get("duration")
                    plays = song.get("plays")
                    artist = item.get("author")
                    artistasMasEscuchados[artist] = (artistasMasEscuchados.get(artist, 0) + duration * plays)
        top5 = sorted(artistasMasEscuchados.items(),key=lambda x: x[1],reverse=True)[:5]
        artistasMasEscuchados = [artista for artista, _ in top5]

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return {
        "totalGastado": totalGastado,
        "totalEscuchado": totalEscuchado,
        "cancionesMasEscuchadas": cancionesMasEscuchadas,
        "artistasMasEscuchados": artistasMasEscuchados,
    }