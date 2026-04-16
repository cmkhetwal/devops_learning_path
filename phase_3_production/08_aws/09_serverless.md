# Lesson 09: Serverless Computing with AWS Lambda

## Why This Matters in DevOps

Serverless is not the absence of servers --- it is the absence of server management.
You write code, upload it, and AWS handles everything else: provisioning, scaling,
patching, and high availability. You pay only when your code runs, down to the
millisecond.

For DevOps engineers, serverless changes the operational model fundamentally. There
are no instances to patch, no capacity to plan, no servers to monitor for disk space.
Instead, your focus shifts to function design, event-driven architecture, cold start
optimization, and cost modeling based on invocations rather than uptime.

Lambda is the backbone of event-driven architectures on AWS. An image uploaded to S3
triggers a Lambda to generate thumbnails. A message in SQS triggers a Lambda to
process orders. An API Gateway request triggers a Lambda to serve a REST endpoint.
Understanding serverless is essential for the SA Associate exam, where you will
frequently choose between Lambda and EC2/ECS for a given scenario.

---

## Core Concepts

### Serverless Philosophy

```
TRADITIONAL:                         SERVERLESS:
  Provision servers                    Write code
  Install runtime                     Upload to Lambda
  Deploy application                  Configure trigger
  Configure auto-scaling              Done.
  Patch OS monthly
  Monitor disk/CPU/memory             AWS handles:
  Pay for idle servers 24/7           - Scaling (0 to thousands)
                                      - High availability
                                      - OS patching
                                      - Pay only for execution time

  MENTAL MODEL:
  Server-based: "I need 3 servers running 24/7 to handle my traffic"
  Serverless:   "I need a function that runs when events happen"
```

### Lambda Architecture

```
LAMBDA EXECUTION MODEL:

  EVENT SOURCE          LAMBDA SERVICE          YOUR FUNCTION
  (S3, API GW,    -->   Receives event    -->   Executes your
   SQS, EventBridge)    Provisions compute      handler code
                         Runs function          Returns response
                         Scales automatically
                         Shuts down when idle

COLD START vs WARM START:

  COLD START (first invocation or after idle):
  +--------+----------+---------+----------+
  | Download| Create   | Init    | Execute  |
  | code   | container| runtime | handler  |
  | (~50ms)| (~200ms) | (~200ms)| (your    |
  |        |          |         |  code)   |
  +--------+----------+---------+----------+
  Total: 500ms-3s depending on runtime and package size

  WARM START (reused container):
  +----------+
  | Execute  |
  | handler  |
  | (your    |
  |  code)   |
  +----------+
  Total: just your code execution time

  TIPS TO REDUCE COLD STARTS:
  - Use smaller deployment packages
  - Use Python/Node.js (faster than Java/C#)
  - Use Provisioned Concurrency for critical functions
  - Initialize SDK clients OUTSIDE the handler
```

### Lambda Triggers (Event Sources)

```
SYNCHRONOUS (caller waits for response):
  +-- API Gateway       (REST/HTTP API)
  +-- ALB               (HTTP requests)
  +-- Cognito           (user pool triggers)
  +-- CloudFront        (Lambda@Edge)

ASYNCHRONOUS (fire and forget):
  +-- S3                (object events)
  +-- SNS               (notifications)
  +-- EventBridge       (scheduled/event rules)
  +-- CloudWatch Logs   (log processing)
  +-- SES               (email)
  +-- CodeCommit        (repository events)

POLLING (Lambda polls the source):
  +-- SQS               (message queues)
  +-- DynamoDB Streams   (change data capture)
  +-- Kinesis            (streaming data)
  +-- MSK (Kafka)        (streaming data)
```

### Lambda Limits

| Resource | Limit |
|----------|-------|
| Memory | 128 MB - 10,240 MB (10 GB) |
| Timeout | Up to 15 minutes |
| Deployment package | 50 MB (zipped), 250 MB (unzipped) |
| /tmp storage | 512 MB - 10,240 MB |
| Environment variables | 4 KB total |
| Concurrent executions | 1,000 (soft limit, can increase) |
| Layers | Up to 5 per function |

### Lambda Layers

```
LAYERS: Shared code/dependencies across functions

  +--------------------+
  | Your Function Code |    <-- Your handler
  +--------------------+
  | Layer: boto3-extra |    <-- Shared library
  +--------------------+
  | Layer: pandas      |    <-- Data processing
  +--------------------+
  | Runtime: Python 3.12|   <-- AWS-managed
  +--------------------+

  Benefits:
  - Smaller deployment packages
  - Share code across multiple functions
  - Separate dependencies from business logic
  - Independent versioning
```

### Step Functions (Orchestration)

```
STEP FUNCTIONS: Orchestrate multiple Lambdas into workflows

  START
    |
    v
  +--Process Order--+
  |  Lambda          |
  +--------+---------+
           |
    +------+------+
    |             |
    v             v
  +--Check--+  +--Send---+
  | Payment |  | Confirm |
  | Lambda  |  | Email   |
  +----+----+  | Lambda  |
       |       +---------+
  +----+----+
  |         |
  v         v
SUCCESS   FAILED
  |         |
  v         v
+--Ship--+ +--Refund-+
| Lambda | | Lambda  |
+--------+ +---------+

  STATE TYPES:
  - Task:     Execute a Lambda or AWS service action
  - Choice:   Branch based on conditions (if/else)
  - Parallel: Run branches in parallel
  - Wait:     Delay execution
  - Map:      Loop over items (fan-out)
  - Succeed/Fail: End the workflow
```

### SAM (Serverless Application Model)

SAM is an open-source framework for building serverless applications. It extends
CloudFormation with simplified syntax for Lambda, API Gateway, and DynamoDB.

```yaml
# template.yaml (SAM template)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      CodeUri: src/
      Events:
        GetItems:
          Type: Api
          Properties:
            Path: /items
            Method: get
        PostItem:
          Type: Api
          Properties:
            Path: /items
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable

  ItemsTable:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: id
        Type: String
```

---

## Step-by-Step Practical

### Build a Serverless API

```bash
# Step 1: Create the Lambda function code
mkdir -p serverless-api && cd serverless-api

cat > lambda_function.py << 'EOF'
import json
import boto3
import uuid
import os
from datetime import datetime

# Initialize outside handler (reused on warm starts)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """Main handler for API Gateway events."""
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    try:
        if http_method == 'GET' and path == '/items':
            return get_items()
        elif http_method == 'POST' and path == '/items':
            return create_item(json.loads(event.get('body', '{}')))
        elif http_method == 'GET' and path.startswith('/items/'):
            item_id = path.split('/')[-1]
            return get_item(item_id)
        elif http_method == 'DELETE' and path.startswith('/items/'):
            item_id = path.split('/')[-1]
            return delete_item(item_id)
        else:
            return response(404, {'error': 'Not found'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def get_items():
    result = table.scan()
    return response(200, {'items': result.get('Items', [])})

def get_item(item_id):
    result = table.get_item(Key={'id': item_id})
    item = result.get('Item')
    if not item:
        return response(404, {'error': 'Item not found'})
    return response(200, item)

def create_item(body):
    item = {
        'id': str(uuid.uuid4()),
        'name': body.get('name', 'Unnamed'),
        'description': body.get('description', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return response(201, item)

def delete_item(item_id):
    table.delete_item(Key={'id': item_id})
    return response(200, {'message': f'Item {item_id} deleted'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }
EOF

# Step 2: Create a DynamoDB table
aws dynamodb create-table \
    --table-name ServerlessItems \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Step 3: Create the Lambda execution role
cat > lambda-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
EOF

LAMBDA_ROLE_ARN=$(aws iam create-role \
    --role-name serverless-api-role \
    --assume-role-policy-document file://lambda-trust-policy.json \
    --query 'Role.Arn' --output text)

# Attach policies
aws iam attach-role-policy \
    --role-name serverless-api-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > dynamodb-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "dynamodb:GetItem",
            "dynamodb:PutItem",
            "dynamodb:DeleteItem",
            "dynamodb:Scan"
        ],
        "Resource": "arn:aws:dynamodb:us-east-1:*:table/ServerlessItems"
    }]
}
EOF

aws iam create-policy \
    --policy-name serverless-dynamodb-access \
    --policy-document file://dynamodb-policy.json

aws iam attach-role-policy \
    --role-name serverless-api-role \
    --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/serverless-dynamodb-access

# Wait for IAM propagation
sleep 10

# Step 4: Package and create the Lambda function
zip function.zip lambda_function.py

aws lambda create-function \
    --function-name serverless-api \
    --runtime python3.12 \
    --role $LAMBDA_ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 256 \
    --environment "Variables={TABLE_NAME=ServerlessItems}"

# Step 5: Test the function locally
aws lambda invoke \
    --function-name serverless-api \
    --payload '{"httpMethod": "POST", "path": "/items", "body": "{\"name\": \"Test Item\", \"description\": \"My first serverless item\"}"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

cat response.json
# Expected: {"statusCode": 201, "body": "{\"id\": \"xxx\", \"name\": \"Test Item\"...}"}

# Step 6: Create an API Gateway (REST API)
API_ID=$(aws apigateway create-rest-api \
    --name "ServerlessItemsAPI" \
    --description "CRUD API for items" \
    --endpoint-configuration types=REGIONAL \
    --query 'id' --output text)

# Get the root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[0].id' --output text)

# Create /items resource
ITEMS_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part items \
    --query 'id' --output text)

# Create GET method on /items
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $ITEMS_ID \
    --http-method GET \
    --authorization-type NONE

aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $ITEMS_ID \
    --http-method POST \
    --authorization-type NONE

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_ARN="arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:serverless-api"

# Integrate methods with Lambda
for METHOD in GET POST; do
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $ITEMS_ID \
        --http-method $METHOD \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations"
done

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
    --function-name serverless-api \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:${ACCOUNT_ID}:${API_ID}/*"

# Deploy the API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod

API_URL="https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod"
echo "API URL: $API_URL"

# Step 7: Test the API
# Create an item
curl -X POST "$API_URL/items" \
    -H "Content-Type: application/json" \
    -d '{"name": "Widget", "description": "A useful widget"}'

# List items
curl "$API_URL/items"
```

### Create an S3-Triggered Lambda

```bash
# Create a function that processes images uploaded to S3
cat > s3_processor.py << 'EOF'
import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']

        print(f"New file uploaded: s3://{bucket}/{key} ({size} bytes)")

        # Example: copy to processed folder
        new_key = f"processed/{key.split('/')[-1]}"
        s3.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=new_key
        )
        print(f"Copied to s3://{bucket}/{new_key}")

    return {'statusCode': 200, 'body': f'Processed {len(event["Records"])} files'}
EOF

zip s3_processor.zip s3_processor.py

aws lambda create-function \
    --function-name s3-file-processor \
    --runtime python3.12 \
    --role $LAMBDA_ROLE_ARN \
    --handler s3_processor.lambda_handler \
    --zip-file fileb://s3_processor.zip \
    --timeout 60

# Add S3 trigger permission
aws lambda add-permission \
    --function-name s3-file-processor \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn "arn:aws:s3:::${BUCKET_NAME}"

# Configure S3 event notification
aws s3api put-bucket-notification-configuration \
    --bucket $BUCKET_NAME \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [{
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:'$ACCOUNT_ID':function:s3-file-processor",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [{"Name": "prefix", "Value": "uploads/"}]
                }
            }
        }]
    }'

# Test: upload a file
echo "test data" > test-upload.txt
aws s3 cp test-upload.txt s3://$BUCKET_NAME/uploads/test-upload.txt

# Check CloudWatch Logs for the Lambda execution
aws logs filter-log-events \
    --log-group-name /aws/lambda/s3-file-processor \
    --start-time $(date -d '5 minutes ago' +%s000) \
    --query 'events[*].message' --output text
```

---

## Exercises

### Exercise 1: Scheduled Lambda
Create a Lambda function that runs on a schedule (EventBridge rule, every 5 minutes)
to check the health of your web application endpoint and store the result in
DynamoDB. Include response time, status code, and timestamp.

### Exercise 2: SQS-Triggered Processing
Create an SQS queue and a Lambda function that processes messages from the queue.
Send 100 messages to the queue and observe how Lambda scales concurrency to process
them. Monitor the batch size and concurrent executions in CloudWatch.

### Exercise 3: Step Functions Workflow
Build a Step Functions state machine that orchestrates an order processing workflow:
validate order (Lambda) -> process payment (Lambda) -> on success, send confirmation
email (Lambda); on failure, refund (Lambda). Include error handling and retry logic.

### Exercise 4: Lambda with Layers
Create a Lambda Layer containing the pandas and requests libraries. Create a function
that uses these libraries to fetch data from a public API, process it with pandas,
and store results in S3. Verify the layer is shared and can be used by multiple
functions.

### Exercise 5: SAM Deployment
Install the SAM CLI. Create a SAM project with a REST API (API Gateway + Lambda +
DynamoDB). Build and deploy using `sam build` and `sam deploy --guided`. Test the
deployed API. Make a code change and deploy an update.

---

## Knowledge Check

### Question 1
What is a Lambda cold start and how can you mitigate it?

**Answer:** A cold start occurs when Lambda must create a new execution environment
for a function: downloading the code, creating a container, and initializing the
runtime. This adds 500ms-3s of latency. Mitigation strategies: (1) Use lighter
runtimes (Python/Node.js over Java), (2) minimize deployment package size, (3)
initialize SDK clients and database connections outside the handler, (4) use
Provisioned Concurrency ($) to keep environments pre-warmed, (5) keep functions
warm with scheduled pings (hacky but works).

### Question 2
When should you use Lambda versus ECS/EC2?

**Answer:** Use Lambda when: execution time is under 15 minutes, you want zero
server management, traffic is sporadic or event-driven, you want pay-per-invocation
pricing, your workload fits within memory/storage limits. Use ECS/EC2 when: tasks
run longer than 15 minutes, you need persistent connections (WebSocket servers),
you need more than 10 GB memory, you have steady high traffic (EC2 is cheaper at
scale), or you need GPU access.

### Question 3
How does Lambda handle concurrency and scaling?

**Answer:** Lambda automatically scales by running more instances of your function
in parallel. Each concurrent invocation uses one execution environment. The default
account limit is 1,000 concurrent executions (can be increased). You can set
Reserved Concurrency to guarantee capacity for critical functions (and cap it for
others). Provisioned Concurrency pre-warms a specified number of environments
to eliminate cold starts. For polling sources (SQS, Kinesis), Lambda scales
based on the number of messages/shards.

### Question 4
What is the difference between API Gateway REST API and HTTP API?

**Answer:** HTTP API is newer, cheaper (~70% less), faster (lower latency), and
simpler. It supports JWT authorization, OIDC, Lambda and HTTP backends, and
CORS configuration. REST API offers more features: API keys, usage plans, request
validation, request/response transformation, WAF integration, caching, and
resource policies. Use HTTP API for most new projects unless you specifically
need REST API features. REST API is the one typically tested on the SA Associate
exam.

### Question 5
What is AWS SAM and why would you use it?

**Answer:** SAM (Serverless Application Model) is an open-source framework that
extends CloudFormation with simplified syntax for serverless resources (Lambda, API
Gateway, DynamoDB, SQS, etc.). It provides the SAM CLI for local testing and
debugging, build and package commands, and guided deployment. Use SAM when you want
infrastructure-as-code for serverless applications, local testing with `sam local
invoke` and `sam local start-api`, and simplified templates that reduce boilerplate
compared to raw CloudFormation.
