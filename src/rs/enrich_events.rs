#[warn(unused_must_use)]
use lambda_runtime::{service_fn, LambdaEvent, Error};

// use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

// use core::result::Result;
use std::time::{SystemTime, UNIX_EPOCH};

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(_event: LambdaEvent<Value>) -> Result<Value, Error> {
    let mut payload = _event.payload;

    let current_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_secs();
    
    // Add 2 hours (7200 seconds) for TTL
    let ttl = current_time + 7200;

    if let Value::Array(ref mut items) = payload {
        for item in items {
            if let Value::Object(ref mut map) = item {
                map.insert("additional_data".to_string(), json!({
                    "ttl": ttl
                }));
            }
        }
    }
    
    //print!("Updated Event: {:?}", payload);

    Ok(payload)
}