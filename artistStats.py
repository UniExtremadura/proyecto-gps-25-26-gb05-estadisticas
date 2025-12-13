import os
import requests
from dotenv import load_dotenv
from supabaseAuth import gestor_token
from fastapi import HTTPException, status

def getArtistStats (uuid: str):
    load_dotenv()

    token:str = gestor_token.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    #TOTAL SEGUIDORES
    url = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/artists/{uuid}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        # TOTAL SEGUIDORES
        nFollowers = len(data.get("followers",[]))
        #print(nFollowers)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    #TOTAL INGRESOS, PRODUCTOS VENDIDOS, REPRODUCCIONES Y TIPOS VENDIDOS
    url = f"{os.getenv("COMPRAS_SERVICE_BASE_URL")}/orders"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        earn = 0
        totalPlays = 0

        totalCds = 0
        totalVinyls = 0
        totalCassettes = 0
        totalDigitals = 0

        totalSongs = 0
        totalAlbums = 0
        totalMerch = 0
        for order in data:
            items = order.get("items",[])

            for product in items:
                productUuid = product.get("uuid")
                type = product.get("type")
                priceItem = product.get("price")
                quantity = product.get("quantity")
                format = product.get("format")

                if type == "song":
                    urlType = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/songs/{productUuid}"
                elif type == "album":
                    urlType = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/albums/{productUuid}"
                elif type == "merch":
                    urlType = f"{os.getenv("CONTENIDOS_SERVICE_BASE_URL")}/products/{productUuid}"

                responseType = requests.get(urlType, headers=headers, timeout=5)
                responseData = responseType.json()

                if type == "song" or type == "album":
                    authorUuid = responseData.get("author").get("uuid")
                elif type == "merch":
                    authorUuid = responseData.get("reference").get("author").get("uuid")

                if uuid == authorUuid:
                    earn = earn + (priceItem * quantity)

                    if type == "song":
                        totalSongs += 1
                        totalPlays = totalPlays + responseData.get("plays")
                    if type == "album": totalAlbums += 1
                    if type == "merch": totalMerch += 1
                    if format == "cd": totalCds += 1
                    if format == "vinyl": totalVinyls += 1
                    if format == "cassette": totalCassettes += 1
                    if format == "digital": totalDigitals += 1

        return {
            "totalFollowers": nFollowers,
            "earn": earn,
            "totalPlays": totalPlays,
            "totalSongs": totalSongs,
            "totalAlbums": totalAlbums,
            "totalMerch": totalMerch,
            "totalCds": totalCds,
            "totalVinyls": totalVinyls,
            "totalCassettes": totalCassettes,
            "totalDigitals": totalDigitals,
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )