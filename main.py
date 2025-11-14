from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.get("/api")
async def proxy(request: Request):
    params = dict(request.query_params)

    # Extraer parámetros
    pr = params.pop("pr", None)          # subdominio base -> reniec
    dom = params.pop("dom", None)        # dominio -> skrifna.uk
    metodo = params.pop("metodo", "get") # GET o POST
    path = params.pop("parametros", "")  # ruta tipo /buscar

    if not pr or not dom:
        return {"error": "Faltan parámetros pr y dom"}

    # Construir URL destino
    url = f"https://{pr}.{dom}{path}"

    # Cliente HTTP async
    async with httpx.AsyncClient() as client:
        if metodo.lower() == "get":
            r = await client.get(url, params=params)
        else:
            r = await client.post(url, json=params)

    # Retornar datos tal cual → sin CORS bloqueado
    return {
        "ok": True,
        "url_usada": url,
        "respuesta": r.json() if "application/json" in r.headers.get("content-type", "") else r.text
    }
