from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://donaciones-twitch-mercado-pago.vercel.app"}})

ACCESS_TOKEN = "APP_USR-1882181410346504-040522-a1d392d93f2fdcfa3e2b6e87fa57ce50-290664751"  # Reemplazar con tu Access Token real de MercadoPago

@app.route("/")
def index():
    return "Backend Online"

@app.route("/crear-donacion", methods=["POST"])
def crear_donacion():
    try:
        data = request.get_json()
        monto = float(data["monto"])
        mensaje = data["mensaje"]

        preference_data = {
            "items": [
                {
                    "title": "Donación Twitch",
                    "description": "Donación Mariscal Infinito",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto
                }
            ],
            "auto_return": "approved",
            "back_urls": {
                "success": "https://donaciones-twitch-mercado-pago.vercel.app",
                "failure": "https://donaciones-twitch-mercado-pago.vercel.app",
                "pending": "https://donaciones-twitch-mercado-pago.vercel.app"
            },
            "external_reference": mensaje
        }

        res = requests.post(
            "https://api.mercadopago.com/checkout/preferences",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=preference_data
        )

        if res.status_code == 201:
            init_point = res.json()["init_point"]
            preference_id = res.json()["id"]

            pendientes = {}
            if os.path.exists("pendientes.json"):
                with open("pendientes.json", "r", encoding="utf-8") as f:
                    try:
                        pendientes = json.load(f)
                    except json.JSONDecodeError:
                        pendientes = {}

            pendientes[preference_id] = {
                "mensaje": mensaje,
                "monto": monto,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open("pendientes.json", "w", encoding="utf-8") as f:
                json.dump(pendientes, f, indent=4, ensure_ascii=False)

            return jsonify({"mensaje": "Preferencia creada", "url": init_point})

        return jsonify({"error": "Error en MercadoPago", "detalle": res.text}), 400

    except Exception as e:
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500

@app.route("/ultimo-mensaje")
def ultimo_mensaje():
    if os.path.exists("pendientes.json"):
        with open("pendientes.json", "r", encoding="utf-8") as f:
            try:
                pendientes = json.load(f)
                valores = list(pendientes.values())
                if valores:
                    return valores[-1]
            except json.JSONDecodeError:
                pass
    return {}

@app.route("/overlay")
def overlay():
    return """
    <html><head><meta charset="utf-8"><style>
    body {margin:0;padding:0;background:transparent;color:white;
    font-family:Arial,sans-serif;font-size:28px;display:flex;
    justify-content:center;align-items:center;height:100vh;}
    .mensaje {background-color:rgba(0,0,0,0.6);color:white;
    padding:20px;border-radius:10px;max-width:90%;opacity:0;
    transition:opacity 0.5s ease-in-out;}
    .visible {opacity:1;}
    </style></head><body>
    <div id="contenedor" class="mensaje"></div>
    <script>
    let ultimoMensaje="";let mostrando=false;
    async function verificarNuevoMensaje(){
        const res=await fetch('/ultimo-mensaje');
        const data=await res.json();
        if(data && data.mensaje && data.mensaje!==ultimoMensaje){
            ultimoMensaje=data.mensaje;mostrarMensaje(data);
        }
    }
    function mostrarMensaje(data){
        const contenedor=document.getElementById("contenedor");
        contenedor.innerHTML=`💬 <b>${data.mensaje}</b><br>💲 $${data.monto}`;
        contenedor.classList.add("visible");
        if(mostrando)return;mostrando=true;
        setTimeout(()=>{contenedor.classList.remove("visible");mostrando=false;},8000);
    }
    setInterval(verificarNuevoMensaje,3000);
    </script></body></html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
