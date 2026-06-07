CREATE TABLE IF NOT EXISTS public.artists
(
    artist_id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    gender text COLLATE pg_catalog."default",
    country text COLLATE pg_catalog."default",
    score integer,
    CONSTRAINT artists_pkey PRIMARY KEY (artist_id)
)