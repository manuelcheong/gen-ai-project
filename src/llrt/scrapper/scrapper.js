// eslint-disable-next-line import/prefer-default-export
/**
 * Handles the event for the pipe reader.
 * @param {Object} event - The event object.
 * @returns {boolean} - Returns true.
 */
/* 
const axios = require('axios');
const cheerio = require('cheerio');

*/
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const client = new S3Client({ REGION: process.env.REGION });

const bucketName = 'gen-ai-content-pre';


const scrapeAndUpload = async (url, index) =>{
  try {
      let response;

      try {
        response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        response = await response.json(); // Convert response to JSON
        console.log(data);
      } catch (error) {
          console.error('Error fetching data:', error);
      }

      const s3Key = `scraped-data-${index}.txt`;
      const params = {
          Bucket: bucketName,
          Key: s3Key,
          Body: response,
          ContentType: 'text/plain'
      };

      const command = new PutObjectCommand(params);
      await client.send(command);

      console.log(`Successfully uploaded data from ${url} to ${s3Key}`);
  } catch (error) {
      console.error(`Error scraping ${url}:`, error);
  }
} 




export const handler = async (event) => {
  console.log('------ WEBSCRAPPING LLRT 😎 CANARY DEPLOYMENT 🐙 AND LLRT WITH SDK 🐀 -----------');
  console.log(JSON.stringify(event));
  const urls = event.urls || [];
  const promises = urls.map((url, index) => scrapeAndUpload(url, index));
  await Promise.all(promises); 
  // return { message: 'Scraping complete and uploaded to S3' }; 

  return true;
  
};



//   LLRT lambda arm64 no sdk


