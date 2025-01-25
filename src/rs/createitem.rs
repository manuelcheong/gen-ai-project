use spark_connect_rs::{SparkSession, SparkSessionBuilder};

use spark_connect_rs::functions as F;

use spark_connect_rs::dataframe::SaveMode;
use spark_connect_rs::types::DataType;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let spark: SparkSession = SparkSessionBuilder::default().build().await?;


    spark.sql("CREATE NAMESPACE IF NOT EXISTS s3table-genai-pre.namespace1").await?;          
    //spark.sql("CREATE DATABASE IF NOT EXISTS demo").await?;
    //spark.sql("USE demo").await?;
    //spark.sql("DROP TABLE IF EXISTS people").await?;
    spark.sql("CREATE TABLE s3table-genai-pre.namespace1.people (name STRING, age_int INT)").await?;
    spark.sql("INSERT INTO s3table-genai-pre.namespace1.people VALUES ('John', 30), ('Anna', 20), ('Peter', 25)").await?;
    spark.sql("SELECT * FROM s3table-genai-pre.namespace1.people").await?.show(Some(5), None, None).await?;
    // spark.sql("SELECT * FROM people WHERE age_int > 20").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT * FROM people WHERE age_int > 20 ORDER BY name DESC").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT COUNT(*) FROM people").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT SUM(age_int) FROM people").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT AVG(age_int) FROM people").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT MAX(age_int) FROM people").await?.show(Some(5), None, None).await?;
    //spark.sql("SELECT MIN(age_int) FROM people").await?.show(Some(5), None, None).await?;




    Ok(())
}