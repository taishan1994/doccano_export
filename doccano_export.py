"""
连接doccano自带的sqlite3数据库，并生成标注文件
"""
import sqlite3
from pprint import pprint

conn = sqlite3.connect(r'C:\Users\Administrator\doccano\db.sqlite3')

cursor = conn.cursor()

# 用于判别是否导出经过验证的，True为导出经过验证的
confirm = True
# 用于控制是否导出实体标注
export_entities = True
# 用于控制是否导出关系标注
export_relations = False

def get_span_by_project_id(project_id):
    """根据项目id获取实体识别标注结果"""
    if confirm:
        sql = """
            with tmp1 AS (
                SELECT
                    t2.example_id as id,
                    t1.text 
                FROM
                    main.examples_example t1
                    JOIN examples_examplestate t2 ON t1.id = t2.example_id 
                WHERE
                    t1.project_id = {}
                ) SELECT
                t1.*,
                t2.start_offset,
                t2.end_offset,
                t2.label_id,
                t3.text AS label_text,
                t2.id AS span_id 
            FROM
                tmp1 t1
                JOIN labels_span t2 ON t1.id = t2.example_id
                JOIN label_types_spantype t3 ON t3.id = t2.label_id    
        """.format(project_id)
    else:
        sql = """
            with tmp1 AS (
                SELECT
                    t1.id,
                    t1.text 
                FROM
                    main.examples_example t1
                WHERE
                    t1.project_id = {}
                ) SELECT
                t1.*,
                t2.start_offset,
                t2.end_offset,
                t2.label_id,
                t3.text AS label_text,
                t2.id AS span_id 
            FROM
                tmp1 t1
                JOIN labels_span t2 ON t1.id = t2.example_id
                JOIN label_types_spantype t3 ON t3.id = t2.label_id    
        """.format(project_id)
    cursor.execute(sql)
    data = cursor.fetchall()
    example_id_set = set()
    e_tmp = {}
    for d in data:
        if d[0] not in example_id_set:
            example_id_set.add(d[0])
            tmp = {"id": d[0], "text": d[1], "relations": [], "entities": []}
            tmp["entities"].append({
                "id": d[6],
                "start_offset": d[2],
                "end_offset": d[3],
                "label": d[5]
            })
            e_tmp[d[0]] = tmp
        else:
            e_tmp[d[0]]["entities"].append({
                "id": d[6],
                "start_offset": d[2],
                "end_offset": d[3],
                "label": d[5]
            })
    return e_tmp


def get_rel_by_project_id(project_id):
    """根据项目id获取关系标注结果"""
    if confirm:
        sql = """
            with tmp1 AS (
                SELECT
                    t1.id,
                    t1.example_id,
                    t1.from_id_id,
                    t1.to_id_id,
                    type_id 
                FROM
                    labels_relation t1
                    JOIN examples_example t2 ON t1.example_id = t2.id 
                    JOIN examples_examplestate t3 ON t1.example_id = t3.example_id
                WHERE
                    project_id = {}
                ) SELECT
                t1.*,
                t2.text AS relation_text 
            FROM
                tmp1 t1
                JOIN label_types_relationtype t2 ON t1.type_id = t2.id
        """.format(project_id)
    else:
        sql = """
            with tmp1 AS (
                SELECT
                    t1.id,
                    t1.example_id,
                    t1.from_id_id,
                    t1.to_id_id,
                    type_id 
                FROM
                    labels_relation t1
                    JOIN examples_example t2 ON t1.example_id = t2.id 
                WHERE
                    project_id = {}
                ) SELECT
                t1.*,
                t2.text AS relation_text 
            FROM
                tmp1 t1
                JOIN label_types_relationtype t2 ON t1.type_id = t2.id
        """.format(project_id)
    cursor.execute(sql)
    data = cursor.fetchall()
    example_id_set = set()
    e_tmp = {}
    for d in data:
        if d[1] not in example_id_set:
            example_id_set.add(d[1])
            tmp = {"id": d[1], "text": "", "relations": [], "entities": []}
            tmp["relations"].append({
                "id": d[0],
                "from_id": d[2],
                "to_id": d[3],
                "type": d[5]
            })
            e_tmp[d[1]] = tmp
        else:
            e_tmp[d[1]]["relations"].append({
                "id": d[0],
                "from_id": d[2],
                "to_id": d[3],
                "type": d[5]
            })
    return e_tmp


def show_tables():
    """查看当前数据库所有的表"""
    sql = """select name from sqlite_master"""
    cursor.execute(sql)
    data = cursor.execute(sql)
    print("当前所有表：")
    for d in data:
        print(d[0])


def get_project_id():
    """获取最近更新过的文本及项目id"""
    sql = """
        select project_id, text from examples_example order by updated_at desc limit 1
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    pprint(data[0])
    return data[0][0]


show_tables()
project_id = get_project_id()

span_data = get_span_by_project_id(project_id)
relation_data = get_rel_by_project_id(project_id)
# print(span_data)
# print(relation_data)


res = []

if export_entities:
    if export_relations:
        # 合并要素和关系
        for k, v in relation_data.items():
            span_data[k]["relations"] = v["relations"]
            res.append(str(span_data[k]).replace("'", '"'))

    else:
        for k,v in span_data.items():
            res.append(str(span_data[k]).replace("'", '"'))

with open('./data/doccano_ext.json.', 'w', encoding="utf-8") as fp:
    fp.write("\n".join(res))

cursor.close()
conn.close()
