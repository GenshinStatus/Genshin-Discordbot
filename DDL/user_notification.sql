-- public.user_notification definition

-- Drop table

-- DROP TABLE public.user_notification;

CREATE TABLE public.user_notification (
	serverid int8 NULL,
	id int8 NOT NULL,
	"name" bpchar(1) NULL,
	resin int8 NULL DEFAULT 0,
	channelid int8 NULL,
	CONSTRAINT user_notification_pkey PRIMARY KEY (id)
);