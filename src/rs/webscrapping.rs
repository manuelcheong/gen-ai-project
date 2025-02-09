use lambda_runtime::{run, service_fn, Error, LambdaEvent};
use serde_json::Value;
use rayon::prelude::*;
use reqwest::blocking::get;
use scraper::{Html, Selector};
use rusoto_core::Region;
use rusoto_s3::{PutObjectRequest, S3Client, S3};


fn scrape_url(url: &str) -> String {
    match get(url) {
        Ok(response) => {
            if let Ok(body) = response.text() {
                let document = Html::parse_document(&body);
                let selector = Selector::parse("h1").unwrap();
                let extracted_text: Vec<String> = document
                    .select(&selector)
                    .map(|element| element.text().collect::<String>())
                    .collect();
                return format!("URL: {}\nExtracted H1: {:?}\n", url, extracted_text);
            }
        }
        Err(err) => return format!("Failed to fetch {}: {}\n", url, err),
    }
    "".to_string()
}


async fn upload_to_s3(bucket: &str, key: &str, data: String) -> Result<(), Error> {
    let s3_client = S3Client::new(Region::default());

    let request = PutObjectRequest {
        bucket: bucket.to_string(),
        key: key.to_string(),
        body: Some(data.into_bytes().into()),
        ..Default::default()
    };

    s3_client.put_object(request).await?;
    Ok(())
}

async fn function_handler(_event: LambdaEvent<Value>) -> Result<String, Error> {
    let urls = vec![
        "https://example.com",
        "https://www.rust-lang.org",
        "https://www.wikipedia.org",
    ];
    // let bucket_name = "gen-ai-content-pre";

    let results: Vec<String> = urls.par_iter().map(|url| scrape_url(url)).collect();

    for result in results {
        println!("{}", result);
    }

    /* for (index, result) in results.iter().enumerate() {
        let key = format!("scraped_data_{}.txt", index);
        if let Err(e) = upload_to_s3(bucket_name, &key, result.clone()).await {
            eprintln!("Failed to upload {}: {}", key, e);
        } else {
            println!("Uploaded {} to S3", key);
        }
    } */
    
    Ok("Scraping complete and uploaded to S3".to_string())
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    run(service_fn(function_handler)).await
}

