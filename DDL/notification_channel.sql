-- public.notification_channel definition

-- Drop table

-- DROP TABLE public.notification_channel;

CREATE TABLE public.notification_channel (
	guild_id int8 NOT NULL,
	channel_id int8 NOT NULL,
	CONSTRAINT notification_channel_pk PRIMARY KEY (guild_id)
);