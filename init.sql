-- Initialize the news_finder database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'rss', 'api', 'scraper'
    content TEXT,
    summary TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_digests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    digest_date DATE UNIQUE NOT NULL,
    summary TEXT NOT NULL,
    article_count INTEGER NOT NULL DEFAULT 0,
    slack_message_ts VARCHAR(50), -- Slack message timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS digest_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    digest_id UUID NOT NULL REFERENCES daily_digests(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(digest_id, article_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source);
CREATE INDEX IF NOT EXISTS idx_news_articles_source_type ON news_articles(source_type);
CREATE INDEX IF NOT EXISTS idx_daily_digests_date ON daily_digests(digest_date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_news_articles_updated_at 
    BEFORE UPDATE ON news_articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_digests_updated_at 
    BEFORE UPDATE ON daily_digests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data
INSERT INTO news_articles (title, url, source, source_type, content, summary, published_at) VALUES
(
    'Sample AI News Article',
    'https://example.com/sample-ai-news',
    'Example News',
    'api',
    'This is a sample AI news article content for testing purposes.',
    'Sample AI news summary for testing.',
    NOW() - INTERVAL '1 day'
) ON CONFLICT (url) DO NOTHING;
