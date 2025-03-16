// eslint-disable-next-line import/prefer-default-export
/**
 * Handles the event for the pipe reader.
 * @param {Object} event - The event object.
 * @returns {boolean} - Returns true.
 */

/* const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const client = new S3Client({ REGION: process.env.REGION });

const bucketName = 'gen-ai-content-pre';
 */

export const handler = async (event) => {
  console.log('------ FAISS  🐀 -----------');
  console.log(JSON.stringify(event));
 
  return true;
  
};



//   LLRT lambda arm64 no sdk


