# Azure End-to-End Data Platform

End-to-end data platform built on Microsoft Azure, covering ingestion, storage, processing, and analytics.  
This project demonstrates how to design and implement a scalable, cloud-native data architecture using managed Azure services and real-world scraped data.

The solution follows industry best practices commonly used in enterprise analytics environments.

---

## Architecture Overview

The platform follows a layered data lake architecture:

- **Ingestion**  
  Automated ingestion of external data sources using Azure Data Factory.

- **Storage**  
  Centralized data lake built on Azure Blob Storage, organized into logical layers:
  - **Raw (Bronze):** Data stored exactly as ingested
  - **Curated (Silver):** Cleaned and enriched datasets ready for analysis

- **Processing**  
  Cloud-based orchestration and transformations using Azure Data Factory pipelines.

- **Analytics & Visualization (Planned)**  
  Curated datasets designed to be consumed by analytical tools such as Power BI or Azure Synapse.

- **Infrastructure (Planned)**  
  Infrastructure designed to be reproducible and extensible using Infrastructure as Code.

---

## Azure Services Used

- **Azure Blob Storage**
  - Acts as the data lake
  - Logical separation between raw and curated data layers

- **Azure Data Factory**
  - Orchestrates data ingestion and movement
  - Uses linked services and schema-driven datasets
  - Implements metadata enrichment (e.g. ingestion timestamps)

---

## Implemented Pipelines

### `copy_products_raw_to_curated`

- Copies product data from the raw layer to the curated layer
- Adds ingestion metadata
- Preserves source data integrity
- Serves as a foundation for further data transformations

---

## Design Principles

- **Separation of concerns:** Raw data is preserved without modification
- **Scalability:** Cloud-native, managed Azure services
- **Reproducibility:** Clear structure and naming conventions
- **Enterprise realism:** Architecture mirrors real-world retail and consulting data platforms

---

## Future Improvements

- Data cleansing and normalization using Azure Data Factory Data Flows
- Incremental and partitioned ingestion
- Data quality checks and validations
- Analytics layer using Power BI or Azure Synapse
- Infrastructure as Code using Bicep or Terraform

---

## Disclaimer

This project is for educational and portfolio purposes only.  
The data used is publicly available and does not contain real production or confidential business information.
