from flask import Flask ,render_template,request,redirect,session
import pymongo
import ybc_trans,ybc_china,ybc_pminfo
from flask import logging

app = Flask(__name__)

class users():
    def __init__(self):
        # 连接MongoDB 进入 ceshi表 test_set集合
        conn = pymongo.MongoClient('127.0.0.1', 27017)
        db = conn.ceshi  # 连接ceshi数据库，没有则自动创建
        self.my_set = db.test_set  # 使用test_set集合，没有则自动创建
        self.username = None

    def login(self,username,password):
        username_res = False
        password_res = False
        for i in self.my_set.find():
            if i["username"] == username:
                username_res = True
                if i["password"] == password:
                    password_res = True
                    self.my_set.update_one({'username': username}, {'$set': {'login': 1}})
                    self.username = username
                    return i["name"],"/"
        if username_res and password_res == False:
            return "密码输入错误","login.html"
        else:
            return '账号不存在', 'login.html'
    def login_check(self):
        if self.username != None:
            # 获取登录账号的信息
            login_res = self.my_set.find_one({'username':self.username})
            # 检测登录状态
            if login_res["login"] == 1:
                login_name = login_res['name']
                return login_name

    def logout(self):
        self.my_set.update_one({'login': 1}, {'$set': {'login': 0}})
    def register(self,name,username,pwd):
        register_res = False
        for i in self.my_set.find():
            if i["username"] == username:
                register_res = True
                return '账号已存在','register.html'
        if register_res == False:
            print(name,username,pwd)
            self.username = username
            msg = {"name":name,"username":username,"password":pwd,"login":1}
            self.my_set.insert_one(msg)
            return '注册成功','/'
    def fanyi(self,language,content):
        if language == "ZH":
            text = ybc_trans.zh2en(content)
            return text
        elif language == "EN":
            text = ybc_trans.en2zh(content)
            return text
    def PM25(self,cities):
        #空气检测
        pm_data = ybc_pminfo.pm25(cities)
        return pm_data
user_table = users()
user_table.login_check()

all_app = [[
    {'name': '在线翻译', 'url': '/fy','img':'fanyi.png'},
    {'name': '空气查询', 'url': '/kq','img':'kongqi.png'},
    {'name':'飞翔的小猿', 'url': '/fx','img':'feixiang.jpg'},
    {'name': '一起秀家乡', 'url': '/jx','img':'jaixiang.jpg'},
    {'name': 'TODO', 'url': '/todo','img':'todo.png'},
    {'name': '打字小游戏', 'url': '/dz','img':'dazi.png'}
    ],
    [
        {'name': '答题大挑战', 'url': '/dt'},
    ]
]

@app.route('/')
def home():
    user_name = user_table.login_check()
    return render_template('home.html',login_res=user_name,all_app=all_app)

@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == '' or password == '':
            return render_template('login.html',login_res='请输入正确信息')
        login_res, reverse_url = user_table.login(username, password)
        # print(login_res, reverse_url)

        if "/" == reverse_url:
            return redirect(reverse_url)
        else:
            return render_template(reverse_url,login_res=login_res)
    else:
        return render_template('login.html')

@app.route('/logout')
def Logout():
    user_table.logout()
    return redirect('/')

@app.route('/registered', methods=['GET', 'POST'])
def Registered():
    if request.method == 'POST':
        name = request.form["name"]
        username = request.form["username"]
        pwd1 = request.form["pwd1"]
        pwd2 = request.form["pwd2"]
        if name == '' or username == '' or pwd1 == '' or pwd2 == '':
            return render_template('register.html', register_res="请正确输入~")
        if pwd1 == pwd2:
            res,reverse_url = user_table.register(name, username, pwd1)
            if "/" == reverse_url:
                return redirect(reverse_url)
            else:
                return render_template(reverse_url, register_res=res)
        else:
            return render_template('register.html', register_res="两次密码不一致哦~")
    return render_template('register.html')

@app.route('/app/<name>', methods=['GET', 'POST'])
def App(name):
    print(request.method)
    if name == "fy":
        if request.args.get('content') is not None:
            if request.args.get('content').strip() == '':
                fy_res = '要正确输入呦~'
                return render_template('fy.html',fy_res=fy_res)
            language = request.args.get('xuanze')
            words = request.args.get('content').strip()
            fy_res = user_table.fanyi(language,words)
            return render_template('fy.html',words=words,fy_res=fy_res)
    if name == 'kq':
        if request.method == 'GET':
            cities = ybc_china.all_cities()
            return render_template('kq.html',cities=cities)
        if request.method == 'POST':
            cities = ybc_china.all_cities()
            pmjieguo = user_table.PM25(request.form['name'])
            pmcity = request.form['name']
            pmzhiliang = '空气质量：'+pmjieguo['pm25']
            pmyingxiang = '影响：'+pmjieguo['affect']
            pmjianyi = '建议：'+pmjieguo['advise']
            return render_template('kq.html',cities=cities,pmcity=pmcity,pmzhiliang = pmzhiliang,pmyingxiang=pmyingxiang,pmjianyi=pmjianyi)
    if name == 'fx':
        pass
    return render_template(name + '.html')

@app.route('/interaction/<name>')
def interaction(name):
    return render_template(name + '.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
