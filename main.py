from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import urllib.parse
import urllib.request
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# 🔥 Función síncrona (bloqueante) sin librerías externas
# ---------------------------------------------------
def request_sync(url, metodo, params):
    try:
        if metodo.lower() == "get":
            # Construir URL con parámetros
            url_completa = url + "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url_completa)
        else:
            # POST con form-data nativo
            data = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=data)

        # Hacer request
        with urllib.request.urlopen(req, timeout=20) as res:
            contenido = res.read().decode("utf-8")

            # Intentar JSON
            try:
                contenido = json.loads(contenido)
            except:
                pass

            return {
                "ok": True,
                "url": url,
                "status": res.status,
                "body": contenido
            }

    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}

# ---------------------------------------------------
# 🔥 Wrapper asíncrono (usa hilo para no bloquear FastAPI)
# ---------------------------------------------------
async def llamar_api(pr, dom, metodo, path, params):
    url = f"https://{pr}.{dom}{path}"
    return await asyncio.to_thread(request_sync, url, metodo, params)

# ---------------------------------------------------
# 🟡 PROXY PRINCIPAL MULTI API
# ---------------------------------------------------
@app.get("/api")
async def proxy(request: Request):
    q = dict(request.query_params)

    # -------- API 1 --------
    pr1 = q.pop("pr", None)
    dom1 = q.pop("dom", None)
    metodo1 = q.pop("metodo", "get")
    path1 = q.pop("parametros", "")

    if not pr1 or not dom1:
        return {"error": "Faltan pr y dom para API 1"}

    params_api1 = q.copy()

    # -------- API 2 --------
    pr2 = q.pop("pr2", None)
    dom2 = q.pop("dom2", None)
    metodo2 = q.pop("metodo2", "get")
    path2 = q.pop("parametros2", "")

    params_api2 = q.copy()

    tareas = [
        llamar_api(pr1, dom1, metodo1, path1, params_api1)
    ]

    if pr2 and dom2:
        tareas.append(llamar_api(pr2, dom2, metodo2, path2, params_api2))

    respuestas = await asyncio.gather(*tareas)

    if len(respuestas) == 1:
        return {"ok": True, "api_1": respuestas[0]}

    return {
        "ok": True,
        "api_1": respuestas[0],
        "api_2": respuestas[1]
    }
