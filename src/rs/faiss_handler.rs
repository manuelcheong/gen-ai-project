use aws_config::meta::region::RegionProviderChain;
use aws_sdk_dynamodb::{Client as DynamoDbClient, model::AttributeValue};
use aws_sdk_s3::Client as S3Client;
use bytes::Bytes;
use faiss::{Index, IndexImpl, MetricType};
use lambda_runtime::{run, service_fn, Error, LambdaEvent};
use ndarray::{Array, Array1, Array2, Axis};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::Path;
use tempfile::NamedTempFile;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;

// Configuración
const BUCKET_NAME: &str = "vector-indices-pre";
const INDEX_KEY: &str = "current_index.idx";
const TABLE_NAME: &str = "vectors-table-pre";

// Estructuras para la solicitud y respuesta
#[derive(Deserialize)]
struct Request {
    query_vector: Vec<f32>,
    k: Option<usize>,
}

#[derive(Serialize)]
struct SearchResult {
    item: HashMap<String, Value>,
    similarity_score: f32,
}

#[derive(Serialize)]
struct Response {
    results: Vec<SearchResult>,
    status_code: i32,
}

// Función principal de Lambda
async fn function_handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    // Configurar tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .with_target(false)
        .without_time()
        .init();

    let query_vector = event.payload.query_vector;
    let k = event.payload.k.unwrap_or(10);

    // Inicializar clientes AWS
    let region_provider = RegionProviderChain::default_provider().or_else("eu-west-1");
    let config = aws_config::from_env().region(region_provider).load().await;
    let s3_client = S3Client::new(&config);
    let dynamodb_client = DynamoDbClient::new(&config);

    // Cargar el índice FAISS desde S3
    let index = load_index(&s3_client).await?;

    // Realizar búsqueda vectorial
    let (distances, indices) = search_similar_vectors(&index, &query_vector, k)?;

    // Obtener metadatos de DynamoDB
    let metadata = get_metadata(&dynamodb_client, &indices).await?;

    // Combinar resultados
    let mut results = Vec::new();
    for i in 0..indices.len() {
        if i < metadata.len() {
            let similarity_score = 1.0 / (1.0 + distances[i]);
            results.push(SearchResult {
                item: metadata[i].clone(),
                similarity_score,
            });
        }
    }

    Ok(Response {
        results,
        status_code: 200,
    })
}

// Cargar índice FAISS desde S3
async fn load_index(s3_client: &S3Client) -> Result<Box<dyn Index>, Error> {
    // Descargar archivo de índice
    let get_object_output = s3_client
        .get_object()
        .bucket(BUCKET_NAME)
        .key(INDEX_KEY)
        .send()
        .await?;

    // Guardar en archivo temporal
    let index_bytes = get_object_output.body.collect().await?.into_bytes();
    let temp_file = NamedTempFile::new()?;
    let temp_path = temp_file.path().to_owned();
    
    let mut file = File::create(&temp_path).await?;
    file.write_all(&index_bytes).await?;
    file.sync_all().await?;
    drop(file);

    // Cargar índice desde archivo
    let index = faiss::read_index(temp_path.to_str().unwrap())?;
    Ok(index)
}

// Buscar vectores similares
fn search_similar_vectors(
    index: &Box<dyn Index>,
    query_vector: &[f32],
    k: usize,
) -> Result<(Vec<f32>, Vec<i64>), Error> {
    // Convertir vector de consulta al formato correcto
    let query_array = Array::from_vec(query_vector.to_vec())
        .into_shape((1, query_vector.len()))?;

    // Realizar búsqueda
    let (distances, indices) = index.search(&query_array, k as i64)?;
    
    // Extraer resultados
    let distances_vec = distances.row(0).to_vec();
    let indices_vec = indices.row(0).to_vec();
    
    Ok((distances_vec, indices_vec))
}

// Obtener metadatos de DynamoDB
async fn get_metadata(
    client: &DynamoDbClient,
    indices: &[i64],
) -> Result<Vec<HashMap<String, Value>>, Error> {
    let mut results = Vec::new();

    for &idx in indices {
        let item_id = format!("doc{}", idx);
        
        let response = client
            .get_item()
            .table_name(TABLE_NAME)
            .key("item_id", AttributeValue::S(item_id))
            .send()
            .await?;

        if let Some(item) = response.item {
            // Convertir de DynamoDB AttributeValue a serde_json::Value
            let mut map = HashMap::new();
            for (key, value) in item {
                map.insert(key, attribute_to_json_value(value)?);
            }
            results.push(map);
        }
    }

    Ok(results)
}

// Convertir AttributeValue de DynamoDB a serde_json::Value
fn attribute_to_json_value(attr: AttributeValue) -> Result<Value, Error> {
    if let Some(s) = attr.as_s() {
        Ok(Value::String(s.to_string()))
    } else if let Some(n) = attr.as_n() {
        let num: f64 = n.parse()?;
        Ok(Value::Number(serde_json::Number::from_f64(num).unwrap()))
    } else if let Some(b) = attr.as_bool() {
        Ok(Value::Bool(b))
    } else if let Some(list) = attr.as_l() {
        let mut json_list = Vec::new();
        for item in list {
            json_list.push(attribute_to_json_value(item.clone())?);
        }
        Ok(Value::Array(json_list))
    } else if let Some(map) = attr.as_m() {
        let mut json_map = serde_json::Map::new();
        for (key, value) in map {
            json_map.insert(key.clone(), attribute_to_json_value(value.clone())?);
        }
        Ok(Value::Object(json_map))
    } else if attr.as_null().is_some() {
        Ok(Value::Null)
    } else {
        Ok(Value::Null) // Default fallback
    }
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    run(service_fn(function_handler)).await
}