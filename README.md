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

### Servicios Externos
| Servicio | Descripción |
|----------|-------------|
| Roboflow | API de detección de errores (modelo `3d-printer-error-detection/5`) |

---

## 🏗️ Arquitectura

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│                 │◄──────────────────►│                 │
│    Frontend     │   ws://ip:8000/ws  │     Backend     │
│   (Vue.js)      │                    │   (FastAPI)     │
│                 │                    │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                              ▼                 ▼                 ▼
                       ┌──────────┐      ┌──────────┐      ┌──────────┐
                       │OctoPrint │      │  Cámara  │      │ Roboflow │
                       │   API    │      │          │      │   API    │
                       └──────────┘      └──────────┘      └──────────┘
```

---

## 🔄 Flujo de Datos

### Conexión Inicial

```
1. Usuario abre el Frontend en navegador
2. Frontend comprueba si hay IP del backend guardada (localStorage)
   ├─ NO → Muestra popup de configuración (obligatorio)
   └─ SI → Conecta WebSocket a ws://[IP]:8000/ws
3. Backend acepta conexión WebSocket
```

### Ciclo de Actualización (cada 3 segundos)

```
Backend (automático):
  │
  ├─► 1. Consulta OctoPrint API
  │      GET /api/printer  → Estado, temperaturas
  │      GET /api/job      → Progreso, archivo, tiempos
  │
  ├─► 2. Captura imagen de cámara
  │      GET /webcam/?action=snapshot
  │
  ├─► 3. Envía imagen a Roboflow
  │      POST → Imagen JPEG
  │      ◄── Respuesta JSON con predicciones
  │
  ├─► 4. Procesa imagen
  │      Dibuja bounding boxes sobre errores detectados
  │      Convierte a Base64
  │
  └─► 5. Envía a todos los clientes WebSocket
         {
           "type": "update",
           "data": {
             "status": { ... },
             "detections": { ... },
             "snapshot": "data:image/jpeg;base64,..."
           }
         }

Frontend:
  │
  └─► Recibe mensaje WebSocket
      Actualiza UI automáticamente (sin polling)
```

### Comandos del Usuario

```
Usuario pulsa "Pausar":
  │
  Frontend ──► WebSocket ──► {"action": "pause"}
                                    │
  Backend ◄─────────────────────────┘
      │
      └─► POST OctoPrint /api/job {"command": "pause"}
      │
      └─► Responde al Frontend
          {"type": "command_result", "action": "pause", "success": true}
```

---

## 📡 Formato de Mensajes WebSocket

### Backend → Frontend

**Actualización de estado:**
```json
{
  "type": "update",
  "data": {
    "status": {
      "connected": true,
      "state": "Printing",
      "temperatures": {
        "bed": {"actual": 60.0, "target": 60.0},
        "tool0": {"actual": 200.0, "target": 200.0}
      },
      "job": {
        "file": "modelo.gcode",
        "progress": 45.5,
        "time_elapsed": 3600,
        "time_remaining": 4400
      }
    },
    "detections": {
      "has_errors": true,
      "total_detections": 2,
      "classes": {
        "spaghetti": {"count": 1, "max_confidence": 0.85},
        "stringing": {"count": 1, "max_confidence": 0.72}
      }
    },
    "snapshot": "data:image/jpeg;base64,/9j/4AAQ..."
  }
}
```

**Resultado de comando:**
```json
{
  "type": "command_result",
  "action": "pause",
  "success": true
}
```

### Frontend → Backend

**Pausar impresión:**
```json
{"action": "pause"}
```

**Reanudar impresión:**
```json
{"action": "resume"}
```

---

## 🚀 Instalación

### Opción rápida: instalar todo a la vez

Desde la carpeta raíz del proyecto, ejecuta:

**Windows:**
```bash
setup_env.bat
```

**Linux / Raspberry Pi:**
```bash
chmod +x setup_env.sh backend/install.sh frontend/install.sh
bash setup_env.sh
```

Esto instalará tanto el backend como el frontend automáticamente.

---

### Opción manual: instalar por separado

#### 🔧 Backend (Python + FastAPI)

**Requisitos previos:**
- [Python 3.10](https://www.python.org/downloads/) instalado
  - **Windows:** Asegúrate de marcar "Add to PATH" durante la instalación
  - **Linux / Raspberry Pi:** `sudo apt install python3.10 python3.10-venv`

**Pasos:**

1. Abre una terminal y navega a la carpeta del backend:
   ```bash
   cd backend
   ```

2. Ejecuta el script de instalación:

   **Windows:**
   ```bash
   install.bat
   ```

   **Linux / Raspberry Pi:**
   ```bash
   chmod +x install.sh
   bash install.sh
   ```

   Esto creará un entorno virtual con Python 3.10 (`.venv`) e instalará todas las dependencias del archivo `requirements.txt`.

3. **(Alternativa manual)** Si prefieres hacerlo paso a paso:

   **Windows:**
   ```bash
   py -3.10 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Linux / Raspberry Pi:**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

> **⚠️ Nota Linux:** La carpeta `.venv` es **oculta** (empieza por punto). Usa `ls -a` para verla. Si no aparece con `ls` normal, no significa que no exista.

---

#### 🎨 Frontend (Vue.js + Vite)

**Requisitos previos:**
- [Node.js 18+](https://nodejs.org/) instalado
  - **Linux / Raspberry Pi:** `sudo apt install nodejs npm` o usa [nvm](https://github.com/nvm-sh/nvm)

**Pasos:**

1. Abre una terminal y navega a la carpeta del frontend:
   ```bash
   cd frontend
   ```

2. Ejecuta el script de instalación:

   **Windows:**
   ```bash
   install.bat
   ```

   **Linux / Raspberry Pi:**
   ```bash
   chmod +x install.sh
   bash install.sh
   ```

   Esto ejecutará `npm install` y descargará todas las dependencias definidas en `package.json`.

3. **(Alternativa manual)** Si prefieres hacerlo directamente:
   ```bash
   npm install
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

### 🔗 Primera conexión

1. Abre `http://localhost:5173` en tu navegador
2. La primera vez te pedirá la **dirección IP del backend** (si ejecutas todo en la misma máquina, introduce `localhost:8000`)
3. El sistema se conectará por WebSocket y empezará a mostrar datos en tiempo real

---

## 📁 Estructura de Archivos

```
TFG/
├── backend/
│   ├── app/
│   │   ├── main.py              # API + WebSocket
│   │   ├── config.py            # Configuración persistente
│   │   ├── octoprint_client.py  # Cliente OctoPrint
│   │   ├── roboflow_client.py   # Cliente Roboflow
│   │   └── image_processor.py   # Dibujado bounding boxes
│   ├── settings.json            # Configuración guardada
│   ├── requirements.txt
│   ├── install.bat              # Instalador Windows
│   └── install.sh               # Instalador Linux/Raspberry Pi
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Shell principal (header + router-view)
│   │   ├── main.js              # Punto de entrada (plugins)
│   │   ├── style.css            # Estilos globales
│   │   ├── router/
│   │   │   └── index.js         # Definición de rutas
│   │   ├── stores/
│   │   │   └── printer.js       # Estado global (Pinia)
│   │   ├── views/
│   │   │   ├── HomeView.vue     # Página de inicio
│   │   │   ├── MonitorView.vue  # Dashboard de monitorización
│   │   │   └── AboutView.vue    # Información del proyecto
│   │   └── components/
│   │       ├── AppHeader.vue    # Cabecera/navegación
│   │       ├── CameraView.vue   # Vista de cámara
│   │       ├── PrinterStatus.vue # Estado impresora
│   │       ├── ControlPanel.vue  # Botones control
│   │       └── SettingsDialog.vue # Configuración
│   ├── package.json
│   ├── install.bat              # Instalador Windows
│   └── install.sh               # Instalador Linux/Raspberry Pi
├── setup_env.bat                # Instalación completa (Windows)
├── setup_env.sh                 # Instalación completa (Linux/Raspberry Pi)
└── README.md
```

---

## ❓ Problemas Comunes (Linux / Raspberry Pi)

| Problema | Solución |
|----------|----------|
| `python3.10: command not found` | `sudo apt install python3.10 python3.10-venv` |
| No se crea el entorno virtual | Instalar paquete venv: `sudo apt install python3.10-venv` |
| No veo la carpeta `.venv` | Es oculta en Linux (empieza por `.`). Usa `ls -a` para verla |
| Quiero verificar que `.venv` existe | `test -d .venv && echo "EXISTE"` |
| Quiero buscar dónde se creó `.venv` | `find ~ -name ".venv" -type d` |
| `Permission denied` al ejecutar `.sh` | `chmod +x install.sh` o ejecutar con `bash install.sh` |
| `npm: command not found` | `sudo apt install nodejs npm` o usa [nvm](https://github.com/nvm-sh/nvm) |
