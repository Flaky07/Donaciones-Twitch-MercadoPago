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
        gif_url = data.get("gif_url", "") 

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
            "external_reference": external_reference
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

            # Guardamos también el gif
            pendientes[preference_id] = {
                "mensaje": mensaje,
                "monto": monto,
                "usuario": usuario,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "external_reference": external_reference,
                "gif": gif_url 
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
        gif = data.get("gif", "")  # 👈 Se extrae el gif desde la data pendiente

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
                        "usuario": usuario,
                        "external_reference": external_reference,
                        "gif": gif  # 👈 Ahora se devuelve junto a la donación
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
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    :root {
      --primary-color: #6366f1;
      --secondary-color: #4f46e5;
      --text-color: #f8fafc;
      --bg-color: rgba(15, 23, 42, 0.95);
      --border-color: rgba(99, 102, 241, 0.3);
    }
    
    body {
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: 'Inter', sans-serif;
      color: var(--text-color);
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    
    .overlay-wrapper {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: center;
      padding-top: 5vh; /* espacio para el gif */
      box-sizing: border-box;
    }
    
    /* 📦 GIF centrado arriba */
    .alert-gif {
      max-width: 30vw;
      max-height: 30vh;
      width: auto;
      height: auto;
      margin-bottom: 20px;
      display: none; /* se activa desde JS */
    }
    
    /* 🟩 Alerta centrada debajo del GIF */
    .alert-container {
      background-color: var(--bg-color);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
      padding: 20px;
      width: 90%;
      max-width: 400px;
      display: flex;
      align-items: center;
      gap: 16px;
      opacity: 0;
      transition: opacity 0.4s ease, transform 0.4s ease;
      transform: translateY(40px);
    }
    
    .alert-container.visible {
      opacity: 1;
      transform: translateY(0);
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
    }
    
    .alert-amount {
      font-size: 22px;
      font-weight: 700;
      color: var(--primary-color);
    }
    
    .hidden {
      display: none;
    }
    
    /* 🔁 Responsive fallback para espacios más chicos en OBS */
    @media screen and (max-width: 500px) {
      .alert-gif {
        max-width: 60vw;
      }
    
      .alert-container {
        flex-direction: column;
        text-align: center;
        padding: 14px;
        gap: 12px;
      }
    
      .alert-icon {
        width: 36px;
        height: 36px;
      }
    
      .alert-message {
        font-size: 16px;
      }
    
      .alert-amount {
        font-size: 18px;
      }
    }
    </style>

    </head>
    <body>
    <div class="overlay-wrapper">
      <img id="gif" class="alert-gif" src="" alt="gif" style="display: none;">
      
      <div id="contenedor" class="alert-container">
        <div class="alert-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
               viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
            <path d="M4 2C2.8 3.7 2 5.7 2 8"></path>
            <path d="M22 8c0-2.3-.8-4.3-2-6"></path>
          </svg>
        </div>
        <div class="alert-content">
          <div id="mensaje" class="alert-message">Esperando mensaje...</div>
          <div id="monto" class="alert-amount">$0.00</div>
        </div>
      </div>
    </div>

    <script>
    let queue = [];
    let mostrando = false;
    let ultimaReferencia = "";

    async function verificarNuevoMensaje() {
      try {
        const res = await fetch('/ultimo-mensaje');
        const data = await res.json();
        if (data && data.external_reference && data.external_reference !== ultimaReferencia) {
          ultimaReferencia = data.external_reference;
          if (!queue.some(item => item.external_reference === data.external_reference)) {
            queue.push(data);
            if (!mostrando) mostrarSiguiente();
          }
        }
      } catch (e) {
        console.error("Error al verificar mensajes:", e);
      }
    }

    function mostrarSiguiente() {
      if (queue.length === 0) {
        mostrando = false;
        return;
      }

      mostrando = true;
      const data = queue.shift();
      mostrarMensaje(data);

      setTimeout(() => {
        ocultarMensaje();
        setTimeout(() => mostrarSiguiente(), 1000);
      }, 8000);
    }

    function mostrarMensaje(data) {
      const c = document.getElementById("contenedor");
      const gifEl = document.getElementById("gif");
    
      // Mensaje de texto
      document.getElementById("mensaje").textContent = `${data.usuario || "anónimo"} : ${data.mensaje}`;
      document.getElementById("monto").textContent = `$${parseFloat(data.monto).toFixed(2)}`;
    
      // URL del gif o fallback
      const gifURL = data.gif || "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTlzb21yczh0eGVkZ3U5NHdxc2MwODY5cDdyNzk3aGxydnh4YzFpMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IXnnnVD5kyKqXRhaCR/giphy.gif";
    
      gifEl.src = gifURL;
      gifEl.style.display = "block";  // Mostrar el gif
    
      c.classList.add("visible");     // Mostrar la alerta
    }
    
    function ocultarMensaje() {
      const gifEl = document.getElementById("gif");
    
      // Ocultar gif y alerta
      document.getElementById("contenedor").classList.remove("visible");
      gifEl.style.display = "none";
      gifEl.src = "";  // Limpieza para evitar gif congelado
    }


    setInterval(verificarNuevoMensaje, 3000);
    </script>
    </body>
    </html>
    """

@app.route("/api/donaciones")
def api_donaciones():
    if os.path.exists("donaciones.json"):
        with open("donaciones.json", "r", encoding="utf-8") as f:
            try:
                donaciones = json.load(f)
            except json.JSONDecodeError:
                donaciones = []
    else:
        donaciones = []
    return jsonify(donaciones[::-1]) 

@app.route("/historial")
def historial():
    if os.path.exists("donaciones.json"):
        with open("donaciones.json", "r", encoding="utf-8") as f:
            try:
                donaciones = json.load(f)
            except json.JSONDecodeError:
                donaciones = []
    else:
        donaciones = []

    filas = "\n".join(f"""
        <tr>
            <td>{d['fecha']}</td>
            <td>{d.get('usuario', 'anónimo')}</td>
            <td>{d['mensaje']}</td>
            <td class='amount'>${d['monto']}</td>
        </tr>
    """ for d in reversed(donaciones))

    total = sum(d["monto"] for d in donaciones)
    cantidad = len(donaciones)
    promedio = total / cantidad if cantidad > 0 else 0

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Historial de Donaciones</title>
<style>
    * {{
        margin: 0; padding: 0; box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    body {{
        background-color: #f5f5f5;
        color: #333;
        line-height: 1.6;
    }}
    .container {{
        width: 90%; max-width: 1200px;
        margin: 0 auto; padding: 20px;
    }}
    header {{
        background-color: #4CAF50;
        color: white;
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
    .subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
    .card {{
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-bottom: 2rem;
    }}
    h2 {{
        color: #4CAF50;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.5rem;
    }}
    .donation-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .donation-table th, .donation-table td {{
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid #f0f0f0;
    }}
    .donation-table th {{
        background-color: #f9f9f9;
        font-weight: 600;
    }}
    .donation-table tr:hover {{ background-color: #f5f5f5; }}
    .amount {{
        font-weight: 600;
        color: #4CAF50;
    }}
    .summary {{
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 2px solid #f0f0f0;
    }}
    .summary-item {{
        text-align: center;
        flex: 1;
    }}
    .summary-value {{
        font-size: 1.8rem;
        font-weight: 600;
        color: #4CAF50;
        margin-bottom: 0.5rem;
    }}
    .summary-label {{
        font-size: 0.9rem;
        color: #777;
    }}
    footer {{
        text-align: center;
        padding: 2rem 0;
        color: #777;
        font-size: 0.9rem;
    }}
    @media (max-width: 768px) {{
        .donation-table thead {{ display: none; }}
        .donation-table, .donation-table tbody, .donation-table tr, .donation-table td {{
            display: block;
            width: 100%;
        }}
        .donation-table tr {{
            margin-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .donation-table td {{
            text-align: right;
            padding-left: 50%;
            position: relative;
            border-bottom: 1px solid #f5f5f5;
        }}
        .donation-table td::before {{
            content: attr(data-label);
            position: absolute;
            left: 0;
            width: 50%;
            padding-left: 15px;
            font-weight: 600;
            text-align: left;
        }}
        .summary {{ flex-direction: column; }}
        .summary-item {{ margin-bottom: 1rem; }}
    }}
</style>
</head>
<body>
<header>
    <div class="container">
        <h1>Historial de Donaciones</h1>
        <p class="subtitle">Gracias por tu apoyo 💜</p>
    </div>
</header>
<main class="container">
    <section class="card">
        <h2>Donaciones Recientes</h2>
        <table class="donation-table">
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Usuario</th>
                    <th>Mensaje</th>
                    <th>Monto</th>
                </tr>
            </thead>
            <tbody id="donation-body">
                {filas}
            </tbody>
        </table>
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value" id="total">${total:.2f}</div>
                <div class="summary-label">Total Donado</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" id="count">{cantidad}</div>
                <div class="summary-label">Donaciones</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" id="average">${promedio:.2f}</div>
                <div class="summary-label">Promedio</div>
            </div>
        </div>
    </section>
</main>
<footer>
    <div class="container">
        <p>&copy; 2025 Donaciones • Proyecto Flaky</p>
    </div>
</footer>
<script>
    async function fetchDonations() {{
        try {{
            const res = await fetch('/api/donaciones');
            const data = await res.json();
            const body = document.getElementById("donation-body");
            body.innerHTML = "";

            let total = 0;

            data.forEach(d => {{
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${{d.fecha}}</td>
                    <td>${{d.usuario || "anónimo"}}</td>
                    <td>${{d.mensaje}}</td>
                    <td class="amount">$${{d.monto}}</td>
                `;
                body.appendChild(row);
                total += d.monto;
            }});

            document.getElementById("total").textContent = `$${{total.toFixed(2)}}`;
            document.getElementById("count").textContent = data.length;
            document.getElementById("average").textContent = data.length ? `$${{(total / data.length).toFixed(2)}}` : "$0.00";
        }} catch (err) {{
            console.error("Error loading donations:", err);
        }}
    }}

    fetchDonations();
    setInterval(fetchDonations, 3000);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)