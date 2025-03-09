#[warn(unused_must_use)]
use lambda_runtime::{service_fn, LambdaEvent, Error};

// use serde::{Deserialize, Serialize};
use serde_json::Value;
use serde_json::json;

use core::result::Result;

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(_event: LambdaEvent<Value>) -> Result<Value, Error> {
    let event = _event.payload;
    
    print!("Event: {:?}", event);

    Ok(event)
}