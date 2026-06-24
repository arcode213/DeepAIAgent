# Examples: AWS Skill

Worked `boto3` and CLI examples with safe defaults: explicit region, pagination,
`ClientError` handling, retries, waiters, tagging, and least-privilege IAM.

---

## Example 1 — Upload a file to S3 (boto3)

```python
import boto3
from botocore.exceptions import ClientError


def upload_file(local_path: str, bucket: str, key: str, region: str = "us-east-1") -> bool:
    """Upload a local file to S3. Returns True on success, False on failure."""
    s3 = boto3.client("s3", region_name=region)
    try:
        s3.upload_file(local_path, bucket, key)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        print(f"Upload failed [{code}]: {exc}")
        return False
    return True
```

## Example 2 — List every object with pagination

```python
import boto3


def list_all_keys(bucket: str, prefix: str = "", region: str = "us-east-1") -> list[str]:
    """Return every object key under a prefix, handling pagination."""
    s3 = boto3.client("s3", region_name=region)
    paginator = s3.get_paginator("list_objects_v2")
    keys: list[str] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys
```

## Example 3 — Launch an EC2 instance and wait until running

```python
import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")
resp = ec2.run_instances(
    ImageId="ami-xxxxxxxx",
    InstanceType="t3.micro",
    MinCount=1, MaxCount=1,
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [
            {"Key": "Project", "Value": "demo"},
            {"Key": "Environment", "Value": "dev"},
        ],
    }],
)
instance_id = resp["Instances"][0]["InstanceId"]

# Waiter blocks until the instance reaches the running state.
ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
print(f"{instance_id} is running")
```

## Example 4 — DynamoDB put/get with adaptive retries

```python
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

cfg = Config(retries={"max_attempts": 10, "mode": "adaptive"})
ddb = boto3.client("dynamodb", region_name="us-east-1", config=cfg)


def put_user(user_id: str, name: str) -> None:
    ddb.put_item(
        TableName="users",
        Item={"id": {"S": user_id}, "name": {"S": name}},
        ConditionExpression="attribute_not_exists(id)",  # idempotent insert
    )


def get_user(user_id: str) -> dict | None:
    try:
        resp = ddb.get_item(TableName="users", Key={"id": {"S": user_id}})
    except ClientError as exc:
        print(f"get_item failed: {exc.response['Error']['Code']}")
        raise
    return resp.get("Item")
```

## Example 5 — Invoke a Lambda function

```python
import json
import boto3

lambda_client = boto3.client("lambda", region_name="us-east-1")
resp = lambda_client.invoke(
    FunctionName="my-fn",
    InvocationType="RequestResponse",
    Payload=json.dumps({"key": "value"}).encode("utf-8"),
)
result = json.loads(resp["Payload"].read())
print(result)
```

## Example 6 — Send a message to SQS

```python
import boto3

sqs = boto3.client("sqs", region_name="us-east-1")
queue_url = sqs.get_queue_url(QueueName="jobs")["QueueUrl"]
sqs.send_message(QueueUrl=queue_url, MessageBody="process order 123")
```

---

## Example 7 — Equivalent AWS CLI commands

```bash
# Copy a file to S3 (region explicit)
aws s3 cp ./report.pdf s3://my-bucket/reports/report.pdf --region us-east-1

# List objects under a prefix
aws s3 ls s3://my-bucket/reports/ --region us-east-1

# Invoke a Lambda function
aws lambda invoke --function-name my-fn \
    --payload '{"key":"value"}' out.json --region us-east-1

# Describe running EC2 instances (server-side filter)
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" --region us-east-1

# Who am I / which identity is in use
aws sts get-caller-identity
```

---

## Example 8 — A least-privilege IAM policy (read one bucket)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOneBucket",
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ]
  }]
}
```

Note the **two ARNs**: `ListBucket` acts on the bucket; `GetObject` acts on the
objects (`/*`). Scope actions and resources — avoid `"*"`.

---

## Example 9 — Using a named profile / session

```python
import boto3

session = boto3.Session(profile_name="dev", region_name="us-east-1")
s3 = session.client("s3")
identity = session.client("sts").get_caller_identity()
print(identity["Arn"])  # confirm which identity you're operating as
```

---

## What these demonstrate

- Explicit `region_name` on every client/session.
- Paginators for list operations instead of assuming a single response.
- `ClientError` handling that inspects the error **code**.
- Adaptive retry config for throttling-prone services.
- Waiters for eventually-ready resources; conditional writes for idempotency.
- Resource tagging and a scoped (not `"*"`) IAM policy.
- `sts get-caller-identity` to confirm the active identity before acting.
