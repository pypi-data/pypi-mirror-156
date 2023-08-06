from flask import render_template, session, redirect
from facrsa_code.library.web.dataApi import get_task_info
from facrsa_code.library.analysis.main import web_action
from facrsa_code import app
import traceback


@app.route('/')
def index_page():
    uid, user = get_info()
    return render_template('index.html', uid=uid, user=user, title="Home")


@app.route('/examples')
def examples_page():
    uid, user = get_info()
    return render_template('examples.html', uid=uid, user=user, title="Examples")


@app.route('/faq')
def faq_page():
    uid, user = get_info()
    return render_template('faq.html', uid=uid, user=user, title="FAQ")


@app.route('/install')
def install_page():
    uid, user = get_info()
    return render_template('install.html', uid=uid, user=user, title="Install")


@app.route('/addtask')
def add_task_page():
    uid, user = get_info()
    return render_template('addtask.html', uid=uid, user=user, title="Add a task")


@app.route('/myfacrsa')
def my_task_page():
    uid, user = get_info()
    check_login()
    return render_template('myfacrsa.html', uid=uid, user=user, title="My faCRSA")


@app.route('/login')
def login_page():
    uid, user = get_info()
    return render_template('login.html', uid=uid, user=user, title="Login")


@app.route('/register')
def register_page():
    uid, user = get_info()
    return render_template('register.html', uid=uid, user=user, title="Register")


@app.route('/result/<string:tid>', methods=['GET'])
def result_page(tid):
    uid, user = get_info()
    try:
        task_info = get_task_info(tid)
        if uid == None and task_info['uid'] != 'public':
            return render_template('404.html')
        if task_info['status'] == '2':
            return redirect("http://127.0.0.1:5000/status/" + str(tid))
        elif task_info['status'] == '0':
            return redirect("http://127.0.0.1:5000/error/" + str(tid))
        return render_template('result.html', tid=tid, uid=uid, user=user, name=task_info['task_name'],
                               des=task_info['description'], title="Result")
    except TypeError:
        return render_template('404.html', title="404")


@app.route('/schedule/<string:tid>', methods=['GET'])
def schedule_page(tid):
    uid, user = get_info()
    url = "http://127.0.0.1:5000/task/" + str(tid)
    try:
        task_info = get_task_info(tid)
        if task_info['status'] == '1':
            return redirect("http://127.0.0.1:5000/result/" + str(tid))
        elif task_info['status'] == '0':
            return redirect("http://127.0.0.1:5000/error/" + str(tid))
        return render_template('schedule.html', tid=tid, uid=uid, user=user, name=task_info['task_name'],
                               mail=task_info['email'], url=url, title="Schedule")
    except TypeError:
        traceback.print_exc()
        return render_template('404.html', title="404")


@app.route('/task/<string:tid>', methods=['GET'])
def task_page(tid):
    try:
        task_info = get_task_info(tid)
        if task_info['status'] == '2':
            url = "http://127.0.0.1:5000/schedule/" + str(tid)
        elif task_info['status'] == '0':
            return redirect("http://127.0.0.1:5000/error/" + str(tid))
        else:
            url = "http://127.0.0.1:5000/result/" + str(tid)
        return redirect(url)
    except TypeError:
        return render_template('404.html', title="404")


@app.route('/error/<string:tid>', methods=['GET'])
def error_page(tid):
    uid, user = get_info()
    try:
        task_info = get_task_info(tid)
        if task_info['status'] == '2':
            return redirect("http://127.0.0.1:5000/status/" + str(tid))
        elif task_info['status'] == '1':
            return redirect("http://127.0.0.1:5000/result/" + str(tid))
        return render_template('error.html', uid=uid, user=user, name=task_info['task_name'],
                               des=task_info['description'], title="Error")
    except TypeError:
        return render_template('404.html', title="404")


@app.route('/showimg')
def show_img_page():
    return render_template('showimg.html')


@app.errorhandler(404)
def error_date(error):
    return render_template("404.html")


def check_login():
    uid, user = get_info()
    if uid == None:
        return render_template('login.html')


def get_info():
    uid = session.get('uid')
    user = session.get('username')
    return uid, user
