# Lesson 08: Containers on AWS

## Why This Matters in DevOps

You already know Docker and Kubernetes from earlier in this learning path. Now the
question is: how do you run containers in production on AWS? AWS offers multiple
container services, each with different trade-offs between control, simplicity,
and cost.

As a DevOps engineer, you will make decisions that affect your team for years: ECS
or EKS? Fargate or EC2 launch type? App Runner for simple workloads? These choices
determine your operational burden, your scaling capabilities, and your monthly bill.

ECS is AWS-native and tightly integrated with the ecosystem. EKS gives you standard
Kubernetes if you need portability. Fargate removes server management entirely. App
Runner removes even container orchestration concerns. Understanding when to use each
is a critical skill for both the SA Associate exam and real-world DevOps practice.

---

## Core Concepts

### Container Services Landscape

```
CONTROL vs SIMPLICITY SPECTRUM:

  MORE CONTROL                                    LESS CONTROL
  MORE COMPLEXITY                                 LESS COMPLEXITY
  |                                                          |
  v                                                          v

  EC2 + Docker   EKS on EC2   ECS on EC2   ECS Fargate   App Runner
  (DIY)          (K8s managed  (AWS native  (Serverless   (Fully managed
                  control       orchestr.    containers)   from source)
                  plane)        + servers)

  DECISION GUIDE:
  +--------------------------------------------------------------------+
  | Already using K8s? Need portability?     --> EKS                   |
  | Want AWS-native, team knows AWS?         --> ECS                   |
  | Want to stop managing servers?           --> ECS + Fargate         |
  | Just want to deploy a container easily?  --> App Runner            |
  | Need full OS control, GPU, Windows?      --> ECS/EKS on EC2       |
  +--------------------------------------------------------------------+
```

### ECS Architecture

```
ECS COMPONENTS:

  +----------------------------------------------------------+
  |  ECS CLUSTER                                              |
  |                                                          |
  |  +---TASK DEFINITION (blueprint)---+                     |
  |  | Image: nginx:latest             |                     |
  |  | CPU: 256  Memory: 512           |                     |
  |  | Port Mappings: 80:80            |                     |
  |  | Environment Variables           |                     |
  |  | Log Configuration               |                     |
  |  | IAM Role (task role)            |                     |
  |  +--------------------------------+                     |
  |                |                                         |
  |  +---SERVICE (manages tasks)-------+                     |
  |  | Desired Count: 3                |                     |
  |  | Launch Type: FARGATE            |                     |
  |  | Load Balancer: ALB              |                     |
  |  | Auto Scaling: CPU target 70%    |                     |
  |  +------+---------+--------+------+                     |
  |         |         |        |                             |
  |     +---v--+  +---v--+  +--v---+                        |
  |     | TASK |  | TASK |  | TASK |                        |
  |     | (run-|  | (run-|  | (run-|                        |
  |     | ning)|  | ning)|  | ning)|                        |
  |     +------+  +------+  +------+                        |
  +----------------------------------------------------------+

  TASK = Running instance of a task definition (like a Pod in K8s)
  SERVICE = Ensures desired number of tasks are running (like Deployment)
  CLUSTER = Logical grouping of services and tasks
```

### ECS Launch Types

```
EC2 LAUNCH TYPE:                    FARGATE LAUNCH TYPE:
+---------------------------+      +---------------------------+
| You manage EC2 instances  |      | AWS manages infrastructure|
| in the cluster            |      |                           |
| +-------+ +-------+      |      | +-------+ +-------+      |
| | EC2   | | EC2   |      |      | |Fargate| |Fargate|      |
| |+----+ | |+----+ |      |      | | Task  | | Task  |      |
| || Task| | || Task| |      |      | |       | |       |      |
| |+----+ | |+----+ |      |      | +-------+ +-------+      |
| |+----+ | |       |      |      |                           |
| || Task| | |       |      |      | No EC2 to manage          |
| |+----+ | |       |      |      | Pay per task (vCPU + mem)  |
| +-------+ +-------+      |      | No patching, no scaling    |
|                           |      | instances                 |
| You patch, scale,         |      +---------------------------+
| monitor instances         |
+---------------------------+

PRICING COMPARISON (approximate):
  EC2:     Pay for instances (even if underutilized)
  Fargate: Pay per task: $0.04048/vCPU/hr + $0.004445/GB/hr
           (more expensive per unit but no waste)
```

### ECR (Elastic Container Registry)

```
DEVELOPER WORKFLOW:

  Build Image --> Push to ECR --> ECS pulls from ECR

  docker build -t myapp .
       |
       v
  docker tag myapp:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
       |
       v
  docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
       |
       v
  ECS Task Definition references this image URI
```

### EKS (Elastic Kubernetes Service)

```
EKS ARCHITECTURE:

  +------AWS Managed------+
  | EKS Control Plane     |
  | (API Server, etcd,    |
  | controller manager)   |
  | Multi-AZ, managed     |
  | $0.10/hr              |
  +-----------+-----------+
              |
  +-----------v-----------+
  | Your VPC              |
  | +--------+ +--------+ |
  | | Worker | | Worker | |  <-- EC2 instances (managed node groups)
  | | Node 1 | | Node 2 | |      or Fargate profiles
  | | [Pods] | | [Pods] | |
  | +--------+ +--------+ |
  +------------------------+

  EKS vs ECS:
  +------------------+-------------------------+----------------------+
  | Aspect           | ECS                     | EKS                  |
  +------------------+-------------------------+----------------------+
  | Orchestrator     | AWS proprietary         | Kubernetes (CNCF)    |
  | Learning curve   | Lower (AWS-native)      | Higher (K8s)         |
  | Portability      | AWS only                | Any K8s environment  |
  | Ecosystem        | AWS integrations         | Helm, Istio, Argo   |
  | Control plane    | Free                    | $0.10/hr ($73/month) |
  | Best for         | AWS-only teams          | Multi-cloud, K8s exp |
  +------------------+-------------------------+----------------------+
```

### App Runner

```
SIMPLEST OPTION:

  Source Code OR Container Image
         |
         v
  +--App Runner Service--+
  | Auto-builds (if src)  |
  | Auto-deploys          |
  | Auto-scales (to zero) |
  | Auto-TLS              |
  | Auto-load balancing   |
  +----------------------+
         |
         v
  HTTPS endpoint ready

  No VPC config, no task definitions, no services.
  Just deploy and go. Great for simple web apps and APIs.
  Limited customization compared to ECS/EKS.
```

---

## Step-by-Step Practical

### Deploy a Docker App on ECS Fargate

```bash
# Step 1: Create an ECR repository
REPO_URI=$(aws ecr create-repository \
    --repository-name devops-web-app \
    --image-scanning-configuration scanOnPush=true \
    --query 'repository.repositoryUri' --output text)
echo "ECR URI: $REPO_URI"

# Step 2: Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $REPO_URI

# Step 3: Create a simple application
mkdir -p ecs-app && cd ecs-app

cat > app.py << 'EOF'
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from ECS Fargate!',
        'hostname': socket.gethostname(),
        'version': os.environ.get('APP_VERSION', '1.0')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
EOF

cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
EOF

# Step 4: Build and push the image
docker build -t devops-web-app .
docker tag devops-web-app:latest $REPO_URI:latest
docker push $REPO_URI:latest

# Step 5: Create an ECS cluster
aws ecs create-cluster --cluster-name production-cluster
# Expected: { "cluster": { "clusterName": "production-cluster", "status": "ACTIVE" } }

# Step 6: Create IAM roles for ECS
# Task execution role (ECS agent uses this to pull images, write logs)
cat > ecs-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
EOF

aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://ecs-trust-policy.json

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Task role (your application uses this to access AWS services)
aws iam create-role \
    --role-name ecsWebAppTaskRole \
    --assume-role-policy-document file://ecs-trust-policy.json

# Step 7: Create a CloudWatch log group
aws logs create-log-group --log-group-name /ecs/devops-web-app

# Step 8: Register a task definition
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > task-definition.json << EOF
{
    "family": "devops-web-app",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsWebAppTaskRole",
    "containerDefinitions": [
        {
            "name": "web-app",
            "image": "${REPO_URI}:latest",
            "portMappings": [
                {
                    "containerPort": 8080,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "APP_VERSION", "value": "1.0"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/devops-web-app",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            },
            "essential": true
        }
    ]
}
EOF

aws ecs register-task-definition \
    --cli-input-json file://task-definition.json

# Step 9: Create a security group for the ECS tasks
ECS_SG=$(aws ec2 create-security-group \
    --group-name ecs-tasks-sg \
    --description "ECS tasks security group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $ECS_SG \
    --protocol tcp --port 8080 \
    --source-group $ALB_SG

# Step 10: Create a target group for ECS
ECS_TG_ARN=$(aws elbv2 create-target-group \
    --name ecs-web-targets \
    --protocol HTTP \
    --port 8080 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path /health \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Step 11: Create the ECS service
aws ecs create-service \
    --cluster production-cluster \
    --service-name web-app-service \
    --task-definition devops-web-app \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={
        subnets=[$PRIV_SUB_1,$PRIV_SUB_2],
        securityGroups=[$ECS_SG],
        assignPublicIp=DISABLED
    }" \
    --load-balancers "targetGroupArn=$ECS_TG_ARN,containerName=web-app,containerPort=8080"

# Step 12: Verify the service
aws ecs describe-services \
    --cluster production-cluster \
    --services web-app-service \
    --query 'services[0].[serviceName,status,runningCount,desiredCount]' \
    --output table

# Step 13: Set up auto-scaling for the ECS service
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/production-cluster/web-app-service \
    --min-capacity 2 \
    --max-capacity 10

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/production-cluster/web-app-service \
    --policy-name cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
        },
        "TargetValue": 70.0,
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'
```

### Update the Application (Rolling Deployment)

```bash
# Update the application code
# Edit app.py to change the version

# Build and push new image
docker build -t devops-web-app .
docker tag devops-web-app:latest $REPO_URI:v2
docker push $REPO_URI:v2

# Update the task definition with new image
# (create a new revision of the task definition with v2 tag)

# Update the service to use the new task definition
aws ecs update-service \
    --cluster production-cluster \
    --service web-app-service \
    --task-definition devops-web-app:2 \
    --force-new-deployment

# Watch the rolling update
aws ecs describe-services \
    --cluster production-cluster \
    --services web-app-service \
    --query 'services[0].deployments[*].[status,runningCount,desiredCount,taskDefinition]' \
    --output table
```

---

## Exercises

### Exercise 1: Multi-Container Task
Create a task definition with two containers: a web application (Flask/Express) and
a sidecar container running Nginx as a reverse proxy. Configure the Nginx container
to forward requests to the app container. Deploy on Fargate.

### Exercise 2: ECS Blue-Green Deployment
Set up a blue-green deployment using two target groups and CodeDeploy. Deploy v1,
then deploy v2 using blue-green strategy. Verify that traffic shifts from v1 to v2
with the ability to rollback.

### Exercise 3: ECR Lifecycle Policy
Create an ECR lifecycle policy that keeps only the 10 most recent images and deletes
untagged images older than 1 day. Verify the policy by pushing multiple images and
checking which ones are retained.

### Exercise 4: EKS Cluster Setup
Create an EKS cluster with managed node groups. Deploy a sample application using
kubectl. Set up the Kubernetes Cluster Autoscaler and the AWS Load Balancer Controller.
Compare the experience with ECS.

### Exercise 5: Cost Analysis
Deploy the same application on: (a) ECS on EC2 (t3.micro), (b) ECS on Fargate,
(c) App Runner. Run a load test against each and calculate the cost per 1 million
requests for each option. Document which is cheapest for different traffic patterns.

---

## Knowledge Check

### Question 1
When would you choose ECS over EKS?

**Answer:** Choose ECS when: (1) your team is already invested in the AWS ecosystem
and does not need Kubernetes portability, (2) you want simpler operations with fewer
components to manage, (3) you want free control plane (EKS costs $0.10/hr), (4) you
need deep integration with AWS services like CodeDeploy and CloudFormation. Choose
EKS when you need Kubernetes compatibility, want to use the K8s ecosystem (Helm,
Istio, Argo), or plan to run workloads across multiple clouds.

### Question 2
What is the difference between the ECS Task Execution Role and the Task Role?

**Answer:** The Task Execution Role is used by the ECS agent (not your application)
to pull container images from ECR, send logs to CloudWatch, and retrieve secrets
from Secrets Manager or Parameter Store. The Task Role is used by your application
code running inside the container to access AWS services (e.g., reading from S3,
writing to DynamoDB). They are separate roles with separate permissions following
the principle of least privilege.

### Question 3
How does Fargate pricing compare to EC2 launch type?

**Answer:** Fargate charges per vCPU-hour and per GB-hour of memory, with no
upfront costs or reservations. EC2 launch type charges for the EC2 instances
regardless of how many tasks are running on them. Fargate is typically more
expensive per unit of compute but eliminates waste from underutilized instances.
For steady-state workloads with high utilization, EC2 is cheaper. For variable
workloads or small services, Fargate is cheaper because you only pay for what
your tasks actually use.

### Question 4
What happens during an ECS rolling deployment?

**Answer:** ECS starts new tasks with the updated task definition while keeping
old tasks running. The service's deployment configuration (minimumHealthyPercent
and maximumPercent) controls how many tasks can be replaced at once. For example,
with desired=4, min=50%, max=200%: ECS can run up to 8 tasks and must keep at
least 2 healthy. New tasks are registered with the load balancer, and old tasks
are drained and stopped. If new tasks fail health checks, the deployment is rolled
back automatically.

### Question 5
What is AWS App Runner and when should you use it?

**Answer:** App Runner is a fully managed service that builds, deploys, and scales
containerized web applications directly from source code or container images. You
do not configure VPCs, load balancers, task definitions, or services. It auto-scales
from zero to handle traffic and provides HTTPS by default. Use it for simple web
applications and APIs where you want the fastest time-to-deploy and minimal
operational overhead. Avoid it when you need custom networking, sidecar containers,
or fine-grained control over the infrastructure.
