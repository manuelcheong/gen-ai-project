const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuración
const BUCKET_NAME = process.env.S3_BUCKET || 'vector-indices-pre';
const TEMP_DIR = os.tmpdir();

// Cliente S3
const s3Client = new S3Client({ region: process.env.AWS_REGION });

// Descargar archivo de S3
async function downloadFromS3(key, localPath) {
  try {
    const response = await s3Client.send(
      new GetObjectCommand({
        Bucket: BUCKET_NAME,
        Key: key
      })
    );
    
    // Escribir a archivo local
    const writeStream = fs.createWriteStream(localPath);
    response.Body.pipe(writeStream);
    
    // Esperar a que termine la escritura
    return new Promise((resolve, reject) => {
      writeStream.on('finish', () => resolve(localPath));
      writeStream.on('error', reject);
    });
  } catch (error) {
    console.error(`Error downloading ${key} from S3:`, error);
    throw error;
  }
}

// Subir archivo a S3
async function uploadToS3(localPath, key) {
  try {
    const fileContent = fs.readFileSync(localPath);
    
    await s3Client.send(
      new PutObjectCommand({
        Bucket: BUCKET_NAME,
        Key: key,
        Body: fileContent
      })
    );
    
    return { success: true, key };
  } catch (error) {
    console.error(`Error uploading to S3 key ${key}:`, error);
    throw error;
  }
}

module.exports = {
  downloadFromS3,
  uploadToS3
};