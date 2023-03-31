from flask import Flask,request,render_template,g,jsonify
import sqlite3

DATABASE = './database.db'

def check(db_name,table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    sql = '''SELECT tbl_name FROM sqlite_master WHERE type = 'table' '''
    cursor.execute(sql)
    values = cursor.fetchall()
    tables = []
    for v in values:
        tables.append(v[0])
    if table_name not in tables:
        return False # 可以建表
    else:
        return True # 不能建表
conn = sqlite3.connect(DATABASE)
#创建一个游标 cursor
cur = conn.cursor()
if (check(DATABASE,"tb") == False):
    sql_text_1 = '''CREATE TABLE tb
            (   fileid varchar(40) primary key,
                name varchar(40),
                time varchar(40),
                operator varchar(40),
                status varchar(40));
                '''
    # 执行sql语句
    cur.execute(sql_text_1)
if (check(DATABASE,"tb_already") == False):
    sql_text_2 = '''CREATE TABLE tb_already
            (   fileid varchar(40) primary key);
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

@app.route('/getList',methods = ['GET'])
def getList():
    g.cur.execute("select * from tb;")
    fileSet=g.cur.fetchall()
    fileList=list()
    for i in fileSet:
        l=list(i)
        l.append('新单')
        fileList.append(l)
    #获取already状态
    g.cur.execute("select * from tb_already;")
    alreadySet=g.cur.fetchall()
    for i in alreadySet:
        fileid=i[0]
        for u in fileList:
            if u[0]==fileid:
                u[-1]="已接单"
    return jsonify(fileList)

@app.route('/postList',methods = ['POST'])
def postList():
    filesDict=request.get_json()
    print(filesDict)
    fileList=list()
    for i in filesDict:
        fileList.append(list(i.values()))

    # 插入多条语句，注意sqlite使用?做占位符
    insert_many_sql = """insert into tb(name,fileid,time,operator,status) values(?,?,?,?,?);"""
    data_list = fileList
    g.cur.execute("delete from tb;")
    g.cur.executemany(insert_many_sql, data_list)
    g.db.commit()
    #把List中没有的从already表中删除
    g.cur.execute("select * from tb_already;")
    print(g.cur.fetchall())
    g.cur.execute("DELETE FROM tb_already where (select count(1) as num from tb where tb_already.fileid = tb.fileid) = 0;")
    g.cur.execute("select * from tb_already;")
    print(g.cur.fetchall())
    # g.cur.execute("select * from tb_already;")
    # alreadySet=g.cur.fetchall()
    # alreadyList=list()
    # for i in alreadySet:
    #     fileid=i[0]
    return "success"

@app.route('/setAlready',methods = ['POST'])
def setAlready():
    name_fileid=request.form['name']
    print(name_fileid)
    try:
        g.cur.execute("insert into tb_already(fileid) values('%s');"%(name_fileid.split(' ')[0]))
    except:
        return "false"
    return name_fileid

@app.route('/autoFilesSystem123',methods = ['GET'])
def autoFilesSystem123():
   return render_template("index.html")

if __name__ == '__main__':
   app.run("0.0.0.0","1024")