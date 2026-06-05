# Sistema de Monitorización de Impresoras 3D

Sistema de detección de errores en impresión 3D usando visión por computadora e inteligencia artificial ejecutada en el navegador.

---

## 📋 Requisitos del Sistema

### Backend (Dispositivo con OctoPrint)
| Componente | Versión / Detalle |
|-----------|---------|
| Python | 3.10+ |
| FastAPI | Framework de la API REST y WebSockets |
| Uvicorn | Servidor ASGI para Python |
| OctoPrint | Cualquier versión con API habilitada |
| Cámara | Configurada en OctoPrint |

### Frontend (Cualquier dispositivo)
| Componente | Versión / Detalle |
|-----------|---------|
| Node.js | 18+ |
| Vue.js | 3.4+ (Composition API) |
| Vite | 6.0+ |
| Pinia | 2.1+ (Gestión de estado global) |
| PrimeVue | 4.0+ (Librería de componentes UI) |
| Navegador | Chrome, Firefox, Edge (moderno) |

### Inteligencia Artificial (Frontend)
| Componente | Descripción |
|------------|-------------|
| ONNX Runtime Web | El modelo de detección se ejecuta localmente en el navegador (`frontend/public/model/best.onnx`) |
| YOLOv8 | Arquitectura del modelo utilizado para la detección de objetos/errores |

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
         │ (Navegador Local)                    │ (Local Network)
         ▼                                      ▼
  ┌────────────┐                         ┌─────────────┐
  │ Inferencia │                         │  OctoPrint  │
  │ WebGL/WASM │                         │  + Cámara   │
  └────────────┘                         └─────────────┘
```

---

## 🔄 Funcionamiento y Flujo de Datos

El sistema está diseñado para ser ligero y eficiente, descargando el trabajo pesado (la inferencia de Inteligencia Artificial) en el dispositivo cliente (navegador web), de forma que el servidor backend (como una Raspberry Pi) solo se encargue de la comunicación y gestión básica con OctoPrint.

### Conexión Inicial

1. El usuario abre el Frontend en el navegador web.
2. El Frontend se conecta vía WebSocket a `ws://[IP_BACKEND]:8000/ws`.
3. El Backend valida y acepta la conexión WebSocket.
4. El Frontend descarga en memoria y prepara el modelo ONNX alojado localmente.

### Ciclo de Actualización (Tiempo Real)

**Backend (automático, cada 1 segundo):**
1. Consulta la API de OctoPrint (Estado actual, temperaturas de extrusor y cama, porcentaje de progreso, etc.).
2. Envía a todos los clientes conectados por WebSocket un paquete con el estado actualizado y metadatos de la impresión.

**Frontend (automático):**
1. Recibe el paquete WebSocket con el estado.
2. Captura el último fotograma (imagen) del stream de la cámara de OctoPrint.
3. Procesa el fotograma usando el modelo ONNX directamente en el navegador (`onnxruntime-web`) apoyándose en aceleración WebGL o WebAssembly.
4. Si se detectan errores en la impresión, dibuja *bounding boxes* (cajas delimitadoras) sobre el vídeo en tiempo real.
5. Actualiza la interfaz gráfica, mostrando gráficos de temperatura e historial, y alerta al usuario si hay un fallo detectado.

---

## 🧠 Modelo de Inteligencia Artificial (ONNX)

La aplicación utiliza un modelo de visión artificial que se ejecuta **directamente en el navegador** (Client-side Inference). Esto permite monitorizar impresoras 3D usando hardware de bajos recursos para el servidor, como una Raspberry Pi clásica que ejecuta OctoPrint.

1. **Ubicación del Modelo:**
   Asegúrate de colocar tu archivo de modelo exportado a formato ONNX en la siguiente ruta:
   `frontend/public/model/best.onnx`

2. **Exportar desde YOLOv8:**
   Si entrenas un modelo en YOLOv8 (`.pt`), expórtalo a ONNX antes de usarlo:
   ```bash
   yolo export model=best.pt format=onnx
   ```

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
   La primera vez que ejecutes el servidor, te pedirá por consola la **URL** y **API Key** de tu OctoPrint. Estos datos se validarán y se guardarán automáticamente en un archivo de entorno (`.env`).

### 2. Frontend (Vue.js + Vite)

1. Abre una terminal y navega a la carpeta del frontend:
   ```bash
   cd frontend
   ```

2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```

3. Asegúrate de tener el modelo ONNX en la ruta correcta (`public/model/best.onnx`).

---

## ▶️ Ejecución

Necesitas **dos terminales** abiertas simultáneamente (o ejecutar el backend como servicio en producción):

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
│   │   ├── main.py              # API + WebSocket (FastAPI)
│   │   ├── config.py            # Configuración general
│   │   ├── octoprint_client.py  # Interfaz con la API de OctoPrint
│   │   └── setup.py             # Gestión de claves y conexión inicial
│   ├── requirements.txt         # Dependencias Python
│   └── .env.back.template       # Plantilla env para backend
├── frontend/
│   ├── public/
│   │   └── model/
│   │       └── best.onnx        # Modelo de IA (YOLO exportado a ONNX)
│   ├── src/
│   │   ├── App.vue              # Shell principal de la interfaz
│   │   ├── main.js              # Punto de entrada Vue.js
│   │   ├── services/            # Servicios (Inferencia ONNX, API locales)
│   │   ├── stores/              # Estado global (Pinia: printer.js, user.js)
│   │   ├── views/               # Vistas y Páginas de la aplicación
│   │   └── assets/              # Recursos estáticos (estilos, logos)
│   └── package.json             # Dependencias Node.js
├── help.txt                     # Instrucciones adicionales
└── README.md                    # Este archivo
```
