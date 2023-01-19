-- public.guilds_own_quiz definition

-- Drop table

-- DROP TABLE public.guilds_own_quiz;

CREATE TABLE public.guilds_own_quiz (
	quiz_id int8 NOT NULL,
	guild_id int8 NOT NULL,
	auth_flg bool NOT NULL DEFAULT false,
	auth_user_id int8 NULL,
	CONSTRAINT guilds_own_quiz_pk PRIMARY KEY (quiz_id, guild_id)
);


-- public.guilds_own_quiz foreign keys

ALTER TABLE public.guilds_own_quiz ADD CONSTRAINT guilds_own_quiz_fk FOREIGN KEY (quiz_id) REFERENCES public.genshin_quiz(quiz_id);