# Click-Streaming-Data-Pipeline
# Click Streaming Data Pipeline
## Real-time Event Processing Platform

A comprehensive streaming data pipeline that demonstrates real-time event ingestion, validation, enrichment, and storage using modern data engineering tools. The platform handles clickstream events from web applications and processes them through a robust, scalable architecture.

##  Overview

This project implements an end-to-end streaming data pipeline that:

1. **Event Ingestion**: Receives clickstream events via REST API
2. **Schema Validation**: Validates events against Avro schemas
3. **Stream Processing**: Enriches data using Apache Spark Streaming
4. **Data Storage**: Stores processed data in MinIO (S3-compatible storage)
5. **Real-time Analytics**: Enables real-time querying with KSQL
6. **Monitoring**: Provides comprehensive observability through Kafka UI                                                                                                                                              
##  Architecture

### Core Components

- **Apache Kafka**: Event streaming platform and message broker
- **MinIO**: S3-compatible object storage for data lake
- **Apache Spark**: Distributed processing engine for stream analytics
- **Schema Registry**: Centralized schema management and validation
- **Kafka Connect**: Data integration framework
- **KSQL**: Stream processing with SQL semantics
- **Kafka UI**: Web-based monitoring and management interface

### Data Flow Architecture

```
[Web App] → [REST API] → [Kafka] → [Spark Streaming] → [MinIO]
    ↓           ↓           ↓            ↓              ↓
[Events]    [Validation] [Topics]   [Enrichment]   [Storage]
```

```mermaid
flowchart LR

A[Event Generator] --> B[REST API Server]

B --> C[Kafka Raw Topic\n(acme.clickstream.raw.events)]

C --> D[Spark Streaming Job]

D --> E[Data Enrichment & Transformation]

E --> F[MinIO Storage\n(S3 Data Lake)]

