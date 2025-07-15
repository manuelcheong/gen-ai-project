const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, BatchGetCommand } = require('@aws-sdk/lib-dynamodb');

// Configuración
const TABLE_NAME = process.env.DYNAMODB_TABLE || 'vectors-table-pre';

// Cliente DynamoDB
const client = new DynamoDBClient({ region: process.env.AWS_REGION });
const docClient = DynamoDBDocumentClient.from(client);

// Obtener metadatos para un conjunto de IDs
async function getMetadataItems(indices) {
  try {
    // Para conjuntos pequeños, usar BatchGetItem
    if (indices.length <= 25) {
      const keys = indices.map((idx) => ({ item_id: `doc${idx}` }));

      const response = await docClient.send(
        new BatchGetCommand({
          RequestItems: {
            [TABLE_NAME]: {
              Keys: keys,
            },
          },
        }),
      );

      return response.Responses[TABLE_NAME] || [];
    }
    // Para conjuntos más grandes, hacer múltiples llamadas

    const results = [];
    // eslint-disable-next-line no-restricted-syntax
    for (const idx of indices) {
      try {
        // eslint-disable-next-line no-await-in-loop
        const response = await docClient.send(
          new GetCommand({
            TableName: TABLE_NAME,
            Key: { item_id: `doc${idx}` },
          }),
        );

        if (response.Item) {
          results.push(response.Item);
        }
      } catch (error) {
        console.warn(`Error getting item doc${idx}:`, error);
        // Continuar con el siguiente ítem
      }
    }
    return results;
  } catch (error) {
    console.error('Error getting metadata from DynamoDB:', error);
    throw error;
  }
}

module.exports = {
  getMetadataItems,
};
