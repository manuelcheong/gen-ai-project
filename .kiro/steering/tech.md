# Technology Stack

## Build System & Framework
- **Serverless Framework v4** - Primary deployment tool
- **AWS Provider** - Target cloud platform (eu-west-1 default region)
- **ARM64 Architecture** - Cost-optimized Lambda runtime

## Runtime Environments
- **Node.js 22.x** - Primary JavaScript runtime
- **LLRT (Low Latency Runtime)** - Optimized JavaScript runtime for Lambda
- **Python 3.12** - AI agent and ML workloads
- **Rust** - High-performance compute functions

## Key Dependencies

### JavaScript/Node.js
- `@aws-sdk/client-s3` - S3 operations
- ESLint with Airbnb config for code quality

### Python
- `strands-agents>=0.1.0` - AI agent framework
- `strands-agents-tools>=0.1.0` - Agent tooling
- `boto3>=1.28.0` - AWS SDK
- `mcp>=1.0.0` - Model Context Protocol

### Rust
- `lambda_runtime` - AWS Lambda runtime
- `reqwest` - HTTP client
- `aws-sdk-s3` - S3 operations
- `serde/serde_json` - Serialization

## AWS Services Used
- **Lambda Functions** - Compute layer
- **Step Functions** - Workflow orchestration
- **API Gateway** - REST and WebSocket APIs
- **S3** - Object storage
- **DynamoDB** - NoSQL database
- **SQS** - Message queuing
- **EventBridge Pipes** - Event routing
- **CloudFront** - CDN
- **Bedrock** - AI model access

## Common Commands

### Development
```bash
# Install dependencies
npm install

# Deploy to pre-production
serverless deploy --stage pre

# Deploy to specific region
serverless deploy --region eu-west-1

# Package Python dependencies
python utils/package_for_lambda.py
```

### Code Quality
```bash
# Run ESLint
npx eslint src/

# Build Rust binaries
cargo build --release
```

## Configuration Notes
- Environment variables managed via SSM Parameter Store
- API keys stored in AWS Secrets Manager
- Individual function packaging enabled for optimization
- Log retention set to 90 days
- Global timeout: 15 seconds, function timeout: 28 seconds