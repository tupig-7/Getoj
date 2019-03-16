from bs4 import BeautifulSoup
from tkinter import messagebox
import tkinter
import urllib
import requests
import sys
import io
import re
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

#保存问题的html函数，传入网址链接
def getHtml(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    html = response.read()
    return html

def saveHtml(file_name,file_content):
    with open(file_name.replace('/','_')+'.html','wb') as f:
        f.write(file_content)

#将代码写入txt文件
def save(filename, contents):
    fh = open(filename, 'w', encoding='utf-8')
    fh.write(contents)
    fh.close()


def login(username, password, top):
    # 登录时需要POST的数据
    data = {'user_id1': username,
            'password1': password,
            'goto:http': '//172.16.94.19:8080/JudgeOnline/login?action=login',
            }

    # 设置请求头
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    # 登录时表单提交到的地址（用开发者工具可以看到）
    login_url = 'http://172.16.94.19:8080/JudgeOnline/login?action=login'

    # 构造Session
    session = requests.Session()

    # 在session中发送登录请求，此后这个session里就存储了cookie
    # 可以用print(session.cookies.get_dict())查看
    resp = session.post(login_url, data)

    # 登录后才能访问的网页
    url = 'http://172.16.94.19:8080/JudgeOnline/status?result=0&user_id=' + username + "&top=" + top

    # 发送访问请求
    resp = session.get(url)
    html_doc = resp.content.decode('utf-8')
    # 使用BeautifulSoup解析Html
    soup = BeautifulSoup(html_doc, "lxml")
    num = 0
    sum = 0 #统计当前页提交总数
    for tag in soup.select("td"):
        num = num + 1
        if (num >= 16 and (num - 16) % 9 == 0):
            # 获取问题原始地址
            url_problem = "http://172.16.94.19:8080/JudgeOnline/" + soup.select("td")[num + 1].select('a')[0].attrs[
                "href"]
            problem_id = soup.select("td")[num + 1].select('a')[0].string
            dir = "F:\\images\\oj\\" + soup.select("td")[num + 1].select('a')[0].string
            html = getHtml(url_problem)
            saveHtml(dir, html)
            # 获取解决问题的提交ID

            # 访问新的url
            url = "http://172.16.94.19:8080/JudgeOnline/showsource?solution_id=" + tag.string
            resp2 = session.get(url)
            html_doc = resp2.content.decode('utf-8')
            # 使用BeautifulSoup解析Html
            soup2 = BeautifulSoup(html_doc, "lxml")
            code = soup2.select('pre')[0].string
            save(dir + '.txt', code)
            # lastIndex用来记录当前页最后一个提交的序号
            lastIndex = tag.string
            sum = sum + 1
    #返回当前页提交总数和最后一次提交的序号
    return sum, lastIndex

def draw():
    str = tkinter.Tk()
    str.title("爬去OJ代码")
    str.geometry("500x380")

    # add lable_title
    lp_title = tkinter.Label(str, text='爬取OJ代码', font=("Arial Black", 22), fg='lightblue')
    lp_title.place(x=180, y=80)

    # add copyright_lable
    copyright_lable = tkinter.Label(str, text='EverythOne @ copyright')
    copyright_lable.pack(side='bottom')

    # add name
    name_text = tkinter.Variable()
    name_lb = tkinter.Label(str, text='用户名：', font=('微软雅黑', 13))
    name_lb.place(x=160, y=160)
    name_input = tkinter.Entry(str, textvariable=name_text, width=20)
    name_input.place(x=220, y=160)

    # add password
    pwd_text = tkinter.Variable()
    pwd_lb = tkinter.Label(str, text='密码：', font=('微软雅黑', 13))
    pwd_lb.place(x=160, y=195)
    pwd_input = tkinter.Entry(str, width=20, textvariable=pwd_text)
    pwd_input.place(x=220, y=195)

    # username  and password is real
    def login_func():
        if name_text.get() == "":
            msg = "用户名不能为空"
        elif pwd_text.get() == "":
            msg = "密码不能为空"
        elif pwd_text.get() != "" and name_text.get() != "":
            msg = "登陆成功"
        else:
            msg = ""
        pwd_lb = tkinter.Label(str, text=msg, font=('微软雅黑', 11), fg='red')
        pwd_lb.place(x=200, y=245)

    # add login_button
    login_button = tkinter.Button(str, text='开始爬取', font=('微软雅黑', 12),width=15, command=str.quit)
    login_button.place(x=200, y=240)
    str.mainloop()
    return name_text.get(), pwd_text.get()
if __name__ == '__main__':

    username, password = draw()
    top = ""
    sum, top = login(username, password, top)
    print(sum, top)
    while(sum == 20):
       sum, top = login(username, password, top)
    tkinter.messagebox.showinfo(title="OK", message="获取完成")

