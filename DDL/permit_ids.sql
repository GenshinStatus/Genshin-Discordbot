-- public.permit_ids definition

-- Drop table

-- DROP TABLE public.permit_ids;

CREATE TABLE public.permit_ids (
	serverid int8 NOT NULL,
	userid int8 NOT NULL,
	CONSTRAINT permit_ids_pkey PRIMARY KEY (serverid, userid)
);