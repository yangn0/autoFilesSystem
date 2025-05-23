from flask import Flask, request, render_template, g, jsonify, make_response
import sqlite3
import traceback
import time

DATABASE = './database.db'


def check(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    sql = '''SELECT tbl_name FROM sqlite_master WHERE type = 'table' '''
    cursor.execute(sql)
    values = cursor.fetchall()
    tables = []
    for v in values:
        tables.append(v[0])
    if table_name not in tables:
        return False  # 可以建表
    else:
        return True  # 不能建表

overtime=15
conn = sqlite3.connect(DATABASE)
#创建一个游标 cursor
cur = conn.cursor()
if (check(DATABASE, "tb") == False):
    sql_text_1 = '''CREATE TABLE tb
            (   fileid varchar(40) primary key,
                name varchar(40),
                reason varchar(40),
                operator varchar(40),
                status varchar(40)
            );
                '''
    # 执行sql语句
    cur.execute(sql_text_1)
if (check(DATABASE, "tb_already") == False):
    sql_text_2 = '''CREATE TABLE tb_already
            (   fileid varchar(40) primary key,
                user varchar(40),
                timestamp DATETIME
            );
                '''
    # 执行sql语句
    cur.execute(sql_text_2)


def connect_db():
    return sqlite3.connect(DATABASE)


app = Flask(__name__)


@app.before_request
def before_request():
    g.db = connect_db()
    g.cur = g.db.cursor()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.commit()
        g.db.close()


@app.route("/set_cookies", methods=['POST'])
def set_cookies():
    name = request.form['name']
    # 设置响应体
    resp = make_response("success")
    # 设置coolie,默认有效期是临时cookie，浏览器关闭就失效
    resp.set_cookie("name", name)
    return resp


# 获取cookie
@app.route("/get_cookies")
def get_cookies():
    name = request.cookies.get("name")
    # print(type(response))  # 类型为：str
    if name == None:
        name = 'Null'
    return name


@app.route('/getList', methods=['GET'])
def getList():
    g.cur.execute("select * from tb;")
    fileSet = g.cur.fetchall()
    fileList = list()
    for i in fileSet:
        l = list(i)
        l.append('新单')
        fileList.append(l)
    #获取already状态
    g.cur.execute("select * from tb_already;")
    alreadySet = g.cur.fetchall()
    for i in alreadySet:
        fileid = i[0]
        for u in fileList:
            if u[0] == fileid:
                u[-1] = "已接单"
                u.append(i[1])
    return jsonify(fileList)


@app.route('/postList', methods=['POST'])
def postList():
    filesDict = request.get_json()
    # print(filesDict)
    fileList = list()
    for i in filesDict:
        fileList.append(list(i.values()))

    # 插入多条语句，注意sqlite使用?做占位符
    insert_many_sql = """insert into tb(name,fileid,reason,operator,status) values(?,?,?,?,?);"""
    data_list = fileList
    g.cur.execute("delete from tb;")
    g.cur.executemany(insert_many_sql, data_list)
    g.db.commit()
    #把List中没有的从already表中删除
    # g.cur.execute("select * from tb_already;")
    # print(g.cur.fetchall())
    # g.cur.execute(
    #     "DELETE FROM tb_already where (select count(1) as num from tb where tb_already.fileid = tb.fileid) = 0;"
    # )
    return "success"


@app.route('/setAlready', methods=['POST'])
def setAlready():
    name_fileid = request.form['name']
    user = request.form['user']
    print(name_fileid)
    print(user)
    if name_fileid.split(' ')[0] == "工作机获取数据失败":
        return {"errno":"false","data":"禁止接这一单！"}  # 禁止工作机接单
    try:
        # 获取user最近一次记录，如果没有则下一步
        g.cur.execute('''SELECT * FROM tb_already
            WHERE user = '%s'
            ORDER BY timestamp DESC
            LIMIT 1;''' % user)
        values = g.cur.fetchall()
        if(len(values)>=1):
            latest_time=values[0][2]
            if(time.time()-latest_time<=overtime):
                return {"errno":"false","data":"接单太快啦！请%d秒后再接下一单"%overtime}
        g.cur.execute(
            "insert into tb_already(fileid,user,timestamp) values('%s','%s','%d');"
            % (name_fileid.split(' ')[0], user, time.time()))
    except:
        traceback.print_exc()
        return {"errno":"false","data":"这一单被抢走啦，点击确定回到列表继续抢单吧(*￣︶￣)"}
    return {"errno":"success","data":name_fileid}


@app.route('/dack', methods=['GET'])
def dack():
    return render_template("index.html")


if __name__ == '__main__':
    app.run("0.0.0.0", "1024")
