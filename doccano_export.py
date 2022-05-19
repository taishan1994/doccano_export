"""
连接doccano自带的sqlite3数据库，并生成标注文件
"""
import sqlite3

conn = sqlite3.connect(r'C:\Users\Administrator\doccano\db.sqlite3')

cursor = conn.cursor()


def get_span_by_project_id(project_id):
    """根据项目id获取实体识别标注结果"""
    sql = """
        with tmp1 AS (
            SELECT
                t1.id,
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
                "label": d[5]
            })
            e_tmp[d[1]] = tmp
        else:
            e_tmp[d[1]]["relations"].append({
                "id": d[0],
                "start_offset": d[2],
                "end_offset": d[3],
                "label": d[5]
            })
    return e_tmp



project_id = 2

span_data = get_span_by_project_id(project_id)
relation_data = get_rel_by_project_id(project_id)
# print(span_data)
# print(relation_data)


res = []
# 合并要素和关系
for k,v in relation_data.items():
    span_data[k]["relations"] = v["relations"]
    res.append(str(span_data[k]))

with open('./doccano_ext.json.', 'w', encoding="utf-8") as fp:
    fp.write("\n".join(res))

cursor.close()
conn.close()
