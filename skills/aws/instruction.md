# Instructions: AWS Skill

The procedure the deep agent follows for any AWS task. Safety first: AWS actions
cost money and can be irreversible.

---

## Phase 1 — Establish context

- Identify the target service(s) and the **exact** operation: read, list,
  create, update, delete.
- Determine the **region** and **account/profile**. State the assumption if the
  user didn't specify (e.g. "assuming `us-east-1` and the default profile").
- Confirm how credentials are provided (env vars, named profile, SSO, IAM role).
  **Never** ask the user to paste secret keys or embed them in code.
- Establish blast radius: is this a personal sandbox, a shared dev account, or
  production? Raise the caution level accordingly.

## Phase 2 — Choose the interface

- One-off / exploratory / shell script → **AWS CLI**.
- Programmatic logic, loops, conditional handling, retries → **boto3**.
- Repeatable, version-controlled, reviewable infrastructure → **IaC**
  (CloudFormation / CDK / Terraform). Prefer this for anything that should
  persist or be reproduced.
- Match the project's existing approach before introducing a new one.

## Phase 3 — Read before you write

- For mutating tasks, **first run a read-only operation** to validate
  assumptions about current state (does the bucket exist? what's the instance
  state? is the item already present?).
- This prevents acting on a wrong mental model and catches permission problems
  early with a harmless call.

## Phase 4 — Write the code / commands

Apply these defaults every time:

- **Explicit region:** `boto3.client("s3", region_name="us-east-1")` or a
  `boto3.Session(profile_name=..., region_name=...)`.
- **Pagination:** use paginators for list/describe; never assume one call
  returns everything.

  ```python
  paginator = client.get_paginator("list_objects_v2")
  for page in paginator.paginate(Bucket=bucket):
      ...
  ```

- **Error handling:** catch `botocore.exceptions.ClientError` and branch on
  `exc.response["Error"]["Code"]` (e.g. `"NoSuchKey"`, `"AccessDenied"`,
  `"ThrottlingException"`). Let truly unexpected errors propagate.
- **Retries/backoff:** rely on botocore's adaptive retry config for throttling:

  ```python
  from botocore.config import Config
  cfg = Config(retries={"max_attempts": 10, "mode": "adaptive"})
  client = boto3.client("dynamodb", config=cfg, region_name="us-east-1")
  ```

- **Waiters** for eventual readiness:
  `client.get_waiter("instance_running").wait(InstanceIds=[id])`.
- **Idempotency:** use client request tokens / conditional writes so a retry
  doesn't double-apply.
- **Tagging:** tag created resources (`Project`, `Environment`, `Owner`).
- **Least privilege:** scope IAM to the specific actions and resource ARNs
  needed; never `"Action": "*"` / `"Resource": "*"` outside a justified case.

## Phase 5 — Verify safely

- For **destructive** actions (delete bucket/object, terminate instance, drop
  table), confirm intent explicitly and prefer a dry run or list-first step.
  Many APIs support `DryRun=True` (EC2) — use it.
- Run the operation and **report the actual API response**, not an assumed
  outcome. Capture identifiers/ARNs returned.
- For created infrastructure, confirm it reached the expected state with a
  describe/waiter call.

## Phase 6 — Report and clean up

- Summarize: what was created/changed, the region, resource identifiers/ARNs,
  and the IAM permissions required.
- State the **cost implication** of any persistent resource (e.g. "this NAT
  gateway costs ~$0.045/hr plus data").
- For demos/tests, **tear down** created resources and confirm removal.

---

## Debugging guide

| Error / symptom | Likely cause | What to check |
|---|---|---|
| `AccessDenied` / `UnauthorizedOperation` | IAM policy lacks the action/resource, or an explicit Deny | Decode the message; check the principal's effective policy and resource ARN. |
| `NoCredentialsError` | Provider chain found nothing | Env vars? `AWS_PROFILE`? Is an instance/task role attached? |
| `ThrottlingException` / `Rate exceeded` | Too many requests | Use adaptive retries, backoff, batch, or request a quota increase. |
| `EndpointConnectionError` | Wrong/unset region or network | Set `region_name`; check VPC endpoints/egress. |
| `ResourceNotFound` / `NoSuchBucket` | Wrong name/region, or not yet created | Confirm the resource exists in **that** region. |
| `ExpiredToken` | STS session/SSO expired | Re-authenticate (`aws sso login`) or refresh the role session. |
| Empty list results | Forgot pagination | Use a paginator. |

## Security guardrails (non-negotiable)

- **Never hard-code** access keys or secrets in source. Use the credential
  provider chain, IAM roles, SSO, Secrets Manager, or SSM Parameter Store.
- **Least privilege by default.** Flag any policy using wildcard actions or
  resources and justify or narrow it.
- **Encrypt** data at rest (S3 SSE/KMS, EBS, RDS) and in transit (TLS).
- **Set the region explicitly**; don't rely on ambient defaults.
- **Destructive ops are irreversible** — confirm, dry-run, or snapshot first.
- Don't log secrets, tokens, or full credentials.
