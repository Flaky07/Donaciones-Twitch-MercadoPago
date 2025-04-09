from flask import Flask, request, redirect, render_template
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

ACCESS_TOKEN = "APP_USR-.....-75432"  # Reemplazar con su Acces Token de MercadoPago

@app.route("/")
def index():
    return render_template("donar.html")

@app.route("/crear-donacion", methods=["POST"])
def crear_donacion():
    try:
        monto = float(request.form['monto'])
        mensaje = request.form['mensaje']

        preference_data = {
            "items": [
                {
                    "title": "Donación Twitch",
                    "description": "Donación Mariscal Infinito",  #EDITAR CON SU NOMBRE
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto
                }
            ],
            "auto_return": "approved",
            "back_urls": {
                "success": "http://localhost:5000/resultado",
                "failure": "http://localhost:5000",
                "pending": "http://localhost:5000"
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

            # Guardar mensaje temporalmente
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

            return redirect(init_point)
        else:
            return f"<h2>❌ Error al crear preferencia:</h2><pre>{res.text}</pre>"

    except Exception as e:
        return f"<h2>⚠️ Error interno:</h2><pre>{str(e)}</pre>"

@app.route("/resultado")
def resultado():
    preference_id = request.args.get("preference_id")
    if not preference_id:
        return "<h2>❌ No se encontró el preference_id</h2>"

    # Cargar mensaje/monto guardado previamente
    mensaje = "(sin mensaje)"
    monto = 0
    fecha = ""

    pendientes_file = "pendientes.json"
    donaciones_file = "donaciones.json"

    if os.path.exists(pendientes_file):
        with open(pendientes_file, "r", encoding="utf-8") as f:
            try:
                pendientes = json.load(f)
                datos = pendientes.get(preference_id)
                if datos:
                    mensaje = datos.get("mensaje", mensaje)
                    monto = datos.get("monto", 0)
                    fecha = datos.get("fecha", "")
            except json.JSONDecodeError:
                pendientes = {}

    # Buscar pagos reales con ese mensaje
    res = requests.get(
        "https://api.mercadopago.com/v1/payments/search",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        params={"external_reference": mensaje}
    )

    if res.status_code == 200:
        resultados = res.json().get("results", [])

        for pago in resultados:
            if pago.get("status") == "approved":
                email = pago.get("payer", {}).get("email", "desconocido")
                fecha_pago = pago.get("date_approved", "fecha no disponible")

                # 🔸 Guardar en donaciones.json
                donaciones = []
                if os.path.exists(donaciones_file):
                    with open(donaciones_file, "r", encoding="utf-8") as f:
                        try:
                            donaciones = json.load(f)
                        except json.JSONDecodeError:
                            donaciones = []

                nueva_donacion = {
                    "fecha": fecha_pago,
                    "monto": monto,
                    "email": email,
                    "mensaje": mensaje
                }

                donaciones.append(nueva_donacion)

                with open(donaciones_file, "w", encoding="utf-8") as f:
                    json.dump(donaciones, f, indent=4, ensure_ascii=False)

                if preference_id in pendientes:
                    pendientes.pop(preference_id)
                    with open(pendientes_file, "w", encoding="utf-8") as f:
                        json.dump(pendientes, f, indent=4, ensure_ascii=False)

                # EDITAR CON SU CANAL DE TWITCH LINEA 155
                return f"""
                    <h2>✅ ¡Gracias por tu donación!</h2>
                    <p><b>Monto:</b> ${monto}</p>
                    <p><b>Mensaje:</b> {mensaje}</p>
                    <p><b>Fecha:</b> {fecha_pago}</p>
                    <p><b>Mail del donante:</b> {email}</p>
                    <script>
                        setTimeout(function() {{
                            window.location.href = "https://www.twitch.tv/elmariscal_infinito";
                        }}, 7000);
                    </script>
                """

        return "<h2>⏳ Aún no se confirmó tu pago</h2><p>Revisá más tarde si fue aprobado.</p>"
    else:
        return f"<h2>❌ Error al buscar pagos:</h2><pre>{res.text}</pre>"
    

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
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                margin: 0;
                padding: 0;
                background: transparent;
                color: white;
                font-family: Arial, sans-serif;
                font-size: 28px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .mensaje {
                background-color: rgba(0, 0, 0, 0.6);
                color: white;
                padding: 20px;
                border-radius: 10px;
                max-width: 90%;
                opacity: 0;
                transition: opacity 0.5s ease-in-out;
            }

            .visible {
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <div id="contenedor" class="mensaje"></div>

        <script>
            let ultimoMensaje = "";
            let mostrando = false;

            async function verificarNuevoMensaje() {
                const res = await fetch('/ultimo-mensaje');
                const data = await res.json();

                if (data && data.mensaje && data.mensaje !== ultimoMensaje) {
                    ultimoMensaje = data.mensaje;
                    mostrarMensaje(data);
                }
            }

            function mostrarMensaje(data) {
                const contenedor = document.getElementById("contenedor");
                contenedor.innerHTML = `
                    💬 <b>${data.mensaje}</b><br>
                        💲 $${data.monto}
                `;
                contenedor.classList.add("visible");

                if (mostrando) return;
                mostrando = true;

                setTimeout(() => {
                    contenedor.classList.remove("visible");
                    mostrando = false;
                }, 8000); // Visible durante 8 segundos
            }

            setInterval(verificarNuevoMensaje, 3000); // Chequea cada 3 segundos
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
