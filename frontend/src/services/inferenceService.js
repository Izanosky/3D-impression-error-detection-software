/**
 * Servicio de inferencia con ONNX Runtime Web.
 *
 * Carga un modelo YOLOv8 exportado en formato ONNX y lo ejecuta
 * directamente en el navegador usando WebAssembly. Recibe una imagen
 * en base64, la preprocesa a 640x640, ejecuta la inferencia y
 * devuelve si se detectaron errores de impresión.
 */
import * as ort from 'onnxruntime-web'

// Ruta CDN para los archivos WASM de ONNX Runtime
ort.env.wasm.wasmPaths = 'https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/'

// Estado del modelo
let session = null
let isInitializing = false

// Configuración del modelo YOLOv8
const MODEL_PATH = '/model/best.onnx'
const INPUT_DIM = 640                // Tamaño de entrada del modelo (640x640)
const CONFIDENCE_THRESHOLD = 0.4     // Umbral mínimo de confianza para considerar un error

/**
 * Carga el modelo ONNX en memoria. Solo se carga una vez.
 * Devuelve true si el modelo está listo, false si falló.
 */
export async function initSession() {
    if (session) return true
    if (isInitializing) return false

    isInitializing = true
    try {
        console.log('[Inference] Cargando modelo YOLOv8 ONNX...')
        session = await ort.InferenceSession.create(MODEL_PATH, {
            executionProviders: ['wasm']
        })
        console.log('[Inference] Modelo cargado con éxito.')
        return true
    } catch (e) {
        console.error('[Inference] Error al cargar el modelo ONNX:', e)
        return false
    } finally {
        isInitializing = false
    }
}

/**
 * Preprocesa una imagen base64 para el modelo YOLOv8:
 * 1. Carga la imagen en un canvas de 640x640
 * 2. Extrae los píxeles RGB
 * 3. Normaliza valores a [0, 1]
 * 4. Crea un tensor de forma [1, 3, 640, 640]
 */
async function preprocessImage(base64Image) {
    return new Promise((resolve, reject) => {
        const img = new Image()
        img.crossOrigin = 'Anonymous'

        img.onload = () => {
            // Dibujar imagen redimensionada en un canvas temporal
            const canvas = document.createElement('canvas')
            canvas.width = INPUT_DIM
            canvas.height = INPUT_DIM
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, INPUT_DIM, INPUT_DIM)

            // Extraer datos RGBA de los píxeles
            const pixels = ctx.getImageData(0, 0, INPUT_DIM, INPUT_DIM).data
            const totalPixels = INPUT_DIM * INPUT_DIM

            // Convertir a Float32 en formato CHW (Canales, Alto, Ancho)
            const float32Data = new Float32Array(3 * totalPixels)
            for (let i = 0; i < totalPixels; i++) {
                float32Data[i] = pixels[i * 4] / 255.0                          // Canal R
                float32Data[totalPixels + i] = pixels[i * 4 + 1] / 255.0        // Canal G
                float32Data[2 * totalPixels + i] = pixels[i * 4 + 2] / 255.0    // Canal B
            }

            resolve(new ort.Tensor('float32', float32Data, [1, 3, INPUT_DIM, INPUT_DIM]))
        }

        img.onerror = reject
        img.src = base64Image
    })
}

/**
 * Ejecuta la inferencia YOLOv8 sobre una imagen base64.
 * Devuelve { has_errors: bool, max_confidence: float }.
 */
export async function detectErrorsYolov8(base64Image) {
    // Asegurar que el modelo esté cargado
    if (!session) {
        await initSession()
        if (!session) return { has_errors: false, max_confidence: 0 }
    }

    try {
        // Preprocesar imagen → tensor
        const tensor = await preprocessImage(base64Image)

        // Ejecutar el modelo
        const inputName = session.inputNames[0]
        const results = await session.run({ [inputName]: tensor })

        // Leer la salida del modelo: [1, numFeatures, numAnchors]
        const output = results[session.outputNames[0]]
        const numClasses = output.dims[1] - 4     // Las primeras 4 son coordenadas de caja
        const numAnchors = output.dims[2]

        // Buscar la confianza máxima entre todas las detecciones
        let maxConfidence = 0
        for (let a = 0; a < numAnchors; a++) {
            for (let c = 0; c < numClasses; c++) {
                const prob = output.data[(4 + c) * numAnchors + a]
                if (prob > maxConfidence) maxConfidence = prob
            }
        }

        return {
            has_errors: maxConfidence > CONFIDENCE_THRESHOLD,
            max_confidence: maxConfidence,
        }
    } catch (e) {
        console.error('[Inference] Fallo al ejecutar inferencia:', e)
        return { has_errors: false, max_confidence: 0 }
    }
}
