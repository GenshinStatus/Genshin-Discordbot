-- public.user_table definition

-- Drop table

-- DROP TABLE public.user_table;

CREATE TABLE public.user_table (
	id int8 NOT NULL,
	uid int4 NOT NULL DEFAULT 0,
	username varchar(100) NOT NULL,
	CONSTRAINT user_table_pkey PRIMARY KEY (id, uid)
);