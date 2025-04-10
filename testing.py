from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

# Variable global para almacenar el último mensaje
ultimo_mensaje = {"mensaje": "", "monto": 0, "timestamp": 0}

@app.route("/overlay")
def overlay():
    return """
    <html><head><meta charset="utf-8"><style>
    :root {
      --primary-color: #6366f1;
      --secondary-color: #4f46e5;
      --text-color: #f8fafc;
      --bg-color: rgba(15, 23, 42, 0.85);
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
    
    /* Botón de prueba */
    .test-button {
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: var(--primary-color);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 10px 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    
    .test-button:hover {
      background-color: var(--secondary-color);
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
    
    <!-- Botón para probar la alerta -->
    <button id="testButton" class="test-button">Probar Alerta</button>
    
    <script>
    let ultimoMensaje = "";
    let timeoutId = null;
    
    async function verificarNuevoMensaje() {
      try {
        const res = await fetch('/ultimo-mensaje');
        const data = await res.json();
        if (data && data.mensaje && data.mensaje !== ultimoMensaje) {
          ultimoMensaje = data.mensaje;
          mostrarMensaje(data);
        }
      } catch (error) {
        console.error("Error al verificar mensajes:", error);
      }
    }
    
    function mostrarMensaje(data) {
      const contenedor = document.getElementById("contenedor");
      const mensajeEl = document.getElementById("mensaje");
      const montoEl = document.getElementById("monto");
      
      mensajeEl.textContent = data.mensaje;
      montoEl.textContent = `$${data.monto}`;
      
      contenedor.classList.add("visible");
      
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      timeoutId = setTimeout(() => {
        contenedor.classList.remove("visible");
      }, 8000);
    }
    
    // Botón de prueba
    document.getElementById("testButton").addEventListener("click", function() {
      fetch('/generar-mensaje-prueba');
    });
    
    setInterval(verificarNuevoMensaje, 3000);
    </script>
    </body></html>
    """

@app.route("/ultimo-mensaje")
def ultimo_mensaje_route():
    return jsonify(ultimo_mensaje)

@app.route("/generar-mensaje-prueba")
def generar_mensaje_prueba():
    global ultimo_mensaje
    mensajes = [
        "¡Nueva donación recibida!",
        "¡Gracias por tu apoyo!",
        "¡Nuevo seguidor!",
        "¡Mensaje especial!",
        "¡Suscripción activada!"
    ]
    
    ultimo_mensaje = {
        "mensaje": random.choice(mensajes),
        "monto": round(random.uniform(5, 1000), 2),
        "timestamp": time.time()
    }
    
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run( host="0.0.0.0", port=5000, debug=True)
