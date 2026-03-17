#!/usr/bin/env python3
"""Add new SAA questions from web sources to questions.json"""
import json
import os

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'questions.json')

NEW_SAA_QUESTIONS = [
    {
        "id": "saa106-1",
        "question": "A company needs to grant temporary access to a third-party auditor to review resources in their AWS account. The auditor should have read-only access for 24 hours. What is the MOST secure approach?",
        "choices": [
            {"label": "A", "text": "Create an IAM user with ReadOnlyAccess policy and delete after 24 hours."},
            {"label": "B", "text": "Create a cross-account IAM role with ReadOnlyAccess policy and a 24-hour maximum session duration."},
            {"label": "C", "text": "Share the root account credentials with a 24-hour password expiry."},
            {"label": "D", "text": "Create an IAM group with temporary permissions."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Cross-account IAM roles with time-limited sessions follow least privilege and are the recommended approach for temporary third-party access. No permanent credentials are created."
    },
    {
        "id": "saa106-2",
        "question": "An application runs on EC2 instances behind an Application Load Balancer across two Availability Zones. The company requires the application to remain available even if an entire AWS Region becomes unavailable. What should a solutions architect recommend?",
        "choices": [
            {"label": "A", "text": "Add more instances in additional Availability Zones within the same Region."},
            {"label": "B", "text": "Deploy the application in a second Region with Route 53 failover routing."},
            {"label": "C", "text": "Use Amazon CloudFront with a custom origin."},
            {"label": "D", "text": "Enable cross-Region replication on the ALB."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Multi-Region deployment with Route 53 failover routing provides Regional-level resilience. If the primary Region fails, Route 53 automatically routes traffic to the secondary Region."
    },
    {
        "id": "saa106-3",
        "question": "A company runs a batch processing workload that can be interrupted and restarted without data loss. The workload runs for approximately 6 hours daily and has flexible start times. Which EC2 pricing option provides the MOST cost savings?",
        "choices": [
            {"label": "A", "text": "On-Demand Instances"},
            {"label": "B", "text": "Reserved Instances (1-year term)"},
            {"label": "C", "text": "Spot Instances"},
            {"label": "D", "text": "Dedicated Hosts"}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "Spot Instances offer up to 90% cost savings over On-Demand. Since the workload is fault-tolerant (can be interrupted and restarted) with flexible timing, Spot Instances are the ideal choice."
    },
    {
        "id": "saa106-4",
        "question": "A company needs to run a batch processing job that processes large files stored in Amazon S3. The job runs once per day and typically completes in 30 minutes. What is the MOST cost-effective compute solution?",
        "choices": [
            {"label": "A", "text": "Amazon EC2 Reserved Instances"},
            {"label": "B", "text": "Amazon EC2 Spot Instances"},
            {"label": "C", "text": "AWS Lambda"},
            {"label": "D", "text": "AWS Fargate with Spot capacity"}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "AWS Fargate with Spot capacity is ideal for short-duration batch jobs. It provides containerized execution with automatic scaling and Spot pricing reduces costs by up to 70%. Lambda has a 15-minute timeout limit, making it unsuitable for 30-minute jobs."
    },
    {
        "id": "saa106-5",
        "question": "A solutions architect is designing a web application that must support thousands of concurrent users with minimal latency globally. The application reads from a MySQL database. Which architecture provides the BEST performance?",
        "choices": [
            {"label": "A", "text": "Amazon RDS MySQL with read replicas in multiple Regions"},
            {"label": "B", "text": "Amazon DynamoDB with Global Tables and DynamoDB Accelerator (DAX)"},
            {"label": "C", "text": "Amazon Aurora MySQL with Aurora Global Database"},
            {"label": "D", "text": "Amazon ElastiCache for Memcached in front of Amazon RDS"}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "Aurora Global Database provides sub-second replication across Regions with up to 15 read replicas per Region. It offers better performance and availability than standard RDS read replicas while maintaining MySQL compatibility."
    },
    {
        "id": "saa106-6",
        "question": "A company must encrypt all data at rest in Amazon S3 and rotate encryption keys automatically every 90 days. Which solution meets these requirements?",
        "choices": [
            {"label": "A", "text": "Use S3-managed keys (SSE-S3) with a Lambda function for rotation."},
            {"label": "B", "text": "Use AWS KMS customer managed keys (SSE-KMS) with automatic key rotation enabled."},
            {"label": "C", "text": "Use client-side encryption with a custom key rotation script."},
            {"label": "D", "text": "Use S3 bucket keys with manual rotation."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "SSE-KMS with customer managed keys supports automatic key rotation. For custom rotation intervals like 90 days, you can configure rotation using Lambda triggered by CloudWatch Events. AWS manages the underlying cryptographic operations."
    },
    {
        "id": "saa106-7",
        "question": "An application writes log data to Amazon S3. The logs must be retained for 7 years for compliance but are rarely accessed after 90 days. What is the MOST cost-effective storage strategy?",
        "choices": [
            {"label": "A", "text": "Use S3 Standard and manually move objects to S3 Glacier after 90 days."},
            {"label": "B", "text": "Use S3 Intelligent-Tiering to automatically move objects between tiers."},
            {"label": "C", "text": "Use S3 Standard with a lifecycle policy to transition to S3 Glacier Flexible Retrieval after 90 days."},
            {"label": "D", "text": "Use S3 One Zone-IA for all objects."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "S3 lifecycle policies automatically transition objects to Glacier Flexible Retrieval after 90 days, reducing storage costs by ~95%. Glacier provides low-cost archival storage with retrieval times of minutes to hours, perfect for compliance retention."
    },
    {
        "id": "saa107-1",
        "question": "A company uses Amazon EC2 instances in an Auto Scaling group behind an Application Load Balancer. During traffic spikes, new instances take 10 minutes to become healthy. How can the solutions architect reduce this time?",
        "choices": [
            {"label": "A", "text": "Use larger instance types with more CPU and memory."},
            {"label": "B", "text": "Create a custom AMI with the application pre-installed and configured."},
            {"label": "C", "text": "Enable ALB connection draining."},
            {"label": "D", "text": "Increase the health check interval."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "A custom AMI with the application and dependencies pre-installed eliminates initialization time. Instances launch ready to serve traffic, reducing startup time from minutes to seconds. This is a best practice for Auto Scaling groups."
    },
    {
        "id": "saa107-2",
        "question": "A company needs to share a large dataset (500 GB) stored in Amazon S3 with a partner company's AWS account. The partner should have read-only access for 30 days. What is the MOST secure approach?",
        "choices": [
            {"label": "A", "text": "Generate a pre-signed URL with 30-day expiration."},
            {"label": "B", "text": "Create a cross-account IAM role with S3 read permissions and a time-based condition."},
            {"label": "C", "text": "Make the S3 bucket public for 30 days."},
            {"label": "D", "text": "Copy the data to the partner's S3 bucket."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Cross-account IAM roles with time-based conditions provide fine-grained access control. Roles integrate with IAM policies and support MFA, providing better security and auditability than pre-signed URLs for large-scale access."
    },
    {
        "id": "saa107-3",
        "question": "An application running on EC2 instances must access files stored in Amazon EFS. The instances are in a private subnet. What networking configuration is required?",
        "choices": [
            {"label": "A", "text": "EFS mount targets in the same VPC and subnet as the EC2 instances."},
            {"label": "B", "text": "A NAT Gateway to allow EFS access from private subnets."},
            {"label": "C", "text": "An internet gateway to route traffic to EFS."},
            {"label": "D", "text": "VPC peering between the application VPC and EFS VPC."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "EFS mount targets must be created in the same VPC as the EC2 instances. EFS traffic never leaves the VPC, so no internet gateway or NAT is needed. Security groups control access between instances and mount targets."
    },
    # Additional SAA questions
    {
        "id": "saa107-4",
        "question": "A company wants to migrate an on-premises Oracle database to AWS. The application requires Oracle-specific features such as PL/SQL and Advanced Queuing. Which migration approach should a solutions architect recommend?",
        "choices": [
            {"label": "A", "text": "Use AWS Database Migration Service (DMS) to migrate to Amazon Aurora."},
            {"label": "B", "text": "Use AWS Database Migration Service (DMS) to migrate to Amazon RDS for Oracle."},
            {"label": "C", "text": "Use AWS Schema Conversion Tool (SCT) to convert the schema to PostgreSQL."},
            {"label": "D", "text": "Use Amazon DynamoDB with AWS DMS for real-time migration."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Since the application requires Oracle-specific features (PL/SQL, Advanced Queuing), migrating to Amazon RDS for Oracle maintains compatibility. DMS can handle the data migration with minimal downtime. Aurora and PostgreSQL don't support Oracle-specific features."
    },
    {
        "id": "saa107-5",
        "question": "A web application requires session state to be shared across multiple EC2 instances. The session data must persist even if instances are terminated. Which solution provides the BEST scalability and performance?",
        "choices": [
            {"label": "A", "text": "Store session state in Amazon S3."},
            {"label": "B", "text": "Use sticky sessions on the Application Load Balancer."},
            {"label": "C", "text": "Store session state in Amazon ElastiCache for Redis."},
            {"label": "D", "text": "Store session state on EBS volumes attached to each instance."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "ElastiCache for Redis provides sub-millisecond latency for session storage, supports replication for high availability, and persists data across instance terminations. S3 has higher latency, sticky sessions don't persist, and EBS is instance-specific."
    },
    {
        "id": "saa108-1",
        "question": "A company is deploying a three-tier web application on AWS. The application tier requires the ability to scale horizontally and must communicate with the database tier securely. How should the VPC be designed?",
        "choices": [
            {"label": "A", "text": "Place all tiers in public subnets with security groups for access control."},
            {"label": "B", "text": "Place the web tier in public subnets, and application and database tiers in private subnets."},
            {"label": "C", "text": "Place all tiers in private subnets with a VPN connection for access."},
            {"label": "D", "text": "Place the web and application tiers in public subnets, and only the database tier in a private subnet."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Best practice is to place only the web tier (load balancer) in public subnets, while application and database tiers reside in private subnets for security. Security groups and NACLs control inter-tier communication."
    },
    {
        "id": "saa108-2",
        "question": "A company needs to process real-time streaming data from IoT devices and store the results for analysis. The data volume varies significantly throughout the day. Which architecture is MOST scalable?",
        "choices": [
            {"label": "A", "text": "Amazon Kinesis Data Streams with AWS Lambda for processing and Amazon S3 for storage."},
            {"label": "B", "text": "Amazon SQS with EC2 instances for processing and Amazon RDS for storage."},
            {"label": "C", "text": "Amazon SNS with AWS Lambda for processing and Amazon DynamoDB for storage."},
            {"label": "D", "text": "AWS IoT Core with Amazon EC2 for processing and Amazon EBS for storage."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "Kinesis Data Streams handles real-time streaming data ingestion and scales based on shard count. Lambda provides serverless processing that scales automatically. S3 provides durable, cost-effective storage for analysis."
    },
    {
        "id": "saa108-3",
        "question": "A company hosts a static website on Amazon S3 and wants to improve global performance while restricting direct access to the S3 bucket. Which solution should be implemented?",
        "choices": [
            {"label": "A", "text": "Enable S3 Transfer Acceleration on the bucket."},
            {"label": "B", "text": "Use Amazon CloudFront with an Origin Access Control (OAC) to serve content from S3."},
            {"label": "C", "text": "Create S3 cross-Region replication to multiple Regions."},
            {"label": "D", "text": "Use Amazon Route 53 latency-based routing to multiple S3 buckets."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "CloudFront with OAC caches content at edge locations globally for improved performance, while OAC restricts direct S3 bucket access, ensuring all requests go through CloudFront. Transfer Acceleration helps uploads, not static website delivery."
    },
    {
        "id": "saa108-4",
        "question": "A company has an application that stores sensitive customer data in Amazon RDS. The company needs to ensure that database credentials are not hardcoded in the application and are rotated automatically. Which solution should be used?",
        "choices": [
            {"label": "A", "text": "Store credentials in AWS Systems Manager Parameter Store with automatic rotation."},
            {"label": "B", "text": "Store credentials in AWS Secrets Manager with automatic rotation enabled."},
            {"label": "C", "text": "Store credentials in environment variables on the EC2 instances."},
            {"label": "D", "text": "Store credentials in an encrypted S3 bucket and reference them from the application."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "AWS Secrets Manager is designed specifically for managing database credentials with built-in automatic rotation for RDS databases. Parameter Store supports SecureString but doesn't have native automatic rotation for database credentials."
    },
    {
        "id": "saa108-5",
        "question": "A solutions architect needs to design a disaster recovery solution with an RTO of 1 hour and RPO of 15 minutes for a critical application. Which DR strategy is MOST cost-effective while meeting these requirements?",
        "choices": [
            {"label": "A", "text": "Backup and restore"},
            {"label": "B", "text": "Pilot light"},
            {"label": "C", "text": "Warm standby"},
            {"label": "D", "text": "Multi-site active-active"}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "Warm standby maintains a scaled-down but fully functional copy of the production environment. It can achieve RTO of minutes to an hour and RPO of seconds to minutes. Pilot light may not meet the 1-hour RTO, and multi-site active-active is more expensive than necessary."
    },
    {
        "id": "saa109-1",
        "question": "A company wants to use Amazon S3 to host a data lake. They need to automatically classify and discover sensitive data like PII across all S3 buckets. Which AWS service should be used?",
        "choices": [
            {"label": "A", "text": "Amazon GuardDuty"},
            {"label": "B", "text": "Amazon Macie"},
            {"label": "C", "text": "AWS Config"},
            {"label": "D", "text": "Amazon Inspector"}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Amazon Macie uses machine learning to automatically discover, classify, and protect sensitive data in Amazon S3. It can identify PII, financial data, and other sensitive information. GuardDuty is for threat detection, Inspector for vulnerability assessment, and Config for resource configuration tracking."
    },
    {
        "id": "saa109-2",
        "question": "An application needs to send notifications to multiple subscribers when an order is placed. Some subscribers process the order via Lambda functions, while others queue the order for batch processing. Which architecture pattern is MOST appropriate?",
        "choices": [
            {"label": "A", "text": "Use Amazon SQS with multiple consumers."},
            {"label": "B", "text": "Use Amazon SNS with SQS and Lambda subscriptions (fanout pattern)."},
            {"label": "C", "text": "Use Amazon EventBridge with multiple targets."},
            {"label": "D", "text": "Use Amazon Kinesis Data Streams with multiple consumers."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "The SNS-SQS fanout pattern is ideal for distributing messages to multiple subscribers with different processing needs. SNS pushes to Lambda for real-time processing and to SQS queues for batch processing. This decouples publishers from subscribers."
    },
    {
        "id": "saa109-3",
        "question": "A company runs a containerized microservices application. They want to minimize operational overhead while maintaining the ability to scale individual services independently. Which compute platform should be recommended?",
        "choices": [
            {"label": "A", "text": "Amazon EC2 with Docker installed"},
            {"label": "B", "text": "Amazon ECS with AWS Fargate"},
            {"label": "C", "text": "Amazon EKS with self-managed node groups"},
            {"label": "D", "text": "AWS Elastic Beanstalk with Docker platform"}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Amazon ECS with Fargate eliminates the need to manage underlying infrastructure. Each service can scale independently with task-level auto scaling. EC2 and self-managed node groups require infrastructure management, and Elastic Beanstalk is less flexible for microservices."
    },
    {
        "id": "saa109-4",
        "question": "A company needs to migrate 50 TB of data from on-premises to Amazon S3. The internet connection is 100 Mbps. The migration must be completed within one week. Which solution should be recommended?",
        "choices": [
            {"label": "A", "text": "Upload directly to S3 using the AWS CLI with multipart upload."},
            {"label": "B", "text": "Use AWS Snowball Edge to transfer the data."},
            {"label": "C", "text": "Set up AWS Direct Connect and transfer the data."},
            {"label": "D", "text": "Use S3 Transfer Acceleration for faster uploads."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "At 100 Mbps, transferring 50 TB would take approximately 46 days, far exceeding the one-week deadline. AWS Snowball Edge can handle 50 TB and ships within days. Direct Connect takes weeks to set up, and Transfer Acceleration won't overcome the bandwidth limitation."
    },
    {
        "id": "saa109-5",
        "question": "A solutions architect is designing an application that needs to perform complex queries and joins on structured data. The data grows by approximately 10 GB per day. The application requires ACID compliance. Which database solution is MOST appropriate?",
        "choices": [
            {"label": "A", "text": "Amazon DynamoDB"},
            {"label": "B", "text": "Amazon Aurora"},
            {"label": "C", "text": "Amazon Redshift"},
            {"label": "D", "text": "Amazon DocumentDB"}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Amazon Aurora provides MySQL/PostgreSQL compatibility with ACID compliance, supports complex queries and joins, and can handle the data growth with auto-scaling storage up to 128 TB. DynamoDB is NoSQL without joins, Redshift is for analytics/warehousing, and DocumentDB is document-based."
    },
]

def main():
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {q['id'] for q in existing}
    new_questions = [q for q in NEW_SAA_QUESTIONS if q['id'] not in existing_ids]
    
    print(f"Existing questions: {len(existing)}")
    print(f"New SAA questions to add: {len(new_questions)}")
    
    existing.extend(new_questions)
    existing.sort(key=lambda q: q['id'])
    
    with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    exams = {}
    for q in existing:
        exam = q['id'][:3]
        exams[exam] = exams.get(exam, 0) + 1
    
    print(f"\nTotal questions: {len(existing)}")
    for k, v in sorted(exams.items()):
        print(f"  {k.upper()}: {v}")

if __name__ == '__main__':
    main()
