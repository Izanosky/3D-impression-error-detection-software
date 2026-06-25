// Servicio para el tratamiento de imagenes con nuestro modelo y ONNX
import * as ort from 'onnxruntime-web'

ort.env.wasm.wasmPaths = 'https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/'

let session = null
let isInitializing = false

const RUTA_MODELO = '/model/nano.onnx'
const DIMENSION = 512
const UMBRAL_CONFIANZA = 0.4

// Cargamos el modelo ONNX
export async function initSession() {
    if (session) return true
    if (isInitializing) return false // Con esto garantizamos que no se cargue el modelo dos veces

    isInitializing = true
    try {
        console.log('[Inference] Cargando modelo YOLOv8 ONNX...')
        session = await ort.InferenceSession.create(RUTA_MODELO, {
            executionProviders: ['wasm']
        }) // Con esto cargamos el modelo usando WebAssembly, que nos 
        // permite ejecutar el propio modelo en el navegador sin usar la GPU
        console.log('[Inference] Modelo cargado con éxito.')
        return true
    }
    catch (e) {
        console.error('[Inference] Error al cargar el modelo ONNX:', e)
        return false
    }
    finally {
        isInitializing = false
    }
}

// Procesamos la imagen
async function processImage(imagen) {
    return new Promise((resolve, reject) => {
        const img = new Image()
        img.crossOrigin = 'Anonymous'

        // Transformamos la imagen para que el modelo pueda procesarlas
        img.onload = () => {
            // Creamos un canvas y le dibujamos la imagen con el tamaño que espera el modelo
            const canvas = document.createElement('canvas')
            canvas.width = DIMENSION
            canvas.height = DIMENSION
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, DIMENSION, DIMENSION)

            // Obtenemos los pixeles de la imagen
            const pixels = ctx.getImageData(0, 0, DIMENSION, DIMENSION).data
            const totalPixels = DIMENSION * DIMENSION

            // Normalizamos la imagen y la transformamos a otro formato
            const float32Data = new Float32Array(3 * totalPixels)
            for (let i = 0; i < totalPixels; i++) {
                float32Data[i] = pixels[i * 4] / 255.0
                float32Data[totalPixels + i] = pixels[i * 4 + 1] / 255.0
                float32Data[2 * totalPixels + i] = pixels[i * 4 + 2] / 255.0
            }

            // Devolvemos el tensor para que el modelo pueda procesarlo
            resolve(new ort.Tensor('float32', float32Data, [1, 3, DIMENSION, DIMENSION]))
        }

        img.onerror = reject
        img.src = imagen
    })
}

// Ejecutamos el propio modelo sobre las imagenes para ver si hay algún error
export async function deteccionErrores(imagen) {
    if (!session) {
        await initSession() // Si no hay sesión, la cargamos
        if (!session) return { has_errors: false, max_confidence: 0 }
    }

    try {
        const tensor = await processImage(imagen) // Obtenemos el tensor de la imagen que le pasemos

        // ONNX define nombres para las entradas y las salidas. Lo que hacemos 
        // aqui es obtener el nombre de la entrada automaticamente del fichero .onnx
        const inputName = session.inputNames[0] // Nombre de la entrada que 
        const results = await session.run({ [inputName]: tensor }) // Ejecutamos el modelo

        const output = results[session.outputNames[0]] // Obtenemos la salida del modelo, al igual que haciamos con la entrada

        const numClasses = output.dims[1] - 4 // Obtenemos el número de clases
        const numAnchors = output.dims[2] // Obtenemos el número de anchors


        // Recorremos todos los anchors y todas las clases para obtener la máxima confianza
        let maxConfidence = 0
        for (let a = 0; a < numAnchors; a++) {
            for (let c = 0; c < numClasses; c++) {
                const prob = output.data[(4 + c) * numAnchors + a]
                if (prob > maxConfidence) maxConfidence = prob
            }
        }

        return { // Devolvemos el resultado de la inferencia
            has_errors: maxConfidence > UMBRAL_CONFIANZA,
            max_confidence: maxConfidence,
        }
    }
    catch (e) {
        console.error('[Inference] Fallo al ejecutar inferencia:', e)
        return { has_errors: false, max_confidence: 0 }
    }
}
