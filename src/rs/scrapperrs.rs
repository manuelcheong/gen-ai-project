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

async fn func(_event: LambdaEvent<Value>) -> Result<Value, Error> {
    // List of URLs to scrape
    let urls: Vec<String> = vec![
        "https://example.com/1".to_string(),
        "https://example.com/2".to_string(),
        // Add more URLs here
    ];

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
    match results {
        Ok(bodies) => {
            for body in bodies.into_iter() {
                println!("Success: {:?}", body);
            }
        },
        Err(err) => eprintln!("Failed to join all tasks: {:?}", err),
    }

    Ok(json!({
        "output": "OK",
        }))
}