-- public.user_table definition

-- Drop table

-- DROP TABLE public.user_table;

CREATE TABLE public.user_table (
	serverid int8 NULL,
	id int8 NOT NULL,
	"name" varchar(100) NULL,
	uid int4 NOT NULL DEFAULT 0,
	username varchar(100) NOT NULL,
	public bool NULL DEFAULT false
);