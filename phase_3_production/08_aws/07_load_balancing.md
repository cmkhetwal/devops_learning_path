# Lesson 07: Elastic Load Balancing

## Why This Matters in DevOps

Load balancers are the traffic cops of distributed systems. Without them, you cannot
achieve high availability, cannot distribute load across multiple instances, and cannot
perform zero-downtime deployments. In a DevOps workflow, load balancers are integral
to blue-green deployments, canary releases, and auto-scaling architectures.

As a DevOps engineer, you will configure ALBs for web applications, NLBs for TCP-heavy
workloads, set up health checks that actually detect application failures (not just
instance liveness), and integrate WAF rules to protect against attacks. You will also
use load balancers with Auto Scaling Groups to automatically register and deregister
instances as they scale.

Understanding the difference between Layer 4 and Layer 7 load balancing is essential
for both the SA Associate exam and real-world architecture decisions. The wrong type
of load balancer can add unnecessary latency, fail to route traffic correctly, or
cost significantly more than necessary.

---

## Core Concepts

### Why Load Balancers?

```
WITHOUT LOAD BALANCER:                WITH LOAD BALANCER:

  Users --> Single Server             Users --> [ALB] --> Server 1
            (single point                  |         --> Server 2
             of failure)                   |         --> Server 3
                                           |
                                     If Server 2 dies:
                                     ALB detects via health check
                                     and routes to Server 1 & 3
```

Benefits:
- **High Availability**: Distribute traffic across multiple AZs
- **Fault Tolerance**: Automatically remove unhealthy targets
- **Scalability**: Pair with Auto Scaling Groups
- **SSL Termination**: Handle TLS at the load balancer, not the app
- **Security**: Single entry point, integrate with WAF

### Types of Load Balancers

```
OSI MODEL CONTEXT:

  Layer 7 (Application)   --> ALB  (HTTP/HTTPS, WebSocket)
  Layer 4 (Transport)     --> NLB  (TCP, UDP, TLS)
  Layer 3 (Network)       --> GLB  (IP packets, inline inspection)

+---------------------------------------------------------------+
|                APPLICATION LOAD BALANCER (ALB)                |
|  - HTTP/HTTPS traffic                                         |
|  - Path-based routing (/api/* -> API servers)                 |
|  - Host-based routing (api.example.com -> API servers)        |
|  - Can inspect HTTP headers, methods, query strings           |
|  - WebSocket support                                          |
|  - Lambda targets                                             |
|  - Slower than NLB (content inspection)                       |
|  - Cost: ~$0.0225/hr + $0.008/LCU                            |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
|                NETWORK LOAD BALANCER (NLB)                    |
|  - TCP/UDP/TLS traffic                                        |
|  - Ultra-low latency (~100 microseconds)                      |
|  - Millions of requests per second                            |
|  - Static IP per AZ (or Elastic IP)                           |
|  - Preserves client source IP                                 |
|  - No content inspection                                      |
|  - Cost: ~$0.0225/hr + $0.006/NLCU                            |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
|                GATEWAY LOAD BALANCER (GLB)                    |
|  - Layer 3 (IP packets)                                       |
|  - Deploy/scale third-party appliances                        |
|  - Firewalls, IDS/IPS, deep packet inspection                 |
|  - Transparent to source/destination                          |
|  - Uses GENEVE protocol (port 6081)                           |
+---------------------------------------------------------------+
```

### ALB Architecture

```
                    INTERNET
                       |
               +-------v-------+
               |      ALB      |
               | (Layer 7)     |
               +---+---+---+---+
                   |   |   |
          +--------+   |   +--------+
          |            |            |
  LISTENER 1     LISTENER 2    LISTENER 3
  Port 80        Port 443      Port 443
  (redirect      (default      (host: api.*)
   to 443)       action)
          |            |            |
   +------+     +------+------+    |
   |             |            |    |
  RULE 1      RULE 2      DEFAULT  |
  /api/*      /static/*   action   |
   |             |           |     |
   v             v           v     v
+--------+  +--------+  +--------+  +--------+
|Target  |  |Target  |  |Target  |  |Target  |
|Group 1 |  |Group 2 |  |Group 3 |  |Group 4 |
|(API    |  |(Static |  |(Web    |  |(API    |
| servers)|  | assets)|  | app)  |  | v2)    |
+--------+  +--------+  +--------+  +--------+
| EC2-1  |  | EC2-3  |  | EC2-5  |  | Fargate|
| EC2-2  |  | EC2-4  |  | EC2-6  |  | Tasks  |
+--------+  +--------+  +--------+  +--------+
```

### Health Checks

```
HEALTH CHECK CONFIGURATION:

  ALB --> GET /health HTTP/1.1 --> Target Instance
                                       |
                              200 OK  --> HEALTHY
                              5xx     --> Mark as UNHEALTHY
                              Timeout --> Mark as UNHEALTHY

  Parameters:
  - Protocol: HTTP/HTTPS
  - Path: /health (application-level check)
  - Port: traffic-port (or custom)
  - Healthy threshold: 3 consecutive successes
  - Unhealthy threshold: 2 consecutive failures
  - Timeout: 5 seconds
  - Interval: 30 seconds

  BEST PRACTICE: Your /health endpoint should check:
  - Application is running
  - Database connection works
  - Critical dependencies are reachable
  - NOT just return 200 blindly
```

### SSL/TLS Termination

```
OPTION 1: Terminate at ALB (recommended)
  Client --[HTTPS]--> ALB --[HTTP]--> EC2
  - ALB handles SSL/TLS
  - Certificate stored in ACM (free)
  - Less CPU on EC2 instances
  - Easy to manage certificates

OPTION 2: End-to-end encryption
  Client --[HTTPS]--> ALB --[HTTPS]--> EC2
  - Re-encrypt traffic to targets
  - Required for compliance in some industries
  - More CPU overhead

OPTION 3: Pass-through (NLB only)
  Client --[TLS]--> NLB --[TLS]--> EC2
  - NLB does NOT terminate TLS
  - Application handles TLS directly
  - Preserves client certificate info
```

### Sticky Sessions (Session Affinity)

```
WITHOUT STICKY SESSIONS:          WITH STICKY SESSIONS:
  Request 1 --> Server A           Request 1 --> Server A (cookie set)
  Request 2 --> Server B           Request 2 --> Server A (cookie match)
  Request 3 --> Server C           Request 3 --> Server A (cookie match)

  TYPES:
  - Duration-based (ALB generates cookie, AWSALB)
  - Application-based (your app sets the cookie name)

  WARNING: Sticky sessions reduce the effectiveness of load balancing.
  Prefer stateless applications with external session stores (Redis).
```

### Path-Based and Host-Based Routing

```
PATH-BASED:
  example.com/api/*      --> API Target Group
  example.com/images/*   --> S3 bucket (via Lambda or redirect)
  example.com/*          --> Web App Target Group (default)

HOST-BASED:
  api.example.com        --> API Target Group
  admin.example.com      --> Admin Target Group
  *.example.com          --> Web App Target Group (default)

COMBINED (most powerful):
  Host: api.example.com + Path: /v2/* --> API v2 Target Group
  Host: api.example.com + Path: /v1/* --> API v1 Target Group
```

---

## Step-by-Step Practical

### Set Up ALB with Two EC2 Targets

```bash
# Step 1: Launch two web server instances (assuming VPC from Lesson 03)
for i in 1 2; do
    INSTANCE=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type t3.micro \
        --key-name devops-key \
        --security-group-ids $WEB_SG \
        --subnet-id $(eval echo \$PUB_SUB_$i) \
        --user-data '#!/bin/bash
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
echo "<h1>Server: '$i'</h1><p>Instance: $INSTANCE_ID</p><p>AZ: $AZ</p>" > /var/www/html/index.html
echo "OK" > /var/www/html/health' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=web-server-$i}]" \
        --query 'Instances[0].InstanceId' --output text)
    echo "Instance $i: $INSTANCE"
    eval "INST_$i=$INSTANCE"
done

# Wait for instances
aws ec2 wait instance-running --instance-ids $INST_1 $INST_2

# Step 2: Create a security group for the ALB
ALB_SG=$(aws ec2 create-security-group \
    --group-name alb-sg \
    --description "ALB security group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

# Allow traffic from ALB to instances
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp --port 80 \
    --source-group $ALB_SG

# Step 3: Create the Target Group
TG_ARN=$(aws elbv2 create-target-group \
    --name web-targets \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 3 \
    --unhealthy-threshold-count 2 \
    --target-type instance \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Step 4: Register targets
aws elbv2 register-targets \
    --target-group-arn $TG_ARN \
    --targets Id=$INST_1 Id=$INST_2

# Step 5: Create the ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name web-alb \
    --subnets $PUB_SUB_1 $PUB_SUB_2 \
    --security-groups $ALB_SG \
    --scheme internet-facing \
    --type application \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' --output text)
echo "ALB DNS: $ALB_DNS"

# Step 6: Create a listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Step 7: Verify target health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN \
    --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
    --output table
# Expected:
# +----------------------+---------+
# | i-0abc123def456      | healthy |
# | i-0def789ghi012      | healthy |
# +----------------------+---------+

# Step 8: Test load balancing
for i in $(seq 1 6); do
    curl -s http://$ALB_DNS | grep "Server:"
done
# Should alternate between Server: 1 and Server: 2
```

### Add Path-Based Routing Rules

```bash
# Create a second target group for API servers
API_TG_ARN=$(aws elbv2 create-target-group \
    --name api-targets \
    --protocol HTTP \
    --port 8080 \
    --vpc-id $VPC_ID \
    --health-check-path /api/health \
    --target-type instance \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Get the listener ARN
LISTENER_ARN=$(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --query 'Listeners[0].ListenerArn' --output text)

# Add a path-based routing rule
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 10 \
    --conditions '[{"Field":"path-pattern","Values":["/api/*"]}]' \
    --actions "[{\"Type\":\"forward\",\"TargetGroupArn\":\"$API_TG_ARN\"}]"

# Add an HTTP to HTTPS redirect rule (when you have a certificate)
# aws elbv2 create-rule \
#     --listener-arn $LISTENER_ARN \
#     --priority 1 \
#     --conditions '[{"Field":"path-pattern","Values":["/*"]}]' \
#     --actions '[{"Type":"redirect","RedirectConfig":{"Protocol":"HTTPS","Port":"443","StatusCode":"HTTP_301"}}]'
```

### Connect ALB with Auto Scaling Group

```bash
# Update the ASG to use the target group
aws autoscaling attach-load-balancer-target-groups \
    --auto-scaling-group-name web-app-asg \
    --target-group-arns $TG_ARN

# The ASG will now automatically register/deregister instances
# as it scales out/in. Health checks from the ALB will determine
# if instances are healthy.

# Verify
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names web-app-asg \
    --query 'AutoScalingGroups[0].TargetGroupARNs' \
    --output table
```

---

## Exercises

### Exercise 1: ALB with Multiple Target Groups
Create an ALB with three target groups: web (port 80), API (port 8080), and admin
(port 8443). Configure path-based routing: /api/* goes to API, /admin/* goes to
admin, and everything else goes to web. Test each route.

### Exercise 2: Health Check Optimization
Create a custom health check endpoint in your application that checks database
connectivity, cache availability, and disk space. Configure the ALB health check
to use this endpoint. Simulate a database failure and observe the ALB marking the
target as unhealthy.

### Exercise 3: SSL/TLS Configuration
Request a free SSL certificate from ACM for your domain. Create an HTTPS listener
on port 443 using the certificate. Add a rule to the HTTP listener (port 80) that
redirects all traffic to HTTPS. Verify the redirect works with curl -I.

### Exercise 4: NLB for TCP Workload
Create an NLB for a TCP-based service (e.g., a database proxy or a custom TCP server).
Compare the behavior with ALB: note the static IP, source IP preservation, and
latency difference.

### Exercise 5: Weighted Target Groups
Create two versions of your application (v1 and v2) in separate target groups.
Configure a weighted routing rule that sends 90% of traffic to v1 and 10% to v2
(canary deployment). Gradually shift traffic to v2 and verify with repeated curl
requests.

---

## Knowledge Check

### Question 1
When would you choose an NLB over an ALB?

**Answer:** Choose NLB when you need: (1) Ultra-low latency (NLB adds ~100
microseconds vs ALB's milliseconds), (2) static IP addresses per AZ (required by
some firewall rules and DNS configurations), (3) TCP/UDP protocol support (non-HTTP
workloads like databases, IoT, gaming), (4) millions of requests per second
throughput, (5) source IP preservation without X-Forwarded-For headers. Choose ALB
for HTTP/HTTPS workloads that need content-based routing.

### Question 2
How does an ALB handle an unhealthy target?

**Answer:** When a target fails the configured number of consecutive health checks
(unhealthy threshold), the ALB marks it as unhealthy and stops sending new requests
to it. Existing connections may be allowed to drain (connection draining/deregistration
delay, default 300 seconds). The ALB continues to health-check the target, and if
it passes the healthy threshold number of consecutive checks, it is marked healthy
again and starts receiving traffic. If all targets are unhealthy, the ALB returns
503 to clients.

### Question 3
What is the difference between path-based routing and host-based routing?

**Answer:** Path-based routing directs traffic based on the URL path (e.g., /api/*
goes to API servers, /images/* goes to a static content server). Host-based routing
directs traffic based on the Host header in the HTTP request (e.g., api.example.com
goes to API servers, admin.example.com goes to admin servers). Both can be combined
in a single rule for very specific routing (e.g., Host=api.example.com AND
Path=/v2/* goes to API v2 servers).

### Question 4
What is connection draining (deregistration delay)?

**Answer:** When a target is deregistered from a target group (e.g., during scale-in
or deployment), the ALB stops sending new requests to it but allows existing
in-flight requests to complete within the deregistration delay period (default 300
seconds). This prevents abruptly dropping active connections. Set a shorter value
for stateless applications and a longer value for long-running requests like file
uploads or WebSocket connections.

### Question 5
How does cross-zone load balancing work?

**Answer:** With cross-zone load balancing enabled (default for ALB, optional for
NLB), each load balancer node distributes traffic across all registered targets in
all enabled AZs, regardless of which AZ the node is in. Without it, each node only
distributes to targets in its own AZ, which can cause uneven distribution if AZs
have different numbers of targets. ALB has cross-zone enabled by default and free.
NLB has it disabled by default and charges for inter-AZ data transfer.
