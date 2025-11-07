-- Initialize PostgreSQL database with pgvector extension
-- This script runs automatically when the container is first created

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE loanserp TO loan;

-- Optional: Create any additional extensions you might need
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search
-- CREATE EXTENSION IF NOT EXISTS btree_gin;  -- For GIN indexes
-- CREATE EXTENSION IF NOT EXISTS btree_gist;  -- For GIST indexes
