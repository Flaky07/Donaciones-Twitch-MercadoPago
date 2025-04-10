from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os


ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN") # EDITAR VARIABLE DE ENTORNO EN RENDER.COM
VERCEL_APP = os.getenv("VERCEL_APP") # EDITAR VARIABLE DE ENTORNO EN RENDER.COM

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": VERCEL_APP}})

@app.route("/")
def index():
    return "Backend Online"

@app.route("/crear-donacion", methods=["POST"])
def crear_donacion():
    try:
        data = request.get_json()
        monto = float(data["monto"])
        usuario = data["usuario"]
        mensaje = data["mensaje"]

        # ✅ Generar external_reference único ANTES de enviarlo a MercadoPago
        external_reference = f"{mensaje}-{int(datetime.now().timestamp())}"

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
                "success": VERCEL_APP,
                "failure": VERCEL_APP,
                "pending": VERCEL_APP
            },
            "external_reference": external_reference  # 👈 ya corregido
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
                "usuario": usuario,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "external_reference": external_reference  # 👈 también guardado
            }

            with open("pendientes.json", "w", encoding="utf-8") as f:
                json.dump(pendientes, f, indent=4, ensure_ascii=False)

            return jsonify({"mensaje": "Preferencia creada", "url": init_point})

        return jsonify({"error": "Error en MercadoPago", "detalle": res.text}), 400

    except Exception as e:
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500


@app.route("/ultimo-mensaje")
def ultimo_mensaje():
    if not os.path.exists("pendientes.json"):
        return {}

    with open("pendientes.json", "r", encoding="utf-8") as f:
        try:
            pendientes = json.load(f)
        except json.JSONDecodeError:
            pendientes = {}

    for preference_id, data in list(pendientes.items()):
        mensaje = data.get("mensaje", "")
        monto = data.get("monto", 0)
        usuario = data.get("usuario", "anónimo")
        external_reference = data.get("external_reference", mensaje)


        res = requests.get(
            "https://api.mercadopago.com/v1/payments/search",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            params={"external_reference": external_reference}
        )

        if res.status_code == 200:
            pagos = res.json().get("results", [])
            for pago in pagos:
                print(f"[DEBUG] Verificando mensaje '{mensaje}' → status: {pago.get('status')}")
                if pago.get("status") == "approved":
                    fecha_pago = pago.get("date_approved", "fecha no disponible")

                    donaciones = []
                    if os.path.exists("donaciones.json"):
                        with open("donaciones.json", "r", encoding="utf-8") as df:
                            try:
                                donaciones = json.load(df)
                            except json.JSONDecodeError:
                                pass

                    nueva_donacion = {
                        "fecha": fecha_pago,
                        "monto": monto,
                        "mensaje": mensaje,
                        "usuario": usuario
                    }

                    donaciones.append(nueva_donacion)
                    with open("donaciones.json", "w", encoding="utf-8") as df:
                        json.dump(donaciones, df, indent=4, ensure_ascii=False)

                    pendientes.pop(preference_id)
                    with open("pendientes.json", "w", encoding="utf-8") as pf:
                        json.dump(pendientes, pf, indent=4, ensure_ascii=False)

                    return nueva_donacion

    return {}

@app.route("/overlay")
def overlay():
    return """
    <html><head><meta charset="utf-8"><style>
    :root {
      --primary-color: #6366f1;
      --secondary-color: #4f46e5;
      --text-color: #f8fafc;
      --bg-color: rgba(15, 23, 42, 0.96);
      --border-color: rgba(99, 102, 241, 0.3);
    }
    
    body {
      margin: 0;
      padding: 0;
      background: transparent;
      color: var(--text-color);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 16px;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      overflow: hidden;
    }
    
    .alert-container {
      background-color: var(--bg-color);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
      padding: 20px;
      max-width: 90%;
      width: 400px;
      display: flex;
      align-items: center;
      gap: 16px;
      transform: translateY(20px);
      opacity: 0;
      transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .alert-container.visible {
      transform: translateY(0);
      opacity: 1;
    }
    
    .alert-icon {
      background-color: var(--primary-color);
      border-radius: 50%;
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    
    .alert-content {
      flex: 1;
    }
    
    .alert-message {
      font-weight: 600;
      font-size: 18px;
      margin-bottom: 4px;
      line-height: 1.4;
    }
    
    .alert-amount {
      font-size: 22px;
      font-weight: 700;
      color: var(--primary-color);
    }
    </style></head>
    <body>
    <div id="contenedor" class="alert-container">
      <div class="alert-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
          <path d="M4 2C2.8 3.7 2 5.7 2 8"></path>
          <path d="M22 8c0-2.3-.8-4.3-2-6"></path>
        </svg>
      </div>
      <div class="alert-content">
        <div id="mensaje" class="alert-message"></div>
        <div id="monto" class="alert-amount"></div>
      </div>
    </div>
    <script>
    let queue = [];
    let mostrando = false;
    let historial = new Set();

    async function verificarNuevoMensaje() {
      try {
        const res = await fetch('/ultimo-mensaje');
        const data = await res.json();

        if (data && data.external_reference && !historial.has(data.external_reference)) {
          queue.push(data);
          historial.add(data.external_reference);
          procesarCola();
        }
      } catch (error) {
        console.error("Error al verificar mensajes:", error);
      }
    }

    function procesarCola() {
      if (mostrando || queue.length === 0) return;

      const data = queue.shift();
      mostrarMensaje(data);
    }

    function mostrarMensaje(data) {
      const contenedor = document.getElementById("contenedor");
      const mensajeEl = document.getElementById("mensaje");
      const montoEl = document.getElementById("monto");

      const usuario = data.usuario || "anónimo";
      mensajeEl.textContent = ` ${usuario} : ${data.mensaje}`;
      montoEl.textContent = `$${data.monto}`;

      contenedor.classList.add("visible");
      mostrando = true;

      setTimeout(() => {
        contenedor.classList.remove("visible");
        mostrando = false;
        setTimeout(procesarCola, 100); // Procesar siguiente
      }, 8000);
    }

    setInterval(verificarNuevoMensaje, 3000);
    </script>
    </body></html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)