# 💜 Sistema de Donaciones para Streamers (Twitch + MercadoPago + OBS)

Este proyecto permite a cualquier **streamer** aceptar **donaciones a través de MercadoPago**, visualizar los mensajes en vivo con **OBS**, e integrar su canal de **Twitch embebido**. Totalmente reutilizable y desplegable con solo editar variables de entorno.

---

## 🚀 Funcionalidades

- ✔️ Checkout de MercadoPago
- ✔️ Mensaje en pantalla vía OBS
- ✔️ Canal de Twitch embebido
- ✔️ Frontend desplegable en Vercel
- ✔️ Backend en Render
- ✔️ Parametrizable por variables de entorno
- ✔️ 100% reutilizable para cualquier streamer

---

## 🧩 Estructura del proyecto

```
📦 twitch-donations
├── 📁 api/                     # Serverless function para exponer ENV en el frontend
│   └── config.js
├── 📁 public/                  # Frontend estático para Vercel
│   ├── index.html
│   ├── vercel.json            # Reescribe /config.js a /api/config.js
│   └── static/styles/
│       └── styles.css
├── app.py                     # Backend Flask para Render
├── .env.example               # Variables para Render
├── requirements.txt           # Dependencias de Python
└── README.md
```

---

## ⚙️ Configuración

### 🔐 Variables de entorno

#### 📦 Backend (Render)

```env
MP_ACCESS_TOKEN=APP_USR-XXXXXXXXXXXXXXXX
VERCEL_APP=https://TU_FRONTEND.vercel.app
```

> Este archivo **no se sube** a GitHub. En producción, se agregan directamente desde Render (Settings > Environment).

#### 🌐 Frontend (Vercel)

En [https://vercel.com](https://vercel.com):

1. Ir al proyecto > `Settings > Environment Variables`
2. Agregar:

```
TWITCH_CHANNEL=nombre_de_tu_canal
BACKEND_URL=https://backend-donaciones.onrender.com
```

![Vercel Variables](https://drive.google.com/uc?id=1rAvI5D-GB014HHL0twNs1NYdPzohgCwn)

---

## ☁️ Deploy en producción

### 🔹 Frontend en Vercel

1. Hacé un **fork** o cloná este repo
2. Subilo a tu GitHub
3. En Vercel, seleccioná **"Import Project"**
4. En **Project Settings**:
   - Root Directory: `public/`
5. Definí las variables de entorno (como se explicó arriba)

> Tu frontend quedará en algo como: `https://donaciones-twitch.vercel.app`

---

### 🔸 Backend en Render

1. Ingresá a [https://render.com](https://render.com)
2. Nuevo servicio tipo `Web Service`
3. Conectá el repositorio
4. Start Command:

```bash
gunicorn app:app
```

5. Agregá las variables de entorno:

```
MP_ACCESS_TOKEN=APP_USR-xxxx
VERCEL_APP=https://donaciones-twitch.vercel.app
```
![Render Variables](https://drive.google.com/uc?id=18VnDQ2gHRHnyYXSxa_PwaC-hZlA271O8)



---

## 🎯 Uso en OBS

Para mostrar los mensajes en pantalla:

1. Abrí **OBS Studio**
2. Agregá una nueva fuente de navegador
3. Borrar el CSS Default que añade OBS
4. Pegá esta URL:

```
https://TU_BACKEND_RENDER.onrender.com/overlay
```

> Los mensajes de donación aparecerán automáticamente en pantalla.


## 🙌 Créditos

Creado por [Flaky](https://github.com/Flaky07)  
Inspirado por streamers que 💜 su comunidad.

---

## 📝 Licencia

MIT - libre para usar, modificar y compartir.
