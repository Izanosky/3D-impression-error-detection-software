# Sistema de Monitorización de Impresoras 3D

Sistema de detección de errores en impresión 3D usando visión por computadora.

---

## 📋 Requisitos del Sistema

### Backend (Dispositivo con OctoPrint)
| Requisito | Versión |
|-----------|---------|
| Python | 3.10+ |
| OctoPrint | Cualquier versión con API habilitada |
| Cámara | Configurada en OctoPrint |

### Frontend (Cualquier dispositivo)
| Requisito | Versión |
|-----------|---------|
| Node.js | 18+ |
| Navegador | Chrome, Firefox, Edge (moderno) |
| Firebase | Proyecto configurado (Auth, Firestore, Storage) |

### Inteligencia Artificial (Frontend)
| Componente | Descripción |
|------------|-------------|
| ONNX Runtime | El modelo de detección se ejecuta localmente en el navegador (`frontend/public/model/best.onnx`) |

---

## 🏗️ Arquitectura

```text
┌─────────────────┐     WebSocket      ┌─────────────────┐
│                 │◄──────────────────►│                 │
│    Frontend     │   ws://ip:8000/ws  │     Backend     │
│   (Vue.js)      │                    │   (FastAPI)     │
│  [ ONNX IA ]    │                    │                 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ (Cloud)                              │ (Local Network)
         ▼                                      ▼
  ┌────────────┐                         ┌─────────────┐
  │  Firebase  │                         │  OctoPrint  │
  │ (DB/Auth)  │                         │  + Cámara   │
  └────────────┘                         └─────────────┘
```

---

## 🔄 Flujo de Datos

### Conexión Inicial

1. Usuario abre el Frontend en navegador y se autentica vía Firebase.
2. Frontend conecta vía WebSocket a `ws://[IP_BACKEND]:8000/ws`.
3. Backend acepta la conexión WebSocket.

### Ciclo de Actualización (cada 1 segundo)

**Backend (automático):**
1. Consulta OctoPrint API (Estado, temperaturas, progreso).
2. Envía a todos los clientes WebSocket el estado y datos de impresión.

**Frontend:**
1. Recibe mensaje WebSocket con el estado.
2. Procesa la última imagen/stream de la cámara usando el modelo ONNX en el navegador (`onnxruntime-web`).
3. Dibuja bounding boxes sobre errores detectados.
4. Actualiza la UI y, si es necesario, alerta al usuario o detiene la impresión.

---

## 🧠 Modelo de Inteligencia Artificial (ONNX)

La aplicación utiliza un modelo de visión artificial que ahora se ejecuta **directamente en el navegador** (Client-side Inference) para liberar carga del servidor, permitiendo usar hardware menos potente (como una Raspberry Pi) para el backend.

1. **Ubicación del Modelo:**
   Asegúrate de colocar tu archivo de modelo exportado a formato ONNX en la siguiente ruta:
   `frontend/public/model/best.onnx`

2. **Exportar desde YOLOv8:**
   Si entrenas un modelo en YOLOv8 (`.pt`), expórtalo a ONNX antes de usarlo:
   `yolo export model=best.pt format=onnx`

---

## 🚀 Instalación y Configuración

### 1. Backend (Python + FastAPI)

1. Abre una terminal y navega a la carpeta del backend:
   ```bash
   cd backend
   ```

2. Crea y activa un entorno virtual:
   **Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   **Linux / Raspberry Pi:**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuración inicial de OctoPrint**:
   La primera vez que ejecutes el servidor, te pedirá por consola la **URL** y **API Key** de tu OctoPrint. Estos datos se validarán y se guardarán automáticamente en `.env.back.template`.

### 2. Frontend (Vue.js + Vite + Firebase)

1. Abre una terminal y navega a la carpeta del frontend:
   ```bash
   cd frontend
   ```

2. Instala las dependencias:
   ```bash
   npm install
   ```

3. **Configura Firebase**:
   Crea un archivo `.env` en la raíz de la carpeta `frontend` y añade tus credenciales de Firebase:
   ```env
   VITE_FIREBASE_API_KEY=tu_api_key
   VITE_FIREBASE_AUTH_DOMAIN=tu_auth_domain
   VITE_FIREBASE_PROJECT_ID=tu_project_id
   VITE_FIREBASE_STORAGE_BUCKET=tu_storage_bucket
   VITE_FIREBASE_MESSAGING_SENDER_ID=tu_messaging_sender_id
   VITE_FIREBASE_APP_ID=tu_app_id
   ```

---

## ▶️ Ejecución

Necesitas **dos terminales** abiertas simultáneamente:

### Terminal 1 — Backend

**Windows:**
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Linux / Raspberry Pi:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000`.

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

---

## 📁 Estructura de Archivos

```text
TFG/
├── backend/
│   ├── app/
│   │   ├── main.py              # API + WebSocket
│   │   ├── config.py            # Configuración
│   │   ├── octoprint_client.py  # Cliente OctoPrint
│   │   └── setup.py             # Gestión de claves/conexión inicial
│   ├── requirements.txt
│   └── .env.back.template       # Plantilla env para backend
├── frontend/
│   ├── public/
│   │   └── model/
│   │       └── best.onnx        # Modelo de IA (YOLO exportado)
│   ├── src/
│   │   ├── App.vue              # Shell principal
│   │   ├── main.js              # Punto de entrada
│   │   ├── services/            # Servicios (Firebase, Inferencia ONNX, Auth)
│   │   ├── stores/              # Estado global (Pinia)
│   │   ├── views/               # Páginas
│   │   └── assets/              # Recursos estáticos
│   └── package.json
├── help.txt
└── README.md
```
