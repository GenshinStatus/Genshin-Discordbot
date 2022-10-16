from datetime import datetime
from email.policy import default
from typing import Tuple
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import Error


# 予め定数として接続先を定義しておきます
load_dotenv()
print(os.getenv('SQL'))

class database:
    __DSN = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user="postgres",  # ユーザ
        password=os.getenv('SQL'),  # パスワード
        host="localhost",  # ホスト名
        port="5432",  # ポート
        dbname="postgres")  # データベース名

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


class User:
    def __init__(self, server_id:int, user_id: int, user_name: str, uid: int, game_name: str, public:bool):
        self.server_id = server_id
        self.user_id = user_id
        self.user_name = user_name
        self.uid = uid
        self.game_name = game_name
        self.public = public

    def get_one_user(user_id: int, server_id: int):
        """
        user_idから一意のユーザー情報を取得します。
        """
        print(user_id)
        print(server_id)
        data = database.load_data_sql(
            sql="""
            select * from user_table where serverid = %s and id = %s
            """,
            data=(server_id, user_id, )
        )
        print(data)
        data = data[0]
        return User(data[0], data[1], data[2], data[4], data[5])

    def insert_user(user):
        """
        利用者情報を新規で追加します。
        この時Userオブジェクトは全ての値が保持されている必要があります。
        """
        # 一意制約違反に引っかかる場合がある気がするのでtry exceptしてます
        try:
            database.table_update_sql(
                sql="""
                insert into user_table values(%s, %s, %s, %s, %s, %s) 
                """,
                data=(user.server_id, user.user_id, user.user_name, user.uid, user.game_name, False)
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
            update user_table set user_name=%s, uid=%s, game_name=%s public=%s where serverid = %s and id = %s
            """,
            data=(user.user_name, user.uid, user.game_name, user.public, user.server_id, user.user_id)
        )
    
    def delete_user(server_id:int, user_id:int):
        """
        利用者情報を削除する場合に利用します。
        """
        database.table_update_sql(
            sql="""
            delete user_table where serverid = %s and id = %s limit = 1
            """,
            data=(server_id, user_id)
        )

    def uid_duplicate_check(server_id, uid):
        """
        UIDが被っているか確認する場合に利用します。
        """
        try:
            n = database.load_data_sql(
            sql="""
            select serverid, uid from user_table where serverid = %s and uid = %s
            """,
            data=(server_id, uid)
            )
            return True
        except:
            return False


class PermitID:
    def __init__(self, uid: int, d_name: str, g_name: str):
        self.uid = uid
        self.d_name = d_name
        self.g_name = g_name

    def get_uid_list(guild_id: int):
        """
        guild_idからUIDのlistを取得する関数です。
        genshin botでguildごとのuidlistを取得するために利用します。
        """
        # print(guild_id)
        result = database.load_data_sql(sql="""
        select uid, username, name
        from user_table
        where id in(select unnest(userid) from permit_ids where serverid = %s )""", data=(guild_id,))
        # print(result)
        data: list[PermitID] = [
            PermitID(uid=v[0], d_name=v[1], g_name=v[2])
            for v in result
        ]
        return data

    def add_permit_id(guild_id: int, user_id: int):
        """
        genshin botでuidlistを公開設定とした時にdatabaseにデータを追加する処理です。
        """
        # print(guild_id)
        try:
            database.table_update_sql(
                sql="""
                update permit_ids set userid = array_append(userid, %s) where serverid = %s and not (column @> array[%s])""",
                data=(user_id, guild_id, user_id,))
        except:
            database.table_update_sql(
                sql="""
                insert into permit_ids values(%s, array[%s])""",
                data=(guild_id, user_id,))

    def remove_permit_id(guild_id: int, user_id: int):
        """
        genshin botでuidlistを公開設定を解除した場合ときにuidを削除する処理です。
        """
        database.table_update_sql(
            sql="""
            update permit_ids set userid = array_remove(userid, %s) where serverid = %s
            """,
            data=(user_id, guild_id,)
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