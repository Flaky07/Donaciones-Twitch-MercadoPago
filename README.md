# 💜 Sistema de Donaciones para Streamers (Twitch + MercadoPago)

Este proyecto permite a cualquier streamer aceptar donaciones mediante **MercadoPago** y mostrar los mensajes en pantalla a través de **OBS**. Además, incluye un stream embebido de Twitch que se puede mostrar/minimizar dinámicamente.

---

## 🚀 Funcionalidades

- ✔️ Donaciones vía MercadoPago (checkout)
- ✔️ Visualización del mensaje del donante en OBS
- ✔️ Canal de Twitch embebido
- ✔️ Overlay personalizable
- ✔️ Backend listo para deploy en Render
- ✔️ Frontend listo para deploy en Vercel
- ✔️ Sistema reutilizable con configuración por archivo

---

## ⚙️ Configuración

### 🔐 Variables de entorno (solo backend)

Renombrá el archivo `.env.example` a `.env` y completá:

```env
MP_ACCESS_TOKEN=APP_USR-XXXXXXXXXXXXXXXX
VERCEL_APP=https://tusitio.vercel.app
```

> El token lo obtenés desde: https://www.mercadopago.com.ar/developers/panel/app

---

## 🧩 Estructura del proyecto

```
📁 twitch-donations/
├── app.py                  # Backend Flask
├── requirements.txt        # Dependencias para Render
├── .env.example            # Variables de entorno de ejemplo
├── public/                 # Archivos del frontend (para Vercel)
│   ├── index.html
│   ├── config.js           # ✅ configuración editable por cada streamer
│   └── static/styles/
│       └── styles.css
```

---

## ☁️ Deploy

### 🔸 Backend: Render

1. Subí este repositorio a GitHub
2. Creá un nuevo servicio en [https://render.com](https://render.com)
3. Elegí "Web Service"
4. En **Start Command**, poné:

```bash
gunicorn app:app
```

5. Agregá variables de entorno:

```
MP_ACCESS_TOKEN=TU_TOKEN_DE_MERCADOPAGO
VERCEL_APP=https://tudominio.vercel.app
```

6. Deploy 🚀

---

### 🔹 Frontend: Vercel

1. En [https://vercel.com](https://vercel.com), creá un nuevo proyecto
2. Seleccioná el mismo repositorio
3. En **Project Settings**, configurá:
   - **Root Directory**: `public/`

Listo, el frontend quedará online en algo como:  
```
https://donaciones-twitch.vercel.app
```

---

## 🧰 Configuración del Frontend

El archivo `config.js` contiene las variables editables del sitio. Modificalo así:

```js
// config.js
const TWITCH_CHANNEL = "tucanal_de_twitch";
const BACKEND_URL = "https://tu-backend.onrender.com";
```

> Esto permite personalizar sin tocar `index.html`, ideal para compartir el proyecto.

---

## 🎥 Twitch + OBS

Para mostrar los mensajes de donaciones en pantalla:

1. Abrí OBS
2. Agregá una fuente de navegador
3. Pegá la URL:

```
https://TU_BACKEND_RENDER.onrender.com/overlay
```

> Esto mostrará los mensajes en vivo cuando alguien done.

---

## 📩 Créditos

Creado por [Flaky](https://github.com/Flaky07)  
Inspirado por streamers que 💜 su comunidad.

---

## 📃 Licencia

MIT — libre de uso y modificación.
