-- Create database if it doesn't exist
SELECT 'CREATE DATABASE docs_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'docs_db')\gexec

-- Connect to the database
\c docs_db

-- Enable logical replication for Debezium
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- SCHEMAS
CREATE SCHEMA IF NOT EXISTS documents;
CREATE SCHEMA IF NOT EXISTS signatures;

-- DOCUMENTS TABLE

CREATE TABLE IF NOT EXISTS documents.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) DEFAULT 'text/plain',
    content_size BIGINT DEFAULT 0,
    s3_key VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    
    CONSTRAINT chk_status CHECK (status IN ('created', 'sent', 'viewed', 'signed', 'completed', 'cancelled'))
);

-- SIGNATURES TABLE
CREATE TABLE IF NOT EXISTS signatures.signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    signer_email VARCHAR(255) NOT NULL,
    signer_name VARCHAR(255) NOT NULL,
    signed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    signature_data TEXT,
    ip_address VARCHAR(45),
    
    CONSTRAINT fk_document 
        FOREIGN KEY (document_id) 
        REFERENCES documents.documents(id) 
        ON DELETE CASCADE
);


-- INDEXES

-- Documents: Composite index for status + created_at queries
CREATE INDEX IF NOT EXISTS idx_documents_status_created_at 
    ON documents.documents(status, created_at DESC);

-- Documents: Composite index for user's documents
CREATE INDEX IF NOT EXISTS idx_documents_created_by_created_at 
    ON documents.documents(created_by, created_at DESC);

-- Signatures: Foreign key index (required for JOIN performance)
CREATE INDEX IF NOT EXISTS idx_signatures_document_id 
    ON signatures.signatures(document_id);

-- Signatures: Composite index for user's signatures
CREATE INDEX IF NOT EXISTS idx_signatures_email_signed_at 
    ON signatures.signatures(signer_email, signed_at DESC);

-- Set REPLICA IDENTITY FULL for complete CDC change data
ALTER TABLE documents.documents REPLICA IDENTITY FULL;
ALTER TABLE signatures.signatures REPLICA IDENTITY FULL;

