# Enterprise RAG & Cloud Scalability Architecture (AWS)

## Executive Summary

This document outlines the production cloud architecture for scaling the **Journal Tracker RAG System** on Amazon Web Services (AWS). While the application runs locally in containerized development mode, the underlying RAG service (`rag_service.py`) is designed with a pluggable vector store and embedding engine interface that scales to millions of papers, patents, and user research notes in AWS.

---

## High-Level Architecture Diagram

```mermaid
flowchart TD
    User([User / Browser]) <--> ALB[AWS Application Load Balancer]
    
    subgraph Compute Layer [AWS ECS / EKS Container Cluster]
        FlaskAPI[Flask Web App Instances\nHPA Scaled]
        WorkerProcess[Async Indexing Worker\nSQS Consumer]
    end
    
    subgraph Data & Storage Layer
        RDS[(AWS RDS PostgreSQL\nwith pgvector extension)]
        Redis[(AWS ElastiCache Redis\nQuery & Embedding Cache)]
        S3[(AWS S3 Bucket\nPaper PDFs & Documents)]
    end
    
    subgraph AI & ML Layer [AWS Bedrock / Groq Cloud]
        BedrockEmbed[AWS Bedrock Titan Embeddings\namazon.titan-embed-text-v2]
        LLMInference[Groq Cloud / AWS Bedrock Llama-3.3-70b]
    end
    
    ALB --> FlaskAPI
    FlaskAPI <--> Redis
    FlaskAPI <--> RDS
    WorkerProcess <--> RDS
    WorkerProcess --> BedrockEmbed
    WorkerProcess <--> S3
    FlaskAPI --> SQS[AWS SQS Queue\nDocument Ingestion Queue]
    SQS --> WorkerProcess
    FlaskAPI --> LLMInference
```

---

## Key Cloud Architectural Pillars

### 1. Unified Relational & Vector Database (AWS RDS PostgreSQL + `pgvector`)
- **Why pgvector over standalone vector DBs**:
  - Eliminates data synchronization lag between SQL metadata (`ResearchPaper`, `Patent`, `Note`) and vector indices.
  - Allows hybrid SQL queries filtering vector similarity by `user_id`, `publication`, `year`, and `read_status` in a single query.
  - Supports **HNSW (Hierarchical Navigable Small World)** and **IVFFlat** vector indices for sub-millisecond similarity search across millions of vectors.
- **SQL Schema with `pgvector`**:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;

  CREATE TABLE document_embeddings (
      id BIGSERIAL PRIMARY KEY,
      chunk_id VARCHAR(255) UNIQUE NOT NULL,
      entity_type VARCHAR(50) NOT NULL, -- 'paper', 'patent', 'note'
      entity_id INT NOT NULL,
      user_id INT NULL,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      metadata JSONB NOT NULL,
      embedding vector(384), -- 384 dimensions for all-MiniLM-L6-v2 or 1536 for Titan
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );

  -- Create HNSW Index for fast cosine distance search
  CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);
  CREATE INDEX idx_user_entity ON document_embeddings(user_id, entity_type);
  ```

---

### 2. High-Throughput Asynchronous Document Ingestion (AWS SQS + Lambda / ECS Worker)
- **Problem**: Ingesting large papers or batch PDFs synchronously during HTTP request blocks user UI and leads to gateway timeouts.
- **Solution**:
  1. Flask API enqueues document payload to **AWS SQS (`journal-tracker-ingestion-queue`)**.
  2. Background worker (AWS ECS Task or AWS Lambda) dequeues message, performs sliding-window chunking, generates embeddings via AWS Bedrock Titan API, and inserts records into RDS `document_embeddings`.
  3. UI updates real-time status via WebSocket or polling.

---

### 3. Dual Caching Strategy (AWS ElastiCache Redis)
- **Vector Embedding Caching**: Caches query vector embeddings to prevent redundant LLM embedding API calls.
- **RAG Response Caching**: Hashes (query + user_id + top_k) to serve frequent research queries instantly with 0ms LLM latency.

---

### 4. Enterprise Multi-Tenancy & Privacy Isolation
- Security filtering enforced directly at the vector query level:
  ```sql
  SELECT chunk_id, title, content, metadata, 1 - (embedding <=> :query_vector) AS cosine_sim
  FROM document_embeddings
  WHERE (user_id IS NULL OR user_id = :current_user_id OR entity_type IN ('paper', 'patent'))
  ORDER BY embedding <=> :query_vector
  LIMIT 4;
  ```

---

## Terraform Infrastructure as Code (IaC) Snippets

### Provisioning AWS RDS PostgreSQL with pgvector Support

```hcl
# AWS RDS PostgreSQL Instance for pgvector RAG Storage
resource "aws_db_instance" "journal_tracker_db" {
  allocated_storage       = 50
  max_allocated_storage   = 500
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = "db.r6g.large"
  db_name                 = "journaltracker"
  username                = "postgres"
  password                = var.db_password
  parameter_group_name    = aws_db_parameter_group.pgvector_params.name
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.db_sg.id]

  tags = {
    Environment = "production"
    Application = "JournalTracker-RAG"
  }
}

resource "aws_db_parameter_group" "pgvector_params" {
  name   = "journal-tracker-pg15-params"
  family = "postgres15"

  parameter {
    name  = "shared_preload_libraries"
    value = "pgvector"
  }
}

# AWS SQS Queue for Asynchronous Document Vectorization
resource "aws_sqs_queue" "rag_ingestion_queue" {
  name                      = "journal-tracker-ingestion-queue.fifo"
  fifo_queue                = true
  content_based_deduplication = true
  visibility_timeout_seconds = 300
}
```

---

## Environment Configuration Matrix

To deploy the application in AWS, set the following environment variables:

| Variable | Local / Demo Mode | Production Cloud Mode (AWS) |
|---|---|---|
| `VECTOR_STORE_TYPE` | `local` (disk pickle) | `pgvector` (RDS PostgreSQL) |
| `DATABASE_URL` | `sqlite:///instance/research_assistant.db` | `postgresql://user:pass@rds-endpoint:5432/journaltracker` |
| `AWS_BEDROCK_ENABLED` | `false` | `true` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | `amazon.titan-embed-text-v1` |
| `AWS_REGION` | `us-east-1` | `us-east-1` |
