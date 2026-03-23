import * as ort from 'onnxruntime-web';

// Configurar paths para WebAssembly
ort.env.wasm.wasmPaths = 'https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/';

let session = null;
let isInitializing = false;

// Configuración YOLOv8
const MODEL_PATH = '/model/best.onnx';
const INPUT_DIM = 640;
const CONFIDENCE_THRESHOLD = 0.4;

export async function initSession() {
    if (session) return true;
    if (isInitializing) return false;
    
    isInitializing = true;
    try {
        console.log('[Inference] Cargando modelo YOLOv8 ONNX...');
        session = await ort.InferenceSession.create(MODEL_PATH, {
            executionProviders: ['wasm']
        });
        console.log('[Inference] Modelo cargado con éxito.');
        return true;
    } catch (e) {
        console.error('[Inference] Error al cargar el modelo ONNX:', e);
        return false;
    } finally {
        isInitializing = false;
    }
}

async function preprocessImage(base64Image) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = INPUT_DIM;
            canvas.height = INPUT_DIM;
            const ctx = canvas.getContext('2d');
            
            // Dibujar imagen redimensionada a 640x640 ignorando aspect ratio (padding sería mejor, pero esto es más rápido)
            ctx.drawImage(img, 0, 0, INPUT_DIM, INPUT_DIM);
            const imageData = ctx.getImageData(0, 0, INPUT_DIM, INPUT_DIM);
            const data = imageData.data;
            
            // Crear Tensor Float32 [1, 3, 640, 640]
            const float32Data = new Float32Array(3 * INPUT_DIM * INPUT_DIM);
            
            for (let i = 0; i < INPUT_DIM * INPUT_DIM; i++) {
                float32Data[i] = data[i * 4] / 255.0; // R
                float32Data[INPUT_DIM * INPUT_DIM + i] = data[i * 4 + 1] / 255.0; // G
                float32Data[2 * INPUT_DIM * INPUT_DIM + i] = data[i * 4 + 2] / 255.0; // B
            }
            
            const tensor = new ort.Tensor('float32', float32Data, [1, 3, INPUT_DIM, INPUT_DIM]);
            resolve(tensor);
        };
        img.onerror = reject;
        img.src = base64Image;
    });
}

export async function detectErrorsYolov8(base64Image) {
    if (!session) {
        await initSession();
        if (!session) return { has_errors: false, max_confidence: 0 };
    }
    
    try {
        const tensor = await preprocessImage(base64Image);
        
        const inputName = session.inputNames[0];
        const feeds = {};
        feeds[inputName] = tensor;
        
        const results = await session.run(feeds);
        
        const outputName = session.outputNames[0];
        const outputTensor = results[outputName];
        const outputData = outputTensor.data;
        // output.dims -> [1, numFeatures, numAnchors]
        const numClasses = outputTensor.dims[1] - 4;
        const numAnchors = outputTensor.dims[2];
        
        let hasErrors = false;
        let maxConfidence = 0;
        
        // Loop por todos los anchors y extraer predicciones (cajas lógicas omitidas ya que no las dibujaremos)
        for (let a = 0; a < numAnchors; a++) {
            for (let c = 0; c < numClasses; c++) {
                // Cálculo de offset en array plano
                const index = (4 + c) * numAnchors + a;
                const prob = outputData[index];
                
                if (prob > maxConfidence) {
                    maxConfidence = prob;
                }
            }
        }
        
        if (maxConfidence > CONFIDENCE_THRESHOLD) {
            hasErrors = true;
        }
        
        return {
            has_errors: hasErrors,
            max_confidence: maxConfidence
        };
        
    } catch (e) {
        console.error('[Inference] Fallo al ejecutar inferencia:', e);
        return { has_errors: false, max_confidence: 0 };
    }
}
