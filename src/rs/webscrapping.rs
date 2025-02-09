use lambda_runtime::{run, service_fn, Error, LambdaEvent};
use serde_json::Value;
use rayon::prelude::*;
use reqwest;
use scraper::{Html, Selector};
// use tokio::io::AsyncWriteExt;

async fn scrape_and_upload(index: usize, url: String) -> Result<(), Error> {
    let response = reqwest::get(&url).await?.text().await?;
    let document = Html::parse_document(&response);
    let selector = Selector::parse("body").unwrap(); // Example: Extracting <h1> tags
    
    let mut scraped_data = String::new();
    for element in document.select(&selector) {
        scraped_data.push_str(&format!("{}\n", element.text().collect::<Vec<_>>().join(" ")));
    }
    
    /* let s3_key = format!("scraped-data-{}.txt", index);
    let put_request = PutObjectRequest {
        bucket: bucket_name.to_string(),
        key: s3_key.to_string(),
        body: Some(scraped_data.into_bytes().into()),
        ..Default::default()
    };
    
    s3_client.put_object(put_request).await?; */
    println!("Pagina {}", index);
    println!("{}", scraped_data);
    Ok(())
}

async fn function_handler(event: LambdaEvent<Value>)-> Result<(), Error> {
    /* let urls = vec![
        "https://example.com",
        "https://www.rust-lang.org",
        "https://www.wikipedia.org",
    ]; */

    let urls: Vec<String> = event.payload["urls"].as_array()
        .unwrap_or(&vec![])
        .iter()
        .filter_map(|u| u.as_str().map(String::from))
        .collect(); 

    // let bucket_name = "gen-ai-content-pre";

    println!("URLs {:?}", urls);

    urls.into_par_iter().enumerate().for_each(|(index, url)| {
        tokio::spawn(async move {
            let _ = scrape_and_upload(index, url.to_string()).await;
        });
    });
    
    Ok(())

}

#[tokio::main]
async fn main() -> Result<(), Error> {
    run(service_fn(function_handler)).await
}

