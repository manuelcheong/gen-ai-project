use aws_sdk_s3::primitives::ByteStream;
use lambda_runtime::{service_fn, LambdaEvent, Error};
use tokio;
use reqwest::{Client};
use serde_json::Value;
use tokio::task::JoinError;
use serde_json::json;
use uuid::Uuid;
use regex::Regex;
// use scraper::{Html, Selector};


fn extract_urls(text: &str) -> Vec<String> {
    let url_pattern = r#"https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})(?:/[^\s"']*)?"#;
    let re = Regex::new(url_pattern).unwrap();

    re.find_iter(text)
        .map(|m| m.as_str().to_string()) // Convert matches to String
        .collect()
}
        
async fn fetch_url(url: String) -> Result<String, Error> {
    let client = Client::new();
    let response = client.get(&url).send().await?;
    let mut final_response = response.text().await?;
    final_response = final_response.replace(" ", "");
    Ok(final_response)
    // let client = Client::new();
    // let response = client.get(&url).send().await?;

    // let response = reqwest::get(&url).await?.text().await?;
    // ---- parsing ----
    
    // let document = Html::parse_document(&response);
    // let selector = Selector::parse("body").unwrap();

    // let mut text_content = String::new();

    /* if let Some(body) = document.select(&selector).next() {
        text_content = body.text().collect::<Vec<_>>().join(" ");
        println!("{}", text_content);
    } else {
        println!("No <body> found!");
    } 
    // --------
    text_content = text_content.replace(" ", "");
    Ok(text_content) */
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(event: LambdaEvent<Value>) -> Result<Value, Error> {
    // List of URLs to scrape
    /* let urls: Vec<String> = vec![
        "https://example.com/1".to_string(),
        "https://example.com/2".to_string(),
        // Add more URLs here
    ]; */

    //let raw_content = event.payload["content"].as_str().unwrap_or("");

    // let full_content = format!("r#{}#", raw_content);

    //let urls = extract_urls(&raw_content);

    let urls: Vec<String> = event.payload["urls"].as_array()
        .unwrap_or(&vec![])
        .iter()
        .filter_map(|u| u.as_str().map(String::from))
        .collect();  

    // Vector to store tasks
    let mut tasks = vec![];

    for url in &urls {
        let task_url = url.clone();
        tasks.push(tokio::task::spawn(async move { fetch_url(task_url).await }));
    }

    // Wait for all tasks to complete and collect results
    let joined_tasks: Vec<tokio::task::JoinHandle<Result<String, Error>>> = tasks;
    let results: Result<Vec<Result<String, Error>>, JoinError> = futures_util::future::try_join_all(joined_tasks).await;

    // Process the results
    let mut output = String::from("");

    match results {
        Ok(bodies) => {
            for body in bodies.into_iter() {
                // println!("Success: {:?}", body);
                output.push_str(&body.unwrap());
            }
        },
        Err(err) => eprintln!("Failed to join all tasks: {:?}", err),
    }

    let config = aws_config::load_from_env().await;
    let s3_client = aws_sdk_s3::Client::new(&config);

    let my_uuid = Uuid::new_v4();
    let uuid_string = my_uuid.to_string();

    upload_content(&s3_client, &output, &uuid_string).await?;

    let prefix = "s3://gen-ai-content-pre/".to_string();
    let result = prefix + &uuid_string;
    Ok(json!({
        "url": result,  // "s3://gen-ai-content-pre/filename.txt",
        "bucket": std::env::var("BUCKET_NAME").expect("BUCKET_NAME must be set"),
        "key": uuid_string,
        }))
}

pub async fn upload_content(
    client: &aws_sdk_s3::Client,
    content: &str,
    uuid_string: &String,
) -> Result<(), Error> {
    // println!("{:?}", content);

    let bucket = std::env::var("BUCKET_NAME").expect("BUCKET_NAME must be set");

    let _result = client
        .put_object()
        .bucket(bucket)
        .key(uuid_string)
        .body(ByteStream::from(String::from(content).into_bytes()))
        .send()
        .await?;

    // println!("{:?}", result);

    Ok(())
}