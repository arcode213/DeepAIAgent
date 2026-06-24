# Examples: Report Writing Skill

Filled-in templates showing the expected structure, specificity, and tone. Save
reports to `reports/<short-kebab-case-topic>.md`.

---

## Example 1 — Full research / decision report

```markdown
# Report: Best Python Web Framework for a Small Internal API

_Date: 2026-06-23_

## Summary
For a small internal JSON API built by a two-person team on Python 3.13,
**FastAPI** is the recommendation. It provides automatic request/response
validation and OpenAPI docs out of the box, first-class async support, and the
least boilerplate of the candidates, while deploying cleanly to AWS Lambda or a
container.

## Context
**Question:** "Which Python web framework should we use for a small internal
REST API?"
**Scope / assumptions:** Team of 2; Python 3.13; JSON REST API only (no
server-rendered HTML); moderate traffic; deploying to AWS Lambda or a container;
no existing framework lock-in.

## Approach
1. Identified the candidate frameworks: FastAPI, Flask, Django REST Framework.
2. Compared them across the criteria that matter for this use case: validation,
   async, auto docs, boilerplate, and AWS deployment fit.
3. Weighed each against the stated constraints.

## Findings

| Criterion        | FastAPI             | Flask          | Django REST   |
|------------------|---------------------|----------------|---------------|
| Validation       | Built-in (Pydantic) | Manual / ext   | Serializers   |
| Async support    | First-class         | Limited        | Partial       |
| Auto API docs    | Yes (OpenAPI/Swagger)| No (extension)| Browsable API |
| Boilerplate      | Low                 | Low            | High          |
| AWS Lambda fit   | Good (via Mangum)   | Good           | Heavier       |
| Learning curve   | Gentle              | Gentle         | Steeper       |

- FastAPI's Pydantic models give typed request/response validation and generated
  OpenAPI docs for free — meaningful for a small team that can't hand-maintain
  schemas.
- Flask is minimal and flexible but pushes validation, serialization, and docs
  onto the team as add-ons.
- Django REST is powerful (ORM, admin, auth) but heavyweight for a JSON-only
  internal API and slower to deploy serverless.

## Risks / Limitations
- Comparison reflects framework capabilities as of 2026-06; verify current
  versions before committing.
- If the API later needs a rich admin UI or a relational ORM, Django's batteries
  may outweigh FastAPI's simplicity — revisit then.

## Conclusion / Recommendation
Adopt **FastAPI**. It best matches a small team building a JSON API with minimal
boilerplate and clean AWS deployment. Reconsider only if requirements grow into
Django's strengths (admin, ORM-heavy app).

## Sources / Artifacts
- Comparison notes: `notes/framework-comparison.md`
- Prototype scaffold: `prototypes/fastapi-demo/`
```

---

## Example 2 — Minimal short-answer report

```markdown
# Report: Default S3 Object Encryption

_Date: 2026-06-23_

## Summary
As of January 2023, Amazon S3 encrypts all new objects at rest by default using
SSE-S3 (AES-256). No configuration is required to enable basic encryption.

## Conclusion
New uploads are encrypted automatically. Use SSE-KMS only when you need
customer-managed keys, key rotation policies, or per-object access audit trails.

## Sources / Artifacts
- AWS S3 documentation — "Default encryption for S3 buckets."
```

---

## Example 3 — Technical investigation / debugging report

```markdown
# Report: Intermittent 500s on the /orders Endpoint

_Date: 2026-06-23_

## Summary
The intermittent 500s are caused by DynamoDB **throttling** under burst load:
the table's provisioned write capacity is exceeded during peak hours, and the
service does not retry, so the request fails. Switching the client to adaptive
retries and the table to on-demand capacity resolves it.

## Context
**Question:** "Why does POST /orders fail ~2% of the time during peak hours?"
**Scope:** Production `orders-api` service; failures cluster 12:00–13:00 UTC.

## Findings
- **Symptom:** ~2% of POST /orders return HTTP 500 between 12:00–13:00 UTC;
  near-zero failures off-peak.
- **Root cause:** CloudWatch shows `WriteThrottleEvents` on the `orders` table
  spiking to ~40/min during the same window. The boto3 client uses the default
  retry config (`mode="legacy"`, 3 attempts) which does not adapt to throttling.
- **Evidence:**
  - CloudWatch metric `WriteThrottleEvents` (orders table), 2026-06-22 12:00–13:00.
  - App logs: `ProvisionedThroughputExceededException` on failed requests.
  - Failure timestamps correlate 1:1 with throttle spikes.

## Conclusion / Recommendation
1. Set the DynamoDB client to `retries={"mode": "adaptive", "max_attempts": 10}`.
2. Switch the `orders` table to **on-demand** capacity (or raise provisioned WCU
   and add auto-scaling) to absorb peaks.
3. Add a CloudWatch alarm on `WriteThrottleEvents > 0`.

## Sources / Artifacts
- Dashboard: `cloudwatch/orders-api`
- Failing log sample: `notes/orders-500-logs.txt`
- Proposed fix diff: `patches/ddb-retry-config.diff`
```

---

## What these examples demonstrate

- The **Summary answers the question on its own**, placed first (BLUF).
- Findings are **specific** (numbers, dates, metric names, file paths) and use a
  **table** where comparison helps.
- **Assumptions and limitations** are stated explicitly.
- The **Conclusion follows from the Findings** and gives concrete next steps.
- Each report includes a **date** and **pointers to where artifacts live**.
- **Length is matched** to the question's complexity (full vs. minimal).
