use lambda_runtime::{run, service_fn, Error, LambdaEvent};
use serde_json::Value;
use reqwest;
use scraper::{Html, Selector};
use rusoto_core::Region;
use rusoto_s3::{PutObjectRequest, S3Client, S3};
use std::collections::HashMap;
use tokio::io::AsyncWriteExt;
use rayo::prelude::*;

async fn scrape_and_upload(url: String, index: usize, bucket_name: &str, s3_client: &S3Client) -> Result<(), Error> {
    let response = reqwest::get(&url).await?.text().await?;
    let document = Html::parse_document(&response);
    let selector = Selector::parse("h1").unwrap(); // Example: Extracting <h1> tags
    
    let mut scraped_data = String::new();
    for element in document.select(&selector) {
        scraped_data.push_str(&format!("{}\n", element.text().collect::<Vec<_>>().join(" ")));
    }
    
    let s3_key = format!("/webscrapping/scraped-data-{}.txt", index);
    let put_request = PutObjectRequest {
        bucket: bucket_name.to_string(),
        key: s3_key.to_string(),
        body: Some(scraped_data.into_bytes().into()),
        ..Default::default()
    };
    
    s3_client.put_object(put_request).await?;
    Ok(())
}

async fn function_handler(event: LambdaEvent<Value>) -> Result<String, Error> {
    // let dummy_event = LambdaEvent::new(serde_json::json!({"urls": ["https://example.com", "https://another.com"]}), serde_json::json!({}));

    let urls: Vec<String> = event.payload["urls"].as_array()
        .unwrap_or(&vec![])
        .iter()
        .filter_map(|u| u.as_str().map(String::from))
        .collect();
    
    let bucket_name = "gen-ai-content-pre";
    let s3_client = S3Client::new(Region::default());
    
    let mut tasks = Vec::new();
    for (index, url) in urls.into_iter().enumerate() {
        let s3_client_clone = s3_client.clone();
        let bucket_name_clone = bucket_name.to_string();
        tasks.push(rayo::spawn(scrape_and_upload(url, index, &bucket_name_clone, &s3_client_clone)));
    }
    
    for task in tasks {
        task.await.unwrap()?;
    }
    
    Ok("Scraping complete and uploaded to S3".to_string())
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    run(service_fn(function_handler)).await
}

