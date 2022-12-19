-- public.genshin_notification definition

-- Drop table

-- DROP TABLE public.genshin_notification;

CREATE TABLE public.genshin_notification (
	notification_id bigserial NOT NULL,
	type_id int4 NOT NULL,
	bot_id int8 NOT NULL,
	user_id int8 NOT NULL,
	guild_id int8 NOT NULL,
	notification_time information_schema."time_stamp" NOT NULL,
	plan_time information_schema."time_stamp" NOT NULL,
	CONSTRAINT regin_notification_pk PRIMARY KEY (notification_id)
);