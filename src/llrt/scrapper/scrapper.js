// eslint-disable-next-line import/prefer-default-export
/**
 * Handles the event for the pipe reader.
 * @param {Object} event - The event object.
 * @returns {boolean} - Returns true.
 */
/* 
const axios = require('axios');
const cheerio = require('cheerio');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const client = new S3Client({ REGION: process.env.REGION });

const bucketName = 'gen-ai-content-pre';


const scrapeAndUpload = async (url, index) =>{
  try {
      const response = await axios.get(url);
      const $ = cheerio.load(response.data);
      const scrapedData = $('body').text(); // Example: Extracting text from <body> tag

      const s3Key = `scraped-data-${index}.txt`;
      const params = {
          Bucket: bucketName,
          Key: s3Key,
          Body: scrapedData,
          ContentType: 'text/plain'
      };

      const command = new PutObjectCommand(params);
      await client.send(command);

      console.log(`Successfully uploaded data from ${url} to ${s3Key}`);
  } catch (error) {
      console.error(`Error scraping ${url}:`, error);
  }
} */

  const https = require("https");




export const handler = async (event) => {
  /* console.log('------ WEBSCRAPPING LLRT 😎 CANARY DEPLOYMENT 🐙 AND LLRT WITH SDK 🐀 -----------');
  console.log(JSON.stringify(event));
  const urls = event.urls || [];
  const promises = urls.map((url, index) => scrapeAndUpload(url, index));
  await Promise.all(promises); */
  // return { message: 'Scraping complete and uploaded to S3' }; 

  //return true;
  const url = event.url || "https://jsonplaceholder.typicode.com/todos/1";

    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = "";
            res.on("data", (chunk) => { data += chunk; });
            res.on("end", () => resolve(data));
        }).on("error", (err) => reject(err));
    });
};



//   LLRT lambda arm64 no sdk


