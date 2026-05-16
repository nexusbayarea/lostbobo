-- Initialize pgvector extension and document table for SimHPC RAG service.
-- Run this against your Supabase database once.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768),
    tenant_id TEXT NOT NULL DEFAULT 'default',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_documents_tenant
    ON rag_documents (tenant_id);

CREATE INDEX IF NOT EXISTS idx_rag_documents_embedding
    ON rag_documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Match documents function for pgvector similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(768),
    match_count INT DEFAULT 5,
    filter_tenant TEXT DEFAULT NULL
)
RETURNS TABLE(
    id BIGINT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rag_documents.id,
        rag_documents.content,
        1 - (rag_documents.embedding <=> query_embedding) AS similarity,
        rag_documents.metadata
    FROM rag_documents
    WHERE (filter_tenant IS NULL OR rag_documents.tenant_id = filter_tenant)
    ORDER BY rag_documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
