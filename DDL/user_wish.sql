-- public.user_wish definition

-- Drop table

-- DROP TABLE public.user_wish;

CREATE TABLE public.user_wish (
	id int8 NULL,
	"name" varchar(100) NULL,
	loof int4 NULL DEFAULT 0,
	banner int4 NULL DEFAULT 0,
	wishnum int4 NULL DEFAULT 10
);