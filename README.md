# AuditFlow
> Real-time Detection of Privileged Access Anomalies in Streaming Audit Logs

### ✨ Tagline

_**“Stream. Detect. Protect.”**_

AuditFlow continuously ingests system and cloud audit logs, identifies unauthorized privileged access, and assigns confidence scores using AI-driven anomaly detection — all in real time.

## 📊 Overview

AuditFlow is an open-source data engineering project that integrates **streaming pipelines, cloud audit logs and AI-based scoring** to detect abnormal priviledged access activities.

The system simulates or consumes live audit events (e.g., AWS CloudTrail, Linux auth logs), transforms them into structured datasets, and applies **rule-based + ML** scoring to flag anomalies such as:
	•	Unauthorized logins or sudo usage
	•	Unexpected admin policy updates
	•	Key or role creations outside normal hours
	•	Access from unfamiliar IPs or regions

`AuditFlow` combines Kafka, Spark, and a modern data warehouse for end-to-end observability.
