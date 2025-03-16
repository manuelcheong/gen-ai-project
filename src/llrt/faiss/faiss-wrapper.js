const fs = require('fs');
const path = require('path');
const os = require('os');
const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const faiss = require('faiss-node');

// Configuración
const BUCKET_NAME = process.env.S3_BUCKET || 'vector-indices-pre';
const INDEX_KEY = process.env.INDEX_KEY || 'current_index.idx';
const TEMP_DIR = os.tmpdir();

// Cliente S3
const s3Client = new S3Client({ region: process.env.AWS_REGION });

// Cargar índice FAISS desde S3
async function loadIndex() {
  const tempPath = path.join(TEMP_DIR, 'faiss_index.idx');
  
  try {
    // Descargar índice de S3
    const response = await s3Client.send(
        new GetObjectCommand({
        Bucket: BUCKET_NAME,
        Key: INDEX_KEY
        })
    );
    
    // Escribir a archivo temporal
    const writeStream = fs.createWriteStream(tempPath);
    response.Body.pipe(writeStream);
    
    // Esperar a que termine la escritura
    await new Promise((resolve, reject) => {
        writeStream.on('finish', resolve);
        writeStream.on('error', reject);
    });
    
    // Cargar índice desde archivo
    const index = faiss.readIndex(tempPath);
    return index;
    } catch (error) {
    console.error('Error loading FAISS index:', error);
    throw error;
    }
}

// Buscar vectores similares
async function searchVectors(queryVector, k) {
  try {
    // Cargar índice
    const index = await loadIndex();
    
    // Convertir a Float32Array si es necesario
    const queryVectorTyped = queryVector instanceof Float32Array 
      ? queryVector 
      : new Float32Array(queryVector);
    
    // Realizar búsqueda
    const result = index.search(queryVectorTyped, k);
    
    return {
      distances: Array.from(result.distances),
      indices: Array.from(result.labels)
    };
  } catch (error) {
    console.error('Error searching vectors:', error);
    throw error;
  }
}

// Actualizar índice con nuevos vectores
async function updateIndex(newVectors, newIds = null) {
    try {
    let index;
    const tempPath = path.join(TEMP_DIR, 'faiss_index.idx');
    
    try {
      // Intentar cargar índice existente
        index = await loadIndex();
    } catch (error) {
      // Crear nuevo índice si no existe
        const dimension = newVectors[0].length;
        index = new faiss.IndexFlatL2(dimension);
    }
    
    // Convertir vectores a Float32Array
    const vectors = new Float32Array(newVectors.flat());
    
    // Añadir vectores al índice
    if (newIds) {
        index.add_with_ids(vectors, new Uint64Array(newIds));
    } else {
        index.add(vectors);
    }
    
    // Guardar índice a archivo temporal
    faiss.writeIndex(index, tempPath);
    
    // Subir a S3
    const fileContent = fs.readFileSync(tempPath);
    await s3Client.send(
            new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: INDEX_KEY,
            Body: fileContent
        })
    );
    
    return { success: true, ntotal: index.ntotal };
    } catch (error) {
    console.error('Error updating index:', error);
    throw error;
    }
}

module.exports = {
  searchVectors,
  updateIndex
};