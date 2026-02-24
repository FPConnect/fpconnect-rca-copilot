-- FPConnect PostgreSQL initialization
-- Enables pgvector extension for semantic search

CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fpconnect TO fpconnect;
