from flask import redirect, session, request, jsonify, url_for, render_template
from facrsa_code.library.util.sqliteUtil import sqliteUtil
from facrsa_code.library.util.configUtil import get_config
from facrsa_code import app
import hashlib
import datetime
import json
import os
import uuid
import sys

os.path.join(os.path.dirname(__file__), '../../../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from tasks import submit_task


@app.route('/api/getMyTask')
def get_my_task():
    sql = 'SELECT * FROM task where del = 0 and uid = ' + "'%s'" % (str(session.get('uid')))
    data = sqliteUtil().fetch_all(sql)
    try:
        num = len(data)
    except TypeError:
        num = 0
    result = {
        "code": 0,
        'msg': "",
        'count': num,
        "data": data
    }
    response = json.dumps(result, default=str)  # 将python的字典转换为json字符串
    return response


@app.route('/api/checkUserName', methods=['POST'])
def check_username():
    username = str(request.form['username'])
    sql = "SELECT * FROM user  WHERE username = '%s'" % (username)  # 根据用户名查找user表中记录
    result = sqliteUtil().fetch_one(sql)  # 获取一条记录
    if result:
        return str(200)
    else:
        return str(404)


@app.route('/api/login', methods=['POST'])
def user_login():
    if "logged_in" in session:  # 如果已经登录，则直接跳转到控制台
        return redirect(url_for("/"))

    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        sql = "SELECT * FROM user  WHERE username = '%s'" % (username)
        result = sqliteUtil().fetch_one(sql)
        if result:  # 如果查到记录
            salt = "facrsa2022"
            password = result['password']  # 用户填写的密码
            # 对比用户填写的密码和数据库中记录密码是否一致
            if password == hashlib.md5(
                    bytes(password_candidate + salt, encoding="utf8")).hexdigest():  # 调用verify方法验证，如果为真，验证通过
                # 写入session
                session['logged_in'] = True
                session['username'] = username
                session['uid'] = result['uid']
                data = {
                    "code": 200,
                    'msg': "success",
                }
                # 第一种
                response = jsonify(data)  # 将python的字典转换为json字符串
                return response
            else:  # 如果密码错误
                data = {
                    "code": 400,
                    'msg': "error (username / pwd)",
                }
                # 第一种
                response = jsonify(data)  # 将python的字典转换为json字符串
                return response
        else:
            data = {
                "code": 400,
                'msg': "user not found",
            }
            # 第一种
            response = jsonify(data)  # 将python的字典转换为json字符串
            return response


@app.route('/api/logout')
def user_logout():
    session.clear()
    return render_template('login.html')


@app.route('/api/register', methods=['POST'])
def user_reg():
    # if "logged_in" in session:  # 如果已经登录，则直接跳转到控制台
    #     return redirect(url_for("dashboard"))
    if request.method == 'POST':  # 如果提交表单
        # 从表单中获取字段
        username = request.form['username']
        password = request.form['password']
        email = request.form['mail']
        uid = str(uuid.uuid1())
        create_time = datetime.datetime.now()
        salt = "facrsa2022"
        pwd_new = hashlib.md5(bytes(password + salt, encoding="utf8")).hexdigest()
        sql = "INSERT INTO user(uid,username,password,email,create_time) VALUES ('%s','%s', '%s', '%s', '%s')" % (uid,
                                                                                                                  username,
                                                                                                                  pwd_new,
                                                                                                                  email,
                                                                                                                  create_time)
        result = sqliteUtil().insert(sql)
        if result == "400":
            return str(400)
        else:
            return str(200)


@app.route('/api/addTask', methods=['POST'])
def add_task():
    if request.method == 'POST':
        name = request.form['name']
        des = request.form['des']
        cf = request.form['cf']
        mail = request.form['mail']
        tid = session.get('tid')
        uid = session.get('uid')
        if uid == None:
            uid = "public"
        create_time = datetime.datetime.now()
        sql = "INSERT INTO task(tid,task_name,description,factor,email,create_time,uid) VALUES ('%s', '%s', '%s', '%s','%s', '%s', '%s')" % (
            tid, name, des, cf, mail, create_time, uid)
        result = sqliteUtil().insert(sql)
        if result == "400":
            del session['tid']
            data = {
                "code": 400,
                'msg': sql,
            }
            return jsonify(data)
        else:
            data = {
                "code": 200,
                'tid': tid,
            }
            submit_task(uid, tid)
            del session['tid']
            return jsonify(data)


@app.route('/api/delTask', methods=['POST'])
def del_task():
    if request.method == 'POST':
        sql = "UPDATE task SET del= 1 WHERE tid='%s' and uid = '%s'" % (request.form['tid'], session.get('uid'))
        result = sqliteUtil().update(sql)
        if result == "400":
            return str(400)
        else:
            return str(200)


@app.route('/test')
def test():
    res = get_config('storage')['upload_path']
    return jsonify(res)


# todo 上传压缩包时重命名，根据tid
# todo 如果是压缩包文件，上传到根目录，然后再interact.py中解压到initial目录
# todo 如果是原图，则上传到initital目录
@app.route('/uploadImg', methods=['POST'])
def upload_img_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'code': -1, 'filename': '', 'msg': 'No file part'})
        file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            return jsonify({'code': -1, 'filename': '', 'msg': 'No selected file'})
        else:
            try:
                user = session.get('uid')
                tid = session.get('tid')
                if session.get('tid'):
                    tid = session.get('tid')
                else:
                    tid = str(uuid.uuid1())
                    session['tid'] = tid
                if user == None:
                    user = "public"
                user_path = get_config('storage')["upload_path"] + "/" +  str(user)
                task_path = user_path + "/" + tid + "/initial"
                if file and allowed_file(file.filename):
                    origin_file_name = file.filename
                    filename = origin_file_name
                    if os.path.exists(user_path):
                        pass
                    else:
                        os.makedirs(user_path)
                    if os.path.exists(task_path):
                        pass
                    else:
                        os.makedirs(task_path)
                    file.save(os.path.join(task_path, filename))
                    return jsonify(
                        {'code': 0, 'filename': origin_file_name, 'msg': os.path.join(task_path, filename)})
                else:
                    return jsonify({'code': -1, 'filename': '', 'msg': 'File not allowed'})
            except Exception as e:
                return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})
    else:
        return jsonify({'code': -1, 'filename': '', 'msg': 'Method not allowed'})


@app.route('/api/delImg', methods=['POST'])
def del_img_file():
    if request.method == 'POST':
        import re
        base_path = re.sub('\\\\', '/', os.path.abspath(os.path.dirname(os.getcwd())))
        img_path = base_path + "/upload/" + str(session.get('uid')) + "/" + session.get('tid') + "/" + request.form[
            'img']
        try:
            os.remove(img_path)
            return jsonify({'code': 200, 'msg': ''})
        except Exception as e:
            print(e)
            return jsonify({'code': 500, 'msg': 'File deleted error'})
    else:
        return ({'code': 500, 'msg': 'Method not allowed'})


@app.route('/api/getSchedule/<tid>', methods=['GET'])
def get_task_schedule(tid):
    sql = "select status from task where tid = '%s'" % (tid)
    result = sqliteUtil().fetch_one(sql)
    return jsonify(result)


@app.route('/api/getResult/<tid>', methods=['GET'])
def get_result(tid):
    sql = "select * from result where tid = '%s'" % (tid)
    data = sqliteUtil().fetch_all(sql)
    try:
        num = len(data)
    except TypeError:
        num = 0
    result = {
        "code": 0,
        'msg': "",
        'count': num,
        "data": data
    }
    response = json.dumps(result, default=str)
    return response


def get_task_info(tid):
    sql = "select * from task where tid = '%s'" % (tid)
    result = sqliteUtil().fetch_one(sql)
    return result


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['jpg', 'png']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
