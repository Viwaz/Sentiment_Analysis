-- Migration 002: Add scrape_sessions table and post_text column to comments
-- Run this once against the live database

-- Add post_text column to comments table (stores the Facebook post body text)
ALTER TABLE public.comments
    ADD COLUMN IF NOT EXISTS post_text TEXT;

-- Add session_id column to comments table (links a comment to its scraping session)
ALTER TABLE public.comments
    ADD COLUMN IF NOT EXISTS session_id INTEGER;

-- Create scrape_sessions table
CREATE TABLE IF NOT EXISTS public.scrape_sessions (
    session_id    SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL,
    session_name  VARCHAR(255) NOT NULL,
    source_url    VARCHAR(500) NOT NULL,
    comment_count INTEGER NOT NULL DEFAULT 0,
    model_used    VARCHAR(100),
    pos_count     INTEGER DEFAULT 0,
    neg_count     INTEGER DEFAULT 0,
    neu_count     INTEGER DEFAULT 0,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) ON DELETE CASCADE
);

-- Add FK from comments.session_id to scrape_sessions
ALTER TABLE public.comments
    ADD CONSTRAINT fk_comment_session
    FOREIGN KEY (session_id)
    REFERENCES public.scrape_sessions (session_id)
    ON DELETE SET NULL;

-- Index for fast session-based lookups
CREATE INDEX IF NOT EXISTS idx_comments_session_id ON public.comments(session_id);
CREATE INDEX IF NOT EXISTS idx_scrape_sessions_user_id ON public.scrape_sessions(user_id);
