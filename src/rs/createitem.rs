#[warn(unused_must_use)]
use lambda_runtime::{service_fn, LambdaEvent, Error};

use serde::{Deserialize, Serialize};
use serde_json::Value;
use serde_json::json;

use core::result::Result;

//use spark_connect_rs::{SparkSession, SparkSessionBuilder};


#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(event: LambdaEvent<Value>) -> Result<Value, Error> {
    // Initialize Spark session
   /*  let spark = SparkSession::builder()
        .app_name("RustIcebergWrite")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.my_catalog.type", "iceberg")
        .config("spark.sql.catalog.my_catalog.warehouse", "arn:aws:s3tables:eu-west-1:178934116267:bucket/s3table-genai-pre")
        .get_or_create()
        .unwrap();

    // Create a DataFrame with sample data
    let data = vec![
        ("1", "Alice", 100.5),
        ("2", "Bob", 200.0),
        ("3", "Charlie", 300.75),
    ];

    let df = spark.create_data_frame(data)
        .unwrap()
        .columns(vec!["id", "name", "amount"]);

    // Write the DataFrame to the Iceberg table
    df.write()
        .format("iceberg")
        .mode("append")
        .save("my_catalog.iceberg_table")
        .unwrap();

    // Stop the Spark session
    spark.stop().unwrap(); */

    Ok(json!({
        "table": "s3table-genai-pre.namespace1.people",
        }))
}