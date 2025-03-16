use aws_config::meta::region::RegionProviderChain;
use aws_sdk_s3::Client as S3Client;
use faiss::{Index, IndexFactory, MetricType};
use ndarray::{Array, Array2};
use std::env;
use std::fs::File;
use std::io::Write;
use std::path::Path;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Configuración
    let bucket_name = "vector-indices-bucket";
    let index_key = "current_index.idx";
    let temp_path = "/tmp/updated_index.idx";
    
    // Inicializar cliente S3
    let region_provider = RegionProviderChain::default_provider().or_else("us-east-1");
    let config = aws_config::from_env().region(region_provider).load().await;
    let s3_client = S3Client::new(&config);
    
    // Cargar vectores nuevos (ejemplo)
    let new_vectors = vec![
        vec![0.1, 0.2, 0.3, 0.4],
        vec![0.5, 0.6, 0.7, 0.8],
    ];
    let dimension = new_vectors[0].len();
    
    // Intentar descargar índice existente
    let existing_index = match s3_client
        .get_object()
        .bucket(bucket_name)
        .key(index_key)
        .send()
        .await {
            Ok(response) => {
                let bytes = response.body.collect().await?.into_bytes();
                let mut temp_file = File::create("/tmp/current_index.idx")?;
                temp_file.write_all(&bytes)?;
                temp_file.flush()?;
                
                Some(faiss::read_index("/tmp/current_index.idx")?)
            },
            Err(_) => None,
        };
    
    // Crear o actualizar índice
    let mut index = match existing_index {
        Some(idx) => idx,
        None => {
            // Crear nuevo índice
            let description = format!("Flat({})", dimension);
            IndexFactory::new(description, MetricType::L2)?
        }
    };
    
    // Convertir vectores a formato ndarray
    let mut flat_vectors = Vec::new();
    for vec in &new_vectors {
        flat_vectors.extend_from_slice(vec);
    }
    
    let vectors_array = Array::from_vec(flat_vectors)
        .into_shape((new_vectors.len(), dimension))?;
    
    // Añadir vectores al índice
    index.add(&vectors_array)?;
    
    // Guardar índice actualizado
    faiss::write_index(&index, temp_path)?;
    
    // Subir a S3
    let file_bytes = tokio::fs::read(temp_path).await?;
    s3_client
        .put_object()
        .bucket(bucket_name)
        .key(index_key)
        .body(file_bytes.into())
        .send()
        .await?;
    
    println!("Índice actualizado correctamente");
    Ok(())
}