from flask import Flask, render_template
from flask import abort, request, redirect, session
import pymysql
from datetime import datetime

app = Flask(__name__,
            template_folder='template')

db=pymysql.connect(user='root',
                    passwd = 'avante',
                    host = 'localhost',
                    db='web',
                    charset='utf8',
                    cursorclass=pymysql.cursors.DictCursor)

app.config['ENV'] = 'Development'
app.config['DEBUG'] = True
app.secret_key = 'who are you?'

def who_am_i():
    if 'user' in session:
        user=session['user']['name']
    else:
        user='Hi everyone!!'
    return user

def am_i_here():
    return True if 'user' in session else False

def get_menu():
    if am_i_here() == False:
        return '현재 시간은 '+ datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = db.cursor()
    cur.execute(f"""
        select id, title from topic
    """)
    menu_list=cur.fetchall()
    menu=[]
    for i in menu_list:
        menu.append(f"""
            <li><a href='{i['id']}'>{i['title']}</li>
        """)
    return "\n".join(menu)

@app.route('/')
def index():
    if am_i_here() == True:
        title='안녕하세요? 게시판 입니다.'
    else:
        title='Log in 해주세요'
    
    return render_template('template.html',
                            user = who_am_i(),
                            title= title,
                            menu = get_menu())

@app.route('/login', methods =['GET','POST'])
def login():
    if am_i_here() == True:
        return redirect('/')
    else:
        title = '로그인 해주세요'
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"""
            select id, name from author
                where name ='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            title = ' 정말 없은 id 입니다.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, password from author
                    where name = '{request.form['id']}' and
                    password = SHA2('{request.form['pw']}', 256)
            """)
            user=cur.fetchone()
            if user is None:
                title = ' 없는 password 입니다.'
            else:
                session['user'] = user
                return redirect('/')
    return render_template('login.html',
                            user = who_am_i(),
                            title = title)

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/join', methods = ['GET','POST'])
def join():
    if am_i_here() == True:
        return redirect('/')
    else:
        title = 'Login 을 위해서 먼저 가입 부탁드립니다.'
    if request.method == 'POST':
        cur = db.cursor()
        cur.execute(f"""
            select name from author where name = '{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            cur = db.cursor()
            cur.execute(f"""
                insert into author (name, profile, password)
                values ('{request.form['id']}',
                        '{request.form['pf']}',
                        SHA2('{request.form['pw']}', 256))
            """)
            db.commit()
            return redirect('/')
        else:
            title='등록하신 id 는 이미 있읍니다.'
    return render_template('join.html',
                            user=who_am_i(),
                            title=title)

@app.route('/withdraw', methods =['GET','POST'])
def withdraw():
    if am_i_here() == False:
        return redirect('/')
    else:
        if request.method == 'POST':
            if request.form['subject'] ==  'YES':
                cur=db.cursor()
                cur.execute(f"""
                    delete from author where name = '{session['user']['name']}'
                """)
                session.pop('user',None)
                db.commit() 
                title = '회원 탈퇴 요청이 처리되었읍니다.'
            else:
                title = '회원 탈퇴 요청을 반려하셨읍니다.'
            return render_template('template.html',
                                    user = who_am_i(),
                                    menu = get_menu(),
                                    title = title)
        else:
            title="정말 회원 탈퇴를 원하시나요?"
    return render_template('withdraw.html',
                            user=who_am_i(),
                            title=title )

@app.route('/favicon.ico')
def favicon():
    return abort(404)
app.run(port='5000')