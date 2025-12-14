# Data Ingestion Layer – Azure Data Factory

This directory documents the **data ingestion and processing layer** of the Azure End-to-End Data Platform.  
It focuses on how raw product data is ingested, cleaned, validated, and loaded into an analytical SQL model using **Azure Data Factory**, **Azure Blob Storage**, and **Azure SQL Database**.

This layer follows an **enterprise-grade ELT approach**, separating raw data preservation from curated and analytical datasets.

---

## Scope

This ingestion layer covers the full flow:

1. Raw data ingestion into Azure Blob Storage  
2. Validation and conditional execution using Azure Data Factory  
3. Data cleansing and normalization using Mapping Data Flows  
4. Loading into a SQL **staging layer**
5. Promotion into **current** and **historical** analytical tables via stored procedures

---

## Data Source

- **Origin:** Public dataset obtained from Kaggle  
- **Original creation:** Web scraping (external source)
- **Format:** CSV
- **Approximate volume:** ~4,600 rows per execution
- **Update frequency (assumed):** Every ~4 months

The dataset represents product-level information including prices, categories, images, and nutritional data.

---

## Storage Architecture (Azure Blob Storage)

**Storage account:** `stazdataamdev`

The data lake is organized using a **layered container structure**:





### Design decisions

- **Raw layer**
  - Stores data exactly as ingested
  - No transformations applied
  - Acts as the immutable source of truth

- **Curated layer**
  - Contains cleaned and standardized data
  - Includes a single consolidated CSV (`products_macro.csv`) for human consumption
  - Spark `part-*` files are considered technical artifacts

---

## Azure Data Factory Setup

**Data Factory:** `adf-azure-data-platform-dev`

### Linked Services

- **Blob Storage linked service**
  - Connects ADF to the data lake containers
- **Azure SQL Database linked service**
  - Connects ADF to the analytical database
  - Uses SQL authentication
  - Firewall configured to allow Azure services

---

## Datasets

| Dataset name | Description |
|-------------|-------------|
| `ds_products_raw` | Points to `raw/products_macro.csv` |
| `ds_products_curated` | Points to `curated/products_macro.csv` |
| `ds_sql_stg_products_clean` | Points to SQL table `stg.products_clean` |

---

## Pipelines Overview

### 1. `pl_raw_to_curated_products`

**Purpose:**  
Copies raw data from the raw layer to the curated layer and enriches it with ingestion metadata.

**Key characteristics:**
- No transformations applied
- Preserves original schema
- Adds ingestion timestamp

---

### 2. `pl_clean_products_prices`

**Purpose:**  
Cleans and normalizes product data using an Azure Data Factory Mapping Data Flow.

---

### 3. `pl_end_to_end_products`

This is the **main orchestration pipeline**.

#### Pipeline Logic








#### Purpose

- Ensures raw data exists before processing
- Prevents partial or invalid executions
- Guarantees idempotent and controlled data loading

---

## Data Flow: `dfCleanProducts`

### Transformations applied

- Column renaming (e.g. `Category` → `category`)
- String trimming and null normalization
- Price cleaning:
  - Removal of currency symbols (`€`)
  - Decimal normalization (`,` → `.`)
- Schema standardization
- Data quality assertions:
  - `id` must not be null

### Output

- Cleaned data written back to the curated layer
- Consistent schema for downstream SQL loading

---

## SQL Layer Design

### Staging Table

**Schema:** `stg.products_clean`

- All columns stored as `NVARCHAR`
- Acts as a transient landing zone
- No business logic or constraints enforced

---

### Current Table

**Schema:** `dbo.products`

- One row per product (`id` is primary key)
- Contains the most recent snapshot
- Strong typing (DECIMAL, DATETIME2, etc.)

---

### Historical Table

**Purpose:**
- Stores historical snapshots of product prices
- Allows multiple rows per product across time
- Enables price evolution analysis

**Key design choice:**
- Snapshot date drives historical versioning
- Same-day re-executions overwrite instead of duplicating data

---

## Stored Procedure

### `sp_load_products_snapshot`

**Responsibilities:**

- Merge data from `stg.products_clean` into:
  - `dbo.products` (current state)
  - Historical table (price history)
- Apply final type casting
- Enforce snapshot logic
- Prevent duplicate loads on the same day

This approach centralizes business logic inside SQL and keeps ADF pipelines orchestration-focused.

---

## Execution & Validation

### How to run

- Manual execution using **Trigger now**
- Debug mode during development
- Designed to be schedulable in the future

### Validation checklist

After a successful run:

1. Raw file exists in Blob Storage
2. Curated `products_macro.csv` updated
3. `stg.products_clean` populated
4. `dbo.products` contains current data
5. Historical table updated (if applicable)

---

## Design Principles

- **Layered architecture (Bronze → Silver → SQL)**
- **Schema-on-read in raw**
- **Schema enforcement downstream**
- **Idempotent executions**
- **Clear separation of orchestration and business logic**

---

## Future Improvements

- Incremental ingestion
- Partitioned historical tables
- Power BI semantic model
- Monitoring and alerting
- Infrastructure as Code (Bicep / Terraform)
- CI/CD for ADF pipelines

---

## Disclaimer

This project is for educational and portfolio purposes only.  
The data used is publicly available and does not represent real production systems or confidential business information.
