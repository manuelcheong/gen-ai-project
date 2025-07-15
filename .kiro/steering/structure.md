# Project Structure

## Root Level
- `serverless.yml` - Main Serverless Framework configuration
- `Cargo.toml` - Rust workspace configuration with multiple binaries
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies for Lambda layers

## Source Code Organization (`src/`)

### JavaScript Functions
- `src/js/` - Standard Node.js Lambda functions
- `src/llrt/` - LLRT-optimized Lambda functions
  - `src/llrt/scrapper/` - Web scraping functions
  - `src/llrt/faiss/` - Vector database operations

### Python Functions
- `src/python/agents/` - Strands-based AI agents
- `src/python/location/` - Location-specific agents
- `src/python/weather/` - Weather-specific agents

### Rust Functions
- `src/rs/` - High-performance Rust Lambda functions
  - Multiple binary targets defined in Cargo.toml
  - Focus on data processing and enrichment

### Frontend Assets
- `src/promptui/` - Web interface components

## Infrastructure as Code (`iac/`)

### API Definitions
- `iac/api/` - API Gateway configurations
  - `definitions/` - Resource and method definitions
  - `schemas/` - JSON schemas for validation
  - Separate files for REST, WebSocket, and private APIs

### AWS Resources
- `iac/lambda/` - Lambda function configurations
- `iac/states/` - Step Functions state machines
  - `definitions/` - ASL (Amazon States Language) JSON files
- `iac/dynamo/` - DynamoDB table definitions
- `iac/s3/` - S3 bucket configurations
- `iac/queues/` - SQS queue definitions
- `iac/pipes/` - EventBridge Pipes configurations
- `iac/network/` - VPC, security groups, load balancers
- `iac/cdn/` - CloudFront distributions
- `iac/waf/` - Web Application Firewall rules

## Key Patterns

### Function Organization
- Each runtime type has its own directory structure
- Infrastructure definitions are separate from source code
- Individual packaging enabled for optimal bundle sizes

### Configuration Management
- Environment-specific values in `serverless.yml` custom section
- SSM Parameter Store for runtime configuration
- Secrets Manager for sensitive data

### Deployment Structure
- Stage-based deployments (pre, prod)
- Region-specific configurations
- Individual function artifacts for faster deployments

## File Naming Conventions
- Infrastructure files use descriptive names matching AWS resource types
- Source files follow runtime-specific conventions (camelCase for JS, snake_case for Python/Rust)
- ASL state machine definitions use `.asl.json` extension