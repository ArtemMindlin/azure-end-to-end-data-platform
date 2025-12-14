# Azure Resources

This directory contains all Azure-related assets used to deploy and operate the cloud data platform.
It documents the architecture, configuration, and infrastructure of the Azure environment, following
enterprise cloud and data engineering best practices.

## Scope

The Azure environment implements an end-to-end data platform composed of:
- Secure cloud storage for raw, curated, and analytics-ready data
- Managed data ingestion and orchestration services
- Cloud-based data processing
- Analytics and visualization layers
- Infrastructure-as-Code definitions for reproducibility

This separation ensures that cloud concerns (resources, services, security, and networking) are clearly
decoupled from local scripts and utilities.

## Directory Structure

```bash
└── azure
    ├── storage/ # Azure Blob Storage configuration and documentation
    ├── data_ingestion/ # Azure Data Factory pipelines and databases
    ├── processing/ # Cloud-based data processing (Databricks/Functions)
    ├── dashboards/ # Power BI assets and cloud-facing analytics
    └── infra/ # Infrastructure as Code (Bicep/Terraform)
```

## Storage Layer

Azure Blob Storage is used as the foundational layer of the platform.
It is configured with a hierarchical namespace enabled (Data Lake Gen2 semantics) and organized into
logical containers that reflect the data lifecycle:

- `raw/`: Immutable source data ingested from external systems
- `curated/`: Cleaned and validated datasets produced by processing jobs
- `analytics/`: Business-ready datasets optimized for reporting and BI

This design follows the medallion (Bronze / Silver / Gold) architecture pattern.

## Security and Networking

The Azure resources are configured with:
- Encryption at rest using Microsoft-managed keys
- Secure transfer enforced (TLS 1.2)
- Private containers with no anonymous access
- Public network access enabled for development, with a clear path to private endpoints in production

Authentication is handled using Azure-managed identities or access keys, depending on the service.

## Environment

This Azure environment represents a **development** setup (`dev`) intended for learning, experimentation,
and portfolio demonstration. Production-grade hardening (private endpoints, customer-managed keys,
advanced monitoring) is considered out of scope but identified as future improvements.

## Notes

All Azure resources are created with cost-awareness in mind and use managed services wherever possible
to minimize operational overhead and align with real-world enterprise data platforms.
