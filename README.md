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
- ✔️ Sistema reutilizable con parámetros dinámicos

---

## ⚙️ Configuración

### 🔐 Variables de entorno (solo backend)

Renombrá el archivo `.env.example` a `.env` y completá:

```env
MP_ACCESS_TOKEN=APP_USR-XXXXXXXXXXXXXXXX
```

> El token lo obtenés desde: https://www.mercadopago.com.ar/developers/panel/credentials

---

## 🧩 Estructura del proyecto

```
📁 twitch-donations/
├── app.py                  # Backend Flask
├── requirements.txt        # Dependencias para Render
├── .env.example            # Variables de entorno de ejemplo
├── public/                 # Archivos del frontend (para Vercel)
│   ├── index.html
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

5. Agregá una variable de entorno:

```
MP_ACCESS_TOKEN=TU_TOKEN_DE_MERCADOPAGO
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

## 💡 Personalización

### Cambiar canal de Twitch sin editar código

En el `index.html`, el canal se puede definir con un parámetro URL:

```
https://tudominio.vercel.app/?canal=nombre_de_tu_canal
```

---

## 📩 Créditos

Creado por [Flaky](https://github.com/Flaky07)  
Inspirado por streamers que 💜 su comunidad.

---

## 📃 Licencia

MIT — libre de uso y modificación.
```
