from datetime import datetime
from typing import Tuple
import os
import psycopg2
import discord


# 予め定数として接続先を定義しておきます
print(os.getenv('SQL'))


class database:
    __DSN = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user=os.getenv('POSTGRES_USER'),  # ユーザ
        password=os.getenv('POSTGRES_PASSWORD'),  # パスワード
        host=os.getenv('HOST'),  # ホスト名
        port=os.getenv('PORT'),  # ポート
        dbname=os.getenv('POSTGRES_DB'))  # データベース名

    def __connection():
        return psycopg2.connect(database.__DSN)

    def load_sql(sql: str, data: Tuple[int, str, datetime] = (), default: any = dict()) -> any:
        """
        sqlを読み込んでそのままDictとかListにします。
        読み込めなかった場合にはdefaultの値を返します。
        → おそらく使う用途ない気がする
        """
        try:
            return database.load_data_sql(sql, data)
        except:
            return default

    def load_data_sql(sql: str, data: Tuple) -> Tuple[Tuple[int, str, datetime]]:
        """
        sqlを読み込んでTuple型で返却します。
        この時、返却値はtable構造に依存します。
        SQL構文などに問題がある場合は、それに基づくErrorをthrowします。
        """
        connector = database.__connection()

        cursor = connector.cursor()
        cursor.execute(sql, data)
        result = cursor.fetchall()
        cursor.close()
        connector.close()
        return result

    def table_update_sql(sql: str, data: Tuple[int, str, datetime] = ()) -> None:
        """
        sqlを実行しtableの更新を行うための関数です。
        SQL構文などに問題がある場合は、それに基づくErrorをthrowします。
        """
        try:
            connector = database.__connection()
            cursor = connector.cursor()
            cursor.execute(sql, data)
        finally:
            connector.commit()
            cursor.close()
            connector.close()


class Guild:
    def __init__(self, id: int):
        self.id = id

    def set_guilds(guild_id_list: list[discord.Guild]):
        """
        guildオブジェクトの配列を受け取り登録を行います。
        """
        if len(guild_id_list) > 0:
            database.table_update_sql(
                sql="insert into bot_table values " +
                    ",".join(["(%s)"] * len(guild_id_list)) +
                    " ON CONFLICT DO NOTHING",
                data=[v.id for v in guild_id_list],
            )

    def get_count():
        """
        guildの数を取得し返します。
        """
        result = database.load_data_sql(
            sql="select count(*) from bot_table", data=None)
        return result[0][0]


class User:
    def __init__(self, user_id: int, uid: int, game_name: str):
        self.user_id = user_id
        self.uid = uid
        self.game_name = game_name

    def get_user_list(user_id: int):
        """
        user_idからユーザーが登録したUIDの一覧を取得します
        """
        # print(user_id)
        data = database.load_data_sql(
            sql="""
            select id, uid, username from user_table where id = %s
            """,
            data=(user_id, )
        )
        # print(data)
        return [User(v[0], v[1], v[2]) for v in data]

    def insert_user(user):
        """
        利用者情報を新規で追加します。
        この時Userオブジェクトは全ての値が保持されている必要があります。
        """
        # 一意制約違反に引っかかる場合がある気がするのでtry exceptしてます
        try:
            database.table_update_sql(
                sql="""
                insert into user_table values(%s, %s, %s) 
                """,
                data=(user.user_id, user.uid, user.game_name)
            )
            return user.game_name
        except:
            User.update_user(user)

    def update_user(user):
        """
        利用者情報を更新する場合に利用します。
        この時Userオブジェクトは全ての値が保持されている必要があります。
        """
        database.table_update_sql(
            sql="""
            update user_table set username=%s where id = %s and uid = %s
            """,
            data=(user.game_name, user.user_id, user.uid, )
        )

    def delete_user(user_id: int, uid: int):
        """
        利用者情報を削除する場合に利用します。
        """
        database.table_update_sql(
            sql="""
            delete from user_table where id = %s and uid = %s
            """,
            data=(user_id, uid)
        )


class PermitID:
    def __init__(self, uid: int, d_id: str, g_name: str):
        self.uid = uid
        self.d_id = d_id
        self.g_name = g_name

    def get_uid_list(guild_id: int):
        """
        guild_idからUIDのlistを取得する関数です。
        genshin botでguildごとのuidlistを取得するために利用します。
        """
        result = database.load_data_sql(sql="""
            select a.id, a.uid, a.username
            from user_table a
            inner join permit_ids b
            on a.id = b.userid
            where b.serverid = %s""",
                                        data=(guild_id,))
        # print(result)
        data: list[PermitID] = [
            PermitID(uid=v[1], d_id=v[0], g_name=v[2])
            for v in result
        ]
        return data

    def is_user_public(guild_id: int, user_id: int):
        """
        ユーザーが登録したUIDが公開されているか取得する関数です。
        getEmbedで公開されているかどうかを取得するために利用します。
        """
        result = database.load_data_sql(
            sql="""
            select 0
            from permit_ids
            where serverid = %s and userid = %s
            """,
            data=(guild_id, user_id))

        if len(result) != 0:
            return True
        else:
            return False

    def add_permit_id(guild_id: int, user_id: int):
        """
        genshin botでuidlistを公開設定とした時にdatabaseにデータを追加する処理です。
        """
        # print(guild_id)
        database.table_update_sql(
            sql="""
            insert into permit_ids values(%s, %s)
            on conflict do nothing
            """,
            data=(guild_id, user_id,))

    def remove_permit_id(guild_id: int, user_id: int):
        """
        genshin botでuidlistを公開設定を解除した場合ときにuidを削除する処理です。
        """
        database.table_update_sql(
            sql="""
            delete from permit_ids where serverid = %s and userid = %s
            """,
            data=(guild_id, user_id,)
        )

class Ephemeral:
    def __init__(self, guild_id: int, ephemeral: bool):
        self.guild_id = guild_id
        self.ephemeral = ephemeral

    def is_ephemeral(guild_id: int):
        """
        そのサーバーでephemeralが有効かどうか取得する関数です。
        各コマンドのephemeral制御のために利用します。
        """
        result = database.load_data_sql(
            sql="""
            select is_ephemeral
            from public_server_config
            where serverid = %s
            """,
            data=(guild_id,))

        return result[0][0]

    def set_ephemeral(guild_id: int, ephemeral: bool):
        """
        Ephemeralを指定したboolにする処理です。
        """
        database.table_update_sql(
            sql="""
            update public_server_config 
            set is_ephemeral = %s
            where serverid = %s
            """,
            data=(ephemeral, guild_id))
        
    def init_ephemeral(guild_id: int):
        """
        guild_idのデータを初期化します。
        """
        database.table_update_sql(
            sql="""
            insert into public_server_config(serverid)
            values(%s)
            """,
            data=(guild_id,),
        )


class channel:
    def __init__(self, guilt_id: int, channel_id: int):
        self.guilt_id = guilt_id
        self.channel_id = channel_id

    def get_channel(guild_id):
        # sqlでデータとってくるやつ
        print(guild_id)
        result = database.load_data_sql(execute="""
        select *
        from server_table
        where serverid = %s""", data=(guild_id,))
        print(result)
        data: list[channel] = [
            channel(guilt_id=v[0], channel_id=v[1])
            for v in result
        ]
        return data


class WishUser:
    def __init__(self, id: int, char_loof: int, weapon_loof: int, wishnum: int):
        self.id = id
        self.char_loof = char_loof
        self.weapon_loof = weapon_loof
        self.wishnum = wishnum

    def get_wish_user(id: int):
        try:
            result: Tuple = database.load_data_sql(
                sql="""
                select *
                from user_wish
                where id = %s
                """,
                data=(id,),
            )[0]
            return WishUser(result[0], result[1], result[2], result[3])
        except:
            WishUser.add_wish_user(id)
            WishUser.update_wish_user(
                id=id, char_roof=0, weap_roof=0, custom_id=0)
            return WishUser(id, 0, 0, 0)

    def add_wish_user(id: int):
        database.table_update_sql(
            sql="""
            insert into user_wish values(%s, %s, %s, %s) 
            """,
            data=(id, 0, 0, 0),
        )
        return

    def update_wish_user(id: int, char_roof: int, weap_roof: int, custom_id: int):
        database.table_update_sql(
            sql="""
            update user_wish set char_roof = %s, weap_roof = %s, custom_id = %s where id = %s
            """,
            data=(char_roof, weap_roof, custom_id, id),
        )
        return
