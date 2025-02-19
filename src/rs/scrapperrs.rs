use aws_sdk_s3::primitives::ByteStream;
use lambda_runtime::{service_fn, LambdaEvent, Error};
use tokio;
use reqwest::{Client};
use serde_json::Value;
use tokio::task::JoinError;
use serde_json::json;


async fn fetch_url(url: String) -> Result<String, Error> {
    let client = Client::new();
    let response = client.get(&url).send().await?;
    Ok(response.text().await?)
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

    upload_content(&s3_client, &output).await?;

    Ok(json!({
        "content": &output,
        }))
}

pub async fn upload_content(
    client: &aws_sdk_s3::Client,
    content: &str,
) -> Result<(), Error> {
    println!("{:?}", content);

    let bucket = std::env::var("BUCKET_NAME").expect("BUCKET_NAME must be set");

    let result = client
        .put_object()
        .bucket(bucket)
        .key("filename.txt")
        .body(ByteStream::from(String::from(content).into_bytes()))
        .send()
        .await?;

    println!("{:?}", result);

    Ok(())
}