from this import d
import lib.sql as sql
from lib.yamlutil import yaml

uidListYaml = yaml(path='uidList_sql.yaml')
uidList = uidListYaml.load_yaml()

wishDataYaml = yaml(path='game_sql.yaml')
wishData = wishDataYaml.load_yaml()


def uidList_to_sql():
    for serverID, v in uidList.items():
        for userID, n in v.items():
            print()
            sql.database.table_update_sql(sql="insert into user_table values (%s, %s, %s)",
                                          data=(
                                              0,
                                              int(userID),
                                              str(n["name"]),
                                          )
                                          )


def wishData_toSql():
    for userID, v in wishData.items():
        print(type(userID))
        print(type(v["name"]))
        print(type(v["top"]))
        sql.write_sql(f"insert into user_wish values (%s, %s, %s, %s, %s)",
                      (int(userID), str(v["name"]), int(v["top"]), 0, 10,))
        #hoge = f"insert into user_wish values ({(int(userID))}, {str(v['name'])}, {int(v['top'])}, 0, 10)"
        # print(hoge)
        # sql.write_sql(hoge)


def wish_to_data():
    for userID, v in wishData.items():
        hoge = sql.load_sql("""
            Select id, name from user_wish""")

        for n in hoge:
            sql.write_sql(
                f"""
                    update user_table set id=%s where name =%s
                """,
                (
                    n[0],
                    n[1],
                )
            )


def aaa(server, id, uid, name, public):
    sql.database.table_update_sql(sql="insert into user_table values (%s, %s, %s)",
                                  data=(
                                      id,
                                      uid,
                                      name,
                                  )
                                  )
    if public == True:
        sql.PermitID.add_permit_id(server, id)


aaa()
