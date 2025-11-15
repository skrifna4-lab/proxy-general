from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# --------------------------------
# 🔓 CORS PARA TODOS LOS DOMINIOS
# --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # permitir cualquier dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def proxy(request: Request):
    params = dict(request.query_params)

    # Extraer parámetros propios del proxy
    pr = params.pop("pr", None)              # ejemplo: reniec
    dom = params.pop("dom", None)            # ejemplo: skrifna.uk
    metodo = params.pop("metodo", "get")     # GET o POST
    path = params.pop("parametros", "")      # ejemplo: /buscar

    if not pr or not dom:
        return {"error": "Faltan parámetros 'pr' y 'dom'"}

    # Construcción de la URL destino
    url = f"https://{pr}.{dom}{path}"

    # Cliente HTTP asíncrono
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            if metodo.lower() == "get":
                res = await client.get(url, params=params)
            else:
                res = await client.post(url, data=params)

        except httpx.RequestError as e:
            return {"error": f"Error al conectar con {url}", "detalle": str(e)}

    # Intentar parsear JSON, si no, devolver texto crudo
    try:
        contenido = res.json()
    except Exception:
        contenido = res.text

    return {
        "ok": True,
        "url_destino": url,
        "enviado": params,
        "status_code": res.status_code,
        "contenido": contenido
    }
