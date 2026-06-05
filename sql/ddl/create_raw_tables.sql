CREATE TABLE IF NOT EXISTS public.artists
(
    id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    gender text COLLATE pg_catalog."default",
    country text COLLATE pg_catalog."default",
    score integer,
    CONSTRAINT artists_pkey PRIMARY KEY (id)
)