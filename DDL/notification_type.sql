-- public.notification_type definition

-- Drop table

-- DROP TABLE public.notification_type;

CREATE TABLE public.notification_type (
	type_id int4 NOT NULL,
	type_name varchar NOT NULL,
	CONSTRAINT notification_type_pk PRIMARY KEY (type_id)
);

-- 一応初期で利用するであろうデータ
INSERT INTO public.notification_type(type_id, type_name) VALUES(1, '天然樹脂');