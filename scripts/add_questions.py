#!/usr/bin/env python3
"""Add new SOA questions from web sources to questions.json"""
import json
import os

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'questions.json')

# New SOA questions collected from free web sources
NEW_SOA_QUESTIONS = [
    # --- Whizlabs Q1-Q25 (SOA Domain questions) ---
    {
        "id": "soa101-1",
        "question": "A pharma company has deployed a new web application on multiple Amazon EC2 instances behind an Application Load Balancer and is protected by AWS WAF. The Security Operations team was observing spam traffic from an IP address and instructed you to block immediately. Further checks found that this IP address is accessing web applications from behind the proxy server. Which is the correct rule that can be applied to meet this requirement?",
        "choices": [
            {"label": "A", "text": "Configure WAF rate-based rules to block matching IP addresses for web request origin."},
            {"label": "B", "text": "Configure WAF rate-based rules to block matching IP addresses from the X-Forwarded-For HTTP header."},
            {"label": "C", "text": "Configure WAF rule to block matching IP address from X-Forwarded-For HTTP header."},
            {"label": "D", "text": "Configure WAF rule to block matching IP address for web request origin."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "AWS WAF has regular rules and rate-based rules. Since the IP needs to be blocked immediately (not rate-based) and is behind a proxy server, the originating client IP is in the X-Forwarded-For HTTP header, not the web request origin. A regular WAF rule matching X-Forwarded-For is the correct approach."
    },
    {
        "id": "soa101-2",
        "question": "A Multinational IT firm has a large number of AWS accounts working on various projects, all part of AWS Organizations. The Operations Team is facing difficulties in enforcing policies across all these multiple accounts and detecting non-conforming resources. Which service is best suited to be implemented along with AWS Organizations to meet this requirement?",
        "choices": [
            {"label": "A", "text": "AWS Control Tower"},
            {"label": "B", "text": "AWS Security Hub"},
            {"label": "C", "text": "AWS Service Catalog"},
            {"label": "D", "text": "AWS Systems Manager"}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "AWS Control Tower is best suited for setting up and governing a multi-account AWS environment. It automates creation of multi-account setups using Landing Zone, automates policy management using guardrails, and provides an integrated dashboard."
    },
    {
        "id": "soa101-3",
        "question": "An ECS cluster running on docker containers is launched using AWS Fargate Launch type. The Operations Team is looking for traffic logs between each of the tasks. Which is the correct interface on which VPC flow logs can be applied?",
        "choices": [
            {"label": "A", "text": "Apply VPC flow logs on the docker virtual interface to monitor traffic between each task."},
            {"label": "B", "text": "Apply VPC flow logs on Amazon EC2 instance secondary ENI to monitor traffic between each task."},
            {"label": "C", "text": "Apply VPC flow logs on ENI of the Amazon ECS task to monitor traffic between each task."},
            {"label": "D", "text": "Apply VPC flow logs on Amazon EC2 instance primary ENI to monitor traffic between each task."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "Default networking mode for AWS Fargate launch type is awsvpc, in which each Amazon ECS task gets a separate ENI. VPC Flow Logs can be applied at the ENI of each task to monitor traffic between tasks."
    },
    {
        "id": "soa101-4",
        "question": "Your team uses a CloudFormation stack with a large amount of AWS resources including Auto Scaling groups, Lambda functions, Security groups and Route 53 domain names. You want to divide the template into several parts while managing all resources in a single stack. Which option is most appropriate?",
        "choices": [
            {"label": "A", "text": 'Ensure the stack template uses YAML format and uses the "—" symbol to divide the template into several partitions.'},
            {"label": "B", "text": 'Use the "AWS::CloudFormation::Stack" resources to divide the stack into several nested stacks.'},
            {"label": "C", "text": 'Use the "AWS::CloudFormation::SubStack" resources to create sub-stacks and export values for other stacks to import.'},
            {"label": "D", "text": 'Divide the stack into a CloudFormation StackSet by using the "AWS::CloudFormation::StackSet" resource.'}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "With nested stacks (AWS::CloudFormation::Stack), the whole stack is divided into different stacks, and outputs from one stack can be used as inputs to another. There is no SubStack resource, and StackSet is for deploying across multiple accounts/regions."
    },
    {
        "id": "soa101-5",
        "question": "A Financial firm wants to deploy a new version of their application using Elastic Beanstalk without any service impact, with ability to quickly rollback, and initially only 10% of traffic should be diverted to the new version. Which deployment policy should be used?",
        "choices": [
            {"label": "A", "text": "Use Traffic splitting deployment policy."},
            {"label": "B", "text": "Use Rolling deployment policy."},
            {"label": "C", "text": "Use Immutable deployment policy."},
            {"label": "D", "text": "Use Rolling with an additional batch deployment policy."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "Traffic splitting deployment policy launches a full set of EC2 instances in a new Auto Scaling group. Post deployment, a certain percentage of traffic can be diverted to the new setup. It's easy to rollback since traffic can be diverted back to the old version."
    },
    {
        "id": "soa102-1",
        "question": "You have an EC2 instance in production with a software issue. You need to take an AMI using AWS CLI without rebooting the instance. Which CLI command would you use?",
        "choices": [
            {"label": "A", "text": 'aws ec2 create-image --instance-id i-01234567890123456 --name "My_Image" --reboot'},
            {"label": "B", "text": 'aws ec2 create-image --instance-id i-01234567890123456 --name "My_Image" --no-reboot'},
            {"label": "C", "text": 'aws ec2 create-image --instance-id i-01234567890123456 --name "My_Image" --no-dry-run'},
            {"label": "D", "text": 'aws ec2 create-image --instance-id i-01234567890123456 --name "My_Image"'}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "The --no-reboot option ensures that the EC2 instance does not reboot during image creation. Without this option, EC2 will reboot the instance by default. --no-dry-run controls whether the operation is executed, not rebooting."
    },
    {
        "id": "soa102-2",
        "question": "You're planning to allow an Administrator to set up an EC2 Instance that needs access to a DynamoDB table. Which policy permissions are required to ensure this implementation can be carried out securely? (Select TWO)",
        "choices": [
            {"label": "A", "text": "A trust policy that allows the EC2 Instance to assume a role."},
            {"label": "B", "text": "A trust policy that allows the user to assume a role."},
            {"label": "C", "text": "An IAM permission policy that allows the user to assume a role."},
            {"label": "D", "text": "An IAM permission policy that allows the user to pass a role."}
        ],
        "answer": ["A", "D"],
        "multiSelect": True,
        "explanation": "A trust policy allows the EC2 service to assume the role, and an IAM permission policy allows the user to pass the role to the EC2 instance. The trust policy is used with AWS services, and iam:PassRole permission is needed for the user."
    },
    {
        "id": "soa102-3",
        "question": "A global financial institution has deployed EC2 instances and Amazon DynamoDB in us-west-1 and ap-northeast-1. They need database tables fully redundant so failure in one region doesn't impact the web application. Which solution provides high availability between these two regions?",
        "choices": [
            {"label": "A", "text": "Copy Data from source DynamoDB table to destination region DynamoDB using Amazon EBS snapshots."},
            {"label": "B", "text": "Copy Data from source DynamoDB table to destination region DynamoDB using Amazon S3 buckets."},
            {"label": "C", "text": "Use code to replicate data changes for DynamoDB tables between these two regions."},
            {"label": "D", "text": "Create a DynamoDB global table to replicate DynamoDB tables between different regions."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "Amazon DynamoDB Global Tables can automatically replicate data from one region to another region. Other options would work but add unnecessary administrative overhead."
    },
    {
        "id": "soa102-4",
        "question": "A global pharma company applied SCP at the OU level to deny all access to an Amazon S3 bucket, but external vendors can still access the S3 bucket. What could be the possible reason?",
        "choices": [
            {"label": "A", "text": "SCP does not apply to users outside the AWS Organizations."},
            {"label": "B", "text": "SCP needs to be applied at account level instead of OU level."},
            {"label": "C", "text": "SCP needs to be applied at root level instead of OU level."},
            {"label": "D", "text": "IAM Policy needs to be created to explicitly deny access to Amazon S3 bucket along with SCP."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "SCPs affect principals of all accounts within the organization. They do not apply to external users who have permissions to resources but are not part of accounts within the AWS Organizations."
    },
    {
        "id": "soa102-5",
        "question": "A team has developed an application that works with a DynamoDB table and it will be hosted on an EC2 Instance. Which approach ensures the application has proper permissions to access the DynamoDB table?",
        "choices": [
            {"label": "A", "text": "Create an IAM user with the required permissions and ensure the application runs on behalf of the user on the EC2 instance."},
            {"label": "B", "text": "Create an IAM group with the required permissions and ensure the application runs on behalf of the group on the EC2 instance."},
            {"label": "C", "text": "Create an IAM Role with the required permissions and ensure that the Role is assigned to the EC2 Instance."},
            {"label": "D", "text": "Create Access keys with the required permissions and ensure that the Access keys are embedded in the application."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "IAM Roles should be used to provide EC2 instances with permissions to access AWS services. Using IAM users or embedding access keys is not secure."
    },
    {
        "id": "soa103-1",
        "question": "The Development Team is attaching an encrypted Cold HDD Amazon EBS volume to an existing m5.large EC2 instance, but the attachment is failing. What could be a possible reason?",
        "choices": [
            {"label": "A", "text": "Cold HDD volume type does not support encryption."},
            {"label": "B", "text": "Instance type m5.large does not support encrypted EBS volumes."},
            {"label": "C", "text": "Default KMS key is used for encryption of Amazon EBS volumes."},
            {"label": "D", "text": "CMK key status used for encryption is in disabled state."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "The CMK Key used for encryption of Amazon EBS volume must be in Enabled state. If the key is disabled, attaching an encrypted EBS volume to an EC2 instance will fail. All EBS volumes support encryption, and all current generation EC2 instances support encrypted volumes."
    },
    {
        "id": "soa103-2",
        "question": "A bank uses Amazon CloudWatch logs to capture logs from EC2 instances. A metric filter for error messages intermittently reports no data. What setting can resolve this issue?",
        "choices": [
            {"label": "A", "text": "Set Default Value in the metric filter as 0."},
            {"label": "B", "text": "Set dimensions value in the metric filter as 0."},
            {"label": "C", "text": "Set metric value in the metric filter as 0."},
            {"label": "D", "text": "Set filter pattern in the metric filter as 0."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "Default Value is the value reported when no matching logs are found with a metric filter. By setting Default Value as 0, metric data can always be reported even if there are no matching logs."
    },
    {
        "id": "soa103-3",
        "question": "A start-up has 4 VPCs. VPC-3 and VPC-4 are production, VPC-1 and VPC-2 are test. The Development Team needs to ensure Lambda functions only use VPC-1 and VPC-2. Which setting should be configured?",
        "choices": [
            {"label": "A", "text": "Use IAM Condition keys to specify VPC to be used by Lambda function."},
            {"label": "B", "text": "Specify VPC ID of VPC-1 & VPC-2 to be used as input parameters to the CreateFunction request."},
            {"label": "C", "text": "Deny VPC ID of VPC-3 & VPC-4 as input parameter to the CreateFunction request."},
            {"label": "D", "text": 'Use IAM "aws:SourceVpce" to specify VPC to be used by Lambda function.'}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "AWS Lambda uses Condition keys like lambda:VpcIds to allow or deny specific VPCs, lambda:SubnetIds for subnets, and lambda:SecurityGroupIds for security groups. VPC ID cannot be specified as an input parameter, and aws:SourceVpce is not supported by Lambda."
    },
    {
        "id": "soa103-4",
        "question": "A company uses the Storage Gateway service to extend storage capacity to AWS Cloud. All data must be encrypted at rest by the AWS Storage Gateway. Which solution should be implemented?",
        "choices": [
            {"label": "A", "text": "Create an X.509 certificate that can be used to encrypt the data."},
            {"label": "B", "text": "Use AWS KMS service to support encryption of the data."},
            {"label": "C", "text": "Use an SSL certificate to encrypt the data."},
            {"label": "D", "text": "Use your own master keys to encrypt the data."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "AWS Storage Gateway uses AWS Key Management Service (KMS) to support encryption. Storage Gateway is integrated with AWS KMS, allowing you to use customer master keys (CMKs) to protect data. If KMS is not used, data is encrypted with SSE-S3 by default."
    },
    {
        "id": "soa103-5",
        "question": "Your company has DynamoDB tables and needs monitoring reports on Read and Write Capacity utilization. How can you accomplish this?",
        "choices": [
            {"label": "A", "text": "Use CloudWatch logs to see the amount of Read and Write Capacity being utilized."},
            {"label": "B", "text": "Use CloudWatch metrics to see the amount of Read and Write Capacity being utilized."},
            {"label": "C", "text": "Use CloudTrail logs to see the amount of Read and Write Capacity being utilized."},
            {"label": "D", "text": "Use AWS Config logs to see the amount of Read and Write Capacity being utilized."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "CloudWatch metrics provide DynamoDB utilization data including Read and Write Capacity. CloudWatch logs won't give capacity consumption, CloudTrail is for API monitoring, and AWS Config is for configuration management."
    },
    {
        "id": "soa104-1",
        "question": "Your team has an Auto Scaling Group managing EC2 Instances but there are issues with the application that need debugging. What should be done?",
        "choices": [
            {"label": "A", "text": "Delete the Auto Scaling Group so that you can investigate the underlying Instances."},
            {"label": "B", "text": "Delete the Launch Configuration so that you can investigate the underlying Instances."},
            {"label": "C", "text": "Suspend the scaling process so that you can investigate the underlying Instances."},
            {"label": "D", "text": "Use AWS Config to take a configuration snapshot of the Instances and then investigate."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "You can suspend and resume scaling processes for your Auto Scaling group. This is useful when investigating configuration problems without invoking scaling processes. Deleting the ASG or Launch Configuration would disrupt the application."
    },
    {
        "id": "soa104-2",
        "question": "You have an EBS-backed EC2 Instance that needs to be upgraded to a higher instance type. How can you achieve this?",
        "choices": [
            {"label": "A", "text": "Directly change the instance type from the AWS Console."},
            {"label": "B", "text": "Stop the Instance and then change the Instance Type."},
            {"label": "C", "text": "Detach the underlying EBS volumes and then change the Instance Type."},
            {"label": "D", "text": "Detach the underlying ENI and then change the Instance Type."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "EBS-backed instances must be stopped before changing the instance type. You cannot change the instance type while the instance is running."
    },
    {
        "id": "soa104-3",
        "question": "Your team plans to use AWS Backup to centralize backups. Backups need to be separated into different categories with each container having its own KMS key. How would you achieve this?",
        "choices": [
            {"label": "A", "text": "Organize backups into different S3 buckets and enable Server-Side Encryption with SSE-KMS."},
            {"label": "B", "text": "Organize backups into different AWS Backup vaults with their own KMS keys."},
            {"label": "C", "text": "Organize backups with different tags and associate a KMS key with each tag."},
            {"label": "D", "text": "Organize backups with different backup plans and configure a dedicated KMS key for each backup plan."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "AWS Backup uses vaults to store backups, not S3 buckets. You can create several AWS Backup vaults and choose a different KMS key for each vault. You cannot associate KMS keys with tags or backup plans."
    },
    {
        "id": "soa104-4",
        "question": "The team is configuring a WAF ACL for an Application Load Balancer and needs to check which requests were blocked, allowed, or counted. Which option is suitable?",
        "choices": [
            {"label": "A", "text": "In CloudWatch metrics, view the request details for the WAF ACL."},
            {"label": "B", "text": "In the AWS WAF console, enable request sampling for the WAF ACL and view the detailed data of the sample requests."},
            {"label": "C", "text": "Enable VPC flow logs, create a log filter for the WAF ACL, and view the request details."},
            {"label": "D", "text": "Enable WAF logs and save the logs in an S3 bucket. Use Athena to analyze the details."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "In the AWS WAF console, you can enable request sampling and view detailed data of sampled requests to determine whether rules work as expected. CloudWatch metrics don't show request details, and VPC flow logs don't contain WAF-filtered request details."
    },
    {
        "id": "soa104-5",
        "question": "You need to host a vendor-based product on an EC2 Instance. Due to the licensing model, you need control over the number of cores of the underlying hardware. Which option should you consider?",
        "choices": [
            {"label": "A", "text": "Reserved Instances"},
            {"label": "B", "text": "Dedicated Instances"},
            {"label": "C", "text": "Spot Instances"},
            {"label": "D", "text": "Dedicated Hosts"}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "Amazon EC2 Dedicated Hosts are physical servers fully dedicated for your use, giving you visibility and control over how instances are placed, including the number of cores. This enables using existing server-bound software licenses."
    },
    {
        "id": "soa105-1",
        "question": "Your company wants to be notified when coming close to their monthly budget for AWS resource costs. How could you achieve this?",
        "choices": [
            {"label": "A", "text": "Create an alarm based on the costing metrics for a collection of resources."},
            {"label": "B", "text": "Create a billing alarm from within CloudWatch."},
            {"label": "C", "text": "Create a billing alarm from within Cost Explorer."},
            {"label": "D", "text": "Create a billing alarm from within IAM."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "You can monitor estimated AWS charges using Amazon CloudWatch. When monitoring of estimated charges is enabled, charges are calculated and sent to CloudWatch as metric data. Billing alarms must be created from CloudWatch."
    },
    {
        "id": "soa105-2",
        "question": "There is a three-tier Web Application behind an ALB. Auto Scaling Group is created for EC2 to scale-out when CPU > 75%. EC2 instances are spread across multiple AZs. The operational Director wants aggregate CPU utilization for all EC2 instances in this Auto Scaling group. Which CloudWatch Metric setting should be used?",
        "choices": [
            {"label": "A", "text": 'Enable "CPU Utilization" metric for each EC2 instance in Auto Scaling Group and aggregate these values.'},
            {"label": "B", "text": 'Enable "CPU Utilization" metric for each EC2 instance within each AZ for Auto Scaling Group.'},
            {"label": "C", "text": 'Enable "CPU Utilization" metric for EC2 with dimension as "AutoScalingGroupName".'},
            {"label": "D", "text": 'Enable "CPU Utilization" metric for EC2 within each AZ with dimension as "AutoScalingGroupName".'}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "For aggregate metrics across all EC2 instances in an Auto Scaling group, use the dimension 'AutoScalingGroupName'. This automatically aggregates across all instances regardless of Availability Zone."
    },
    {
        "id": "soa105-3",
        "question": "Your company has 2 AWS accounts with individual VPCs in different regions with non-overlapping CIDR blocks. They need to communicate. Which is the most cost-effective connectivity option?",
        "choices": [
            {"label": "A", "text": "Use VPN connections."},
            {"label": "B", "text": "Use VPC peering between the 2 VPCs."},
            {"label": "C", "text": "Use AWS Direct Connect."},
            {"label": "D", "text": "Use a NAT gateway."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "VPC peering enables routing traffic privately between VPCs, even across different regions and AWS accounts. It uses existing VPC infrastructure with no single point of failure. VPN and Direct Connect are more complex and costly for this use case."
    },
    {
        "id": "soa105-4",
        "question": "You have a fleet of Linux EC2 Instances needing a shared data store with consistent read view. Item sizes vary from 1KB to 300MB, max data store size 3TB. Which is the ideal data store?",
        "choices": [
            {"label": "A", "text": "Elastic File System"},
            {"label": "B", "text": "Amazon S3"},
            {"label": "C", "text": "Amazon EBS Volumes"},
            {"label": "D", "text": "Amazon DynamoDB"}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "Amazon EFS provides a file system interface with strong consistency and file locking, accessible by thousands of EC2 instances simultaneously. S3 is for object storage, EBS is for local block storage, and DynamoDB is not suitable for large file sizes."
    },
    {
        "id": "soa105-5",
        "question": "You need to save customer transactions for seven years in S3 Glacier and ensure no changes or deletion can be made while allowing read access. Which policy should be enforced?",
        "choices": [
            {"label": "A", "text": "Vault Access Policy"},
            {"label": "B", "text": "S3 Bucket Policy"},
            {"label": "C", "text": "Glacier Control Policy"},
            {"label": "D", "text": "Vault Lock Policy"}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "A Vault Lock Policy can be locked to prevent future changes, providing strong enforcement for compliance controls. Vault Access Policy is for non-compliance related controls that may change. S3 Bucket Policy is for S3 resources, and there is no 'Glacier Control Policy'."
    },
    {
        "id": "soa106-1",
        "question": "Operations Team observed that critical vaults were deleted from Amazon S3 Glacier using AWS CLI. They need details of the users who performed these operations, specifically the time of deletion and source IP address. Which service can provide this?",
        "choices": [
            {"label": "A", "text": "Create an Amazon CloudTrail trail to log data events."},
            {"label": "B", "text": "Create an Amazon CloudTrail trail to log all events."},
            {"label": "C", "text": "Create an AWS Config rule."},
            {"label": "D", "text": "Create AWS Trusted Advisor checks."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "Amazon S3 Glacier is integrated with CloudTrail. A trail logging all events captures API actions like describe/delete/create vaults, including time and user details. Data events are for S3 object-level operations and Lambda invocations, not Glacier vault operations."
    },
    # --- Medium article SOA questions ---
    {
        "id": "soa106-2",
        "question": "A company plans to use AWS CloudFormation to deploy multiple environments across multiple AWS Regions using a single template. What is the recommended approach?",
        "choices": [
            {"label": "A", "text": "Use nested stacks to provision the resources."},
            {"label": "B", "text": "Use change sets to provision additional environments."},
            {"label": "C", "text": "Use parameters to provision the resources."},
            {"label": "D", "text": "Use cross-stack references to provision the resources."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "You can use parameters to pass values to your CloudFormation template when creating or updating a stack to customize each deployment for different environments and regions."
    },
    {
        "id": "soa106-3",
        "question": "How can a SysOps Administrator easily identify potential cost savings by downsizing underutilized Amazon EC2 instances with MINIMAL effort?",
        "choices": [
            {"label": "A", "text": "Use Amazon CloudWatch metrics to identify EC2 instances with low utilization."},
            {"label": "B", "text": "Run an AWS Lambda function that checks for utilization of EC2 instances."},
            {"label": "C", "text": "Use AWS Budgets to generate alerts for underutilized EC2 instances."},
            {"label": "D", "text": "Use AWS Cost Optimization Hub to generate resource optimization recommendations."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "AWS Cost Optimization Hub helps consolidate and prioritize cost optimization recommendations across AWS Organizations accounts and Regions, including EC2 instance rightsizing recommendations."
    },
    {
        "id": "soa106-4",
        "question": "How can a company ensure each department operates within its own isolated environment while only allowing pre-approved AWS services?",
        "choices": [
            {"label": "A", "text": "Use an AWS Organization to create accounts for each department and apply service control policies (SCPs) to control access."},
            {"label": "B", "text": "Create IAM policies for each department that grant access to specific services."},
            {"label": "C", "text": "Create a catalog of approved services in AWS Service Catalog."},
            {"label": "D", "text": "Create Security Groups to isolate departments and configure IAM policies to restrict access."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "AWS Organizations with Service Control Policies (SCPs) provides both account-level isolation and service restriction across departments. SCPs are the proper tool for controlling which AWS services can be used per account."
    },
    {
        "id": "soa106-5",
        "question": "Multiple offices worldwide upload data weekly to Amazon S3. Latency issues are impeding the upload process. What is the SIMPLEST way to improve upload times?",
        "choices": [
            {"label": "A", "text": "Upload to a local Amazon S3 bucket within each region and enable Cross-Region Replication (CRR)."},
            {"label": "B", "text": "Use S3 Multi-part upload."},
            {"label": "C", "text": "Utilize a traditional file transfer protocol (FTP) for the uploads."},
            {"label": "D", "text": "Upload using Amazon S3 Transfer Acceleration."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "Amazon S3 Transfer Acceleration can speed up content transfers by 50-500% for long-distance transfers. Multi-part upload performs parallel uploads but doesn't address latency like Transfer Acceleration does."
    },
    {
        "id": "soa107-1",
        "question": "How can a SysOps Administrator prevent accidentally terminating several critical Amazon EC2 instances?",
        "choices": [
            {"label": "A", "text": "Use AWS Systems Manager to restrict EC2 termination."},
            {"label": "B", "text": "Use AWS Config to restrict EC2 termination."},
            {"label": "C", "text": "Disable all user access to the Amazon EC2 instances in the AWS Console."},
            {"label": "D", "text": "Enable termination protection on the EC2 instances."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "If EC2 termination protection is enabled, the instance can't be terminated using the console, API, or CLI until protection is disabled. By default, this option is turned off."
    },
    {
        "id": "soa107-2",
        "question": "A company needs to securely manage one-time fixed license keys in AWS. The development team needs to access them in automation scripts on EC2 instances and CloudFormation stacks. Which solution is MOST cost-effective?",
        "choices": [
            {"label": "A", "text": 'Amazon S3 Glacier with encrypted files prefixed with "config".'},
            {"label": "B", "text": "AWS Secrets Manager secrets with a tag named SecretString."},
            {"label": "C", "text": "AWS Systems Manager Parameter Store SecureString parameters."},
            {"label": "D", "text": "CloudRotation parameters."}
        ],
        "answer": ["C"],
        "multiSelect": False,
        "explanation": "AWS Systems Manager Parameter Store SecureString parameters provide secure, scalable storage for configuration data including license keys. Secrets Manager is better for secrets requiring rotation and is more expensive. Parameter Store is more cost-effective for static secrets."
    },
    {
        "id": "soa107-3",
        "question": "A serverless application on AWS Lambda uses Amazon RDS for MySQL and encounters frequent 'too many connections' errors. The max_connections value is already maximized. What should a SysOps administrator do?",
        "choices": [
            {"label": "A", "text": "Modify the Lambda function to use Amazon DynamoDB instead of MySQL RDS."},
            {"label": "B", "text": "Scale up the Lambda function's memory to a higher value."},
            {"label": "C", "text": "Re-adjust the max_connect_errors parameter in the database's parameter group."},
            {"label": "D", "text": "Deploy an Amazon RDS Proxy to create a proxy layer and update the Lambda function's connection string."}
        ],
        "answer": ["D"],
        "multiSelect": False,
        "explanation": "Amazon RDS Proxy pools and reuses database connections, reducing the number of connections Lambda functions need. Instead of creating a new connection per request, RDS Proxy efficiently handles concurrent connections."
    },
    {
        "id": "soa107-4",
        "question": "A company wants to provision AWS accounts for each team with predefined baselines and governance policies in a scalable and efficient manner. Which action should be taken?",
        "choices": [
            {"label": "A", "text": "Use AWS Control Tower to create a template in Account Factory and use it to provision new accounts."},
            {"label": "B", "text": "Automate using AWS CloudFormation to provision accounts, set up infrastructure, and integrate with AWS Organizations."},
            {"label": "C", "text": "Use AWS Config to provision accounts and deploy instances using AWS Service Catalog."},
            {"label": "D", "text": "Use AWS Elastic Beanstalk to provision accounts and deploy instances using AWS Service Catalog."}
        ],
        "answer": ["A"],
        "multiSelect": False,
        "explanation": "AWS Control Tower's Account Factory allows creating account templates that enforce predefined baselines and governance policies. AWS Config is for resource inventory, Elastic Beanstalk is for application deployment, and CloudFormation lacks the governance features of Control Tower."
    },
    {
        "id": "soa107-5",
        "question": "Amazon Glacier will be used to archive data with a requirement to retain data for a minimum of 7 years. Which configuration option should be used?",
        "choices": [
            {"label": "A", "text": "A Glacier data retrieval policy."},
            {"label": "B", "text": "A Glacier vault lock policy."},
            {"label": "C", "text": "A Glacier vault access policy."},
            {"label": "D", "text": "A Glacier vault notification."}
        ],
        "answer": ["B"],
        "multiSelect": False,
        "explanation": "A Vault Lock Policy enforces compliance controls by denying deletion of archives less than a specified number of days old using the glacier:ArchiveAgeInDays condition key. Once locked, the policy cannot be changed."
    },
]

def main():
    # Load existing questions
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {q['id'] for q in existing}
    
    # Filter out duplicates
    new_questions = [q for q in NEW_SOA_QUESTIONS if q['id'] not in existing_ids]
    
    print(f"Existing questions: {len(existing)}")
    print(f"New questions to add: {len(new_questions)}")
    
    # Add new questions
    existing.extend(new_questions)
    
    # Sort by id
    existing.sort(key=lambda q: q['id'])
    
    # Write back
    with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Count by exam
    exams = {}
    for q in existing:
        exam = q['id'][:3]
        exams[exam] = exams.get(exam, 0) + 1
    
    print(f"\nTotal questions: {len(existing)}")
    for k, v in sorted(exams.items()):
        print(f"  {k.upper()}: {v}")

if __name__ == '__main__':
    main()
