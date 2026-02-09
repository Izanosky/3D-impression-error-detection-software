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

```bash
# Opción 1: Instalar todo
setup_env.bat

# Opción 2: Instalar por separado
cd backend && install.bat
cd frontend && install.bat
```

## ▶️ Ejecución

```bash
# Terminal 1 - Backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

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
│   └── install.bat
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Componente principal
│   │   └── components/
│   │       ├── CameraView.vue   # Vista de cámara
│   │       ├── PrinterStatus.vue # Estado impresora
│   │       ├── ControlPanel.vue  # Botones control
│   │       └── SettingsDialog.vue # Configuración
│   ├── package.json
│   └── install.bat
└── setup_env.bat
```
