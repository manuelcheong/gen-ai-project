// eslint-disable-next-line import/prefer-default-export
/**
 * Handles the event for the pipe reader.
 * @param {Object} event - The event object.
 * @returns {boolean} - Returns true.
 */

const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const client = new S3Client({ REGION: process.env.REGION });

const bucketName = 'gen-ai-content-pre';


const scrapeAndUpload = async (url, index) =>{
  let response = "empty";
  try {
      

      try {
        response = await fetch(url);
        response = await response.text(); 
      } catch (error) {
          console.error('Error fetching data:', error);
      }
  } catch (error) {
      console.error(`Error scraping ${url}:`, error);
  }
  return response;
} 




export const handler = async (event) => {
  console.log('------ WEBSCRAPPING LLRT 😎 CANARY DEPLOYMENT 🐙 AND LLRT WITH SDK 🐀 -----------');
  console.log(JSON.stringify(event));
  const urls = event.urls || [];
  const promises = urls.map((url) => scrapeAndUpload(url));
  const scrap_all = await Promise.all(promises); 

  const s3Key = `scraped-data.txt`;
  const params = {
      Bucket: bucketName,
      Key: s3Key,
      Body: scrap_all.flat().join('\n'),
      ContentType: 'text/plain'
  };

  const command = new PutObjectCommand(params);
  await client.send(command);

  return true;
  
};



//   LLRT lambda arm64 no sdk


