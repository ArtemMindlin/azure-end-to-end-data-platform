# Azure Resources

This directory contains all Azure-related assets used to deploy and operate the cloud data platform.
It documents the architecture, configuration, and design decisions of the Azure environment, following
enterprise cloud and data engineering best practices.

The goal of this directory is to clearly separate cloud infrastructure and platform components from
local scripts and utilities, mirroring real-world enterprise data platform repositories.

---

## Scope

The Azure environment implements a cloud-native data platform composed of:

- Secure object storage for raw and curated datasets
- Managed data ingestion and orchestration services
- Cloud-based data processing and transformation layers
- Analytics and visualization components
- Infrastructure design aligned with Infrastructure as Code principles

This separation ensures that cloud concerns (resources, services, security, and networking) are
decoupled from local development logic.

---

## Directory Structure

```bash
azure/
├── storage/           # Azure Blob Storage configuration and documentation
├── data_ingestion/    # Azure Data Factory pipelines and datasets
├── processing/        # Cloud-based processing (Databricks / Functions)
├── dashboards/        # Power BI assets and cloud-facing analytics
└── infra/             # Infrastructure as Code (Bicep / Terraform)
```

## Storage Layer

Azure Blob Storage acts as the foundational layer of the platform and is configured with a hierarchical
namespace enabled (Azure Data Lake Gen2 semantics).

Data is organized into logical containers reflecting the data lifecycle:

- **`raw/`**  
  Immutable source data stored exactly as ingested from external systems.  
  This layer preserves data fidelity and serves as the single source of truth.

- **`curated/`**  
  Cleaned and enriched datasets produced by orchestration and transformation jobs.  
  This layer is designed for downstream analytics and further processing.

- **`analytics/`**  
  Business-ready datasets optimized for reporting and analytical consumption.  
  This layer is intended to feed BI tools and analytical engines.

This design follows the medallion (Bronze / Silver / Gold) architecture pattern commonly used in
enterprise analytics platforms.

---

## Data Ingestion and Orchestration

Azure Data Factory (ADF) is used to orchestrate data ingestion and movement across the platform.

Implemented features include:
- Linked services connecting Azure Data Factory to Azure Blob Storage
- Schema-driven source and sink datasets
- Raw-to-curated ingestion pipelines
- Metadata enrichment (e.g. ingestion timestamps)

The ingestion pipelines are designed to preserve raw data integrity while enabling controlled
and reproducible data movement across layers.

---

## Security and Networking

Azure resources are configured with security-first defaults appropriate for a development environment:

- Encryption at rest using Microsoft-managed keys
- Secure data transfer enforced (TLS 1.2)
- Private containers with no anonymous access
- Public network access enabled for development, with a defined path to private endpoints in production

Authentication is handled using Azure-managed identities or access keys, depending on the service and
integration requirements.

---

## Environment

This Azure environment represents a **development (`dev`) setup** intended for learning,
experimentation, and portfolio demonstration.

Production-grade hardening (private endpoints, customer-managed keys, advanced monitoring,
and alerting) is intentionally out of scope but identified as future improvements.

---

## Notes

All Azure resources are created with cost-awareness in mind and rely on managed services wherever
possible to minimize operational overhead and align with real-world enterprise data platform design.
