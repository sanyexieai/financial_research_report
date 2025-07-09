-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建文档表
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    url TEXT,
    search_term VARCHAR(255),
    source VARCHAR(100) DEFAULT 'search_result',
    chunk_id INTEGER DEFAULT 0,
    embedding vector(1024),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_documents_search_term 
ON documents(search_term);

CREATE INDEX IF NOT EXISTS idx_documents_embedding 
ON documents USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_documents_created_at 
ON documents(created_at);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 创建统计视图
CREATE OR REPLACE VIEW documents_stats AS
SELECT 
    COUNT(*) as total_chunks,
    COUNT(DISTINCT split_part(doc_id, '_chunk_', 1)) as total_documents,
    COUNT(DISTINCT search_term) as unique_search_terms,
    MAX(created_at) as last_updated
FROM documents;

-- 创建搜索关键词统计视图
CREATE OR REPLACE VIEW search_terms_stats AS
SELECT 
    search_term,
    COUNT(*) as document_count,
    MAX(created_at) as last_used
FROM documents 
WHERE search_term IS NOT NULL 
GROUP BY search_term 
ORDER BY COUNT(*) DESC; 