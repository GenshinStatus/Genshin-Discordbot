-- public.genshin_quiz definition

-- Drop table

-- DROP TABLE public.genshin_quiz;

CREATE TABLE public.genshin_quiz (
	quiz_id bigserial NOT NULL,
	user_id int8 NOT NULL,
	quiz_data text NOT NULL,
	answer text NOT NULL,
	"options" _text NOT NULL,
	image_url text NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	global_auth_flg bool NOT NULL DEFAULT false,
	global_auth_user_id int8 NULL,
	CONSTRAINT genshin_quiz_pk PRIMARY KEY (quiz_id)
);