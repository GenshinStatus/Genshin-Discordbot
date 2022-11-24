-- public.user_wish definition

-- Drop table

-- DROP TABLE public.user_wish;

CREATE TABLE public.user_wish (
	id int8 NOT NULL,
	char_roof int4 NULL DEFAULT 0,
	weap_roof int4 NULL DEFAULT 0,
	custom_id int4 NULL DEFAULT 10,
	CONSTRAINT user_wish_pk PRIMARY KEY (id)
);