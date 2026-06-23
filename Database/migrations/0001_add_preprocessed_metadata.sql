-- Migration: add preprocessed_id and metadata JSONB to preprocessed_comments
-- Safe upgrade that preserves existing cleaned_text and preprocessed_at values.

BEGIN;

-- If the table doesn't exist, simply create it (fresh install path)
CREATE TABLE IF NOT EXISTS public.preprocessed_comments_new (
    preprocessed_id  SERIAL PRIMARY KEY,
    comment_id       VARCHAR(100) NOT NULL UNIQUE,
    cleaned_text     TEXT NOT NULL,
    metadata         JSONB,
    preprocessed_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_preproc_comment_new FOREIGN KEY (comment_id)
        REFERENCES public.comments (comment_id) ON DELETE CASCADE
);

-- If an old table exists, migrate data across
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'preprocessed_comments') THEN
        -- rename the existing table for copy
        ALTER TABLE public.preprocessed_comments RENAME TO preprocessed_comments_old;

        -- create the new table (if not already created above)
        CREATE TABLE IF NOT EXISTS public.preprocessed_comments (
            preprocessed_id  SERIAL PRIMARY KEY,
            comment_id       VARCHAR(100) NOT NULL UNIQUE,
            cleaned_text     TEXT NOT NULL,
            metadata         JSONB,
            preprocessed_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_preproc_comment FOREIGN KEY (comment_id)
                REFERENCES public.comments (comment_id) ON DELETE CASCADE
        );

        -- copy existing data (preserve cleaned_text and timestamp)
        INSERT INTO public.preprocessed_comments (comment_id, cleaned_text, preprocessed_at)
        SELECT comment_id, cleaned_text, preprocessed_at FROM public.preprocessed_comments_old;

        -- drop old table
        DROP TABLE public.preprocessed_comments_old;
    END IF;
END$$;

COMMIT;

-- Rollback guidance:
-- To rollback, restore from a dump taken before running this migration.
-- Example:
-- pg_restore -h <host> -U <user> -d <db> --clean <backup_file>
