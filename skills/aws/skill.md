# Skill: AWS

> Loaded into the deep agent's context when a task involves Amazon Web Services —
> scripting against, provisioning, or reasoning about cloud infrastructure. Read
> this first, then `instruction.md` for the procedure and `example.md` for code.

## Purpose

This skill makes the agent effective at working with AWS: writing `boto3`
scripts, drafting infrastructure (CLI / IaC), and giving sound architectural
guidance grounded in the **AWS Well-Architected Framework**. It emphasizes safe
defaults — least privilege, explicit regions, pagination, retries, and cleanup.

## When to use this skill

- Interacting with AWS services programmatically (boto3) or via the AWS CLI.
- Provisioning or describing infrastructure (CloudFormation, CDK, Terraform).
- Architecture advice: choosing services, sizing, cost, reliability, security.
- Debugging AWS errors: access denied, throttling, region/endpoint issues,
  credential resolution.
- Automating deployments, data pipelines, event-driven flows, or storage.

## How AWS access works (mental model)

- **Regions & endpoints.** Most services are regional. Always set the region
  explicitly; never depend on an implicit default that differs per environment.
  A few services are global (IAM, Route 53, CloudFront, parts of S3).
- **Credential provider chain** (boto3/CLI resolve in this order):
  1. Explicitly passed keys (avoid in code).
  2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
     `AWS_SESSION_TOKEN`).
  3. Shared config/credentials files (`~/.aws/credentials`, `~/.aws/config`,
     `AWS_PROFILE`), including SSO.
  4. Container/instance roles (ECS task role, EC2 instance profile / IMDS).
  **Prefer roles and SSO; never hard-code secret keys.**
- **IAM** governs every call: an identity (user/role) must have a policy
  `Allow`ing the `Action` on the `Resource`, with no overriding `Deny`.
- **`client` vs `resource`.** `boto3.client("s3")` is the low-level 1:1 API
  mapping; `boto3.resource("s3")` is a higher-level object interface (not
  available for every service).

## Core toolset

| Tool | Use it for |
|---|---|
| **boto3** (Python SDK) | Programmatic logic, loops, error handling, automation. |
| **AWS CLI** (`aws ...`) | Quick, scriptable one-off operations and shell scripts. |
| **CloudFormation / CDK** | Native, repeatable infrastructure as code. |
| **Terraform** | Multi-cloud / when the org standardizes on it. |
| **SAM / Serverless** | Packaging and deploying Lambda-based apps. |

Match whatever the project already uses.

## Common services quick map

- **S3** — object storage (buckets + keys); static hosting; data lake.
- **EC2** — virtual machines; security groups; AMIs; instance types.
- **Lambda** — serverless functions; event-driven; pay-per-invocation.
- **DynamoDB** — managed NoSQL key/value + document store; single-digit-ms.
- **RDS / Aurora** — managed relational databases.
- **SQS / SNS / EventBridge** — queues / pub-sub / event bus (decoupling).
- **IAM** — identities, roles, policies, permissions.
- **CloudWatch** — logs, metrics, alarms, dashboards.
- **ECS / EKS / Fargate** — containers (orchestrated / serverless).
- **API Gateway** — managed HTTP/REST/WebSocket front door.
- **Step Functions** — serverless workflow orchestration (state machines).
- **Secrets Manager / SSM Parameter Store** — secrets & config.
- **KMS** — managed encryption keys.

## Well-Architected principles (the six pillars, applied)

1. **Operational excellence** — automate with IaC; tag resources; log and
   monitor; make deployments repeatable.
2. **Security** — least privilege IAM; no hard-coded secrets; encrypt at rest
   (SSE/KMS) and in transit (TLS); private subnets for data tiers.
3. **Reliability** — design for failure: retries with backoff, idempotency,
   multi-AZ, health checks, waiters for eventual consistency.
4. **Performance efficiency** — right-size instances; pick the right service;
   use caching (CloudFront/ElastiCache) and the right storage class.
5. **Cost optimization** — note the cost of every persistent resource; prefer
   serverless/managed where it lowers total cost; clean up demos.
6. **Sustainability** — avoid idle/over-provisioned resources.

## Operational rules that prevent bugs

- **Set the region explicitly** on every client/session.
- **Paginate** all list/describe operations — results are truncated by default.
- **Handle `ClientError`** and inspect the error **code**, not the string.
- **Use waiters** for resources that take time to become ready/deleted.
- **Idempotency** — design retries to be safe (client tokens, conditional puts).
- **Tag** every created resource (project, environment, owner) for tracking/cost.
- **Treat delete/terminate/overwrite as irreversible** — list/confirm first.

## Companion files

- `instruction.md` — the step-by-step procedure for any AWS task, with security
  and cleanup guardrails.
- `example.md` — worked `boto3` and CLI examples (S3, EC2, Lambda, DynamoDB,
  SQS) plus a least-privilege IAM policy and retry config.
