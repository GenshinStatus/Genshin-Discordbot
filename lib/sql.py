import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import Error

def connection():
    load_dotenv()
    print(os.getenv('SQL'))
    dsn = os.environ.get('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 
                            user="postgres",        #ユーザ
                            password=os.getenv('SQL'),  #パスワード
                            host="localhost",       #ホスト名
                            port="5432",            #ポート
                            dbname="postgres"))    #データベース名
    return psycopg2.connect(dsn)

class sql:
    def load_sql(execute: str ,default: any = dict()) -> any:
        """
        sqlを読み込んでそのままDictとかListにします。
        読み込めなかった場合にはdefaultの値を返します。
        """
        try:
            load_dotenv()
            connector =  psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 
                            user="postgres",        #ユーザ
                            password=os.getenv('SQL'),  #パスワード
                            host="localhost",       #ホスト名
                            port="5432",            #ポート
                            dbname="postgres"))    #データベース名

            cursor = connector.cursor()
            cursor.execute(execute)
            result = cursor.fetchall() 
            return result
        except:
            return default
        finally:
            connector.commit()
            cursor.close()
            connector.close()

    def load_data_sql(execute: str ,data: any) -> any:
        """
        sqlを読み込んでそのままDictとかListにします。
        読み込めなかった場合にはdefaultの値を返します。
        """
        try:
            load_dotenv()
            connector =  psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 
                            user="postgres",        #ユーザ
                            password=os.getenv('SQL'),  #パスワード
                            host="localhost",       #ホスト名
                            port="5432",            #ポート
                            dbname="postgres"))    #データベース名

            cursor = connector.cursor()
            cursor.execute(execute,data)
            result = cursor.fetchall() 
            return result
        finally:
            connector.commit()
            cursor.close()
            connector.close()

    def write_sql(execute: str, data) -> any:
        """
        sqlを読み込んでそのままDictとかListにします。
        読み込めなかった場合にはdefaultの値を返します。
        """
        try:
            load_dotenv()
            connector =  psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 
                            user="postgres",        #ユーザ
                            password=os.getenv('SQL'),  #パスワード
                            host="localhost",       #ホスト名
                            port="5432",            #ポート
                            dbname="postgres"))    #データベース名

            cursor = connector.cursor()
            print(execute)
            print(data)
            cursor.execute(execute,data)
        finally:
            connector.commit()
            cursor.close()
            connector.close()

class UID:
  def __init__(self,uid: int, d_name: str, g_name: str):
    self.uid = uid
    self.d_name = d_name
    self.g_name = g_name

  def get_uid_list(guild_id):
    # sqlでデータとってくるやつ
    print(guild_id)
    result = sql.load_data_sql(execute="""
        select uid, username, name
        from user_table
        where id in(select unnest(userid) from permit_ids where serverid = %s )""", data=(guild_id,))
    print(result)
    data: list[UID] = [UID(uid=v[0], d_name=v[1], g_name=v[2]) for v in result]
    return data

  def set_uid_list(guild_id, user_id, user_name, uid, game_name, public):
    # sqlでデータセット
    print(guild_id)
    sql.write_sql(execute="""
        insert into user_table values (%s, %s, %s, %s, %s, %s)""", 
        data=(guild_id,user_id,user_name,uid,game_name,public))
    return 

  def update_uid_list(where,set,data):
    # sqlでデータセット
    sql.write_sql(execute=f"""
        update user_table set {set} where {where}""", 
        data=data)
    return 

class channel:
  def __init__(self,guilt_id: int, channel_id: int):
    self.guilt_id = guilt_id
    self.channel_id = channel_id

  def get_channel(guild_id):
    # sqlでデータとってくるやつ
    print(guild_id)
    result = sql.load_data_sql(execute="""
        select *
        from server_table
        where serverid = %s""", data=(guild_id,))
    print(result)
    data: list[channel] = [channel(guilt_id=v[0], channel_id=v[1]) for v in result]
    return data
