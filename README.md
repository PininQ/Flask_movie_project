# 小花椒微电影网站

小花椒网站是一个基于Flask框架而搭建的视频类网站。


线上演示地址: [https://www.xhuajiao.top](https://www.xhuajiao.top)


## 实现功能

前台：会员登录及注册、会员中心、电影播放、
电影评论、电影收藏、Ta主页等等。

后台：
管理员登录、修改密码、标签管理、
电影管理、上映预告管理、会员管理、
评论管理、收藏管理、角色管理、
权限管理、管理员管理、日志管理、网站建议管理等等。

## 项目结构


```
Flask_movie_project/    <-- 根目录
├── app                <-- Web目录
│   ├── admin           <-- 后台业务逻辑
│   ├── home            <-- 前端业务逻辑
│   ├── __init__.py
│   ├── models.py       <-- 数据模型文件
│   ├── static          <-- 存放静态文件
│   └── templates       <-- 存放模板文件
├── app.py
├── logs               <-- 存放日志文件
├── manage.py          <-- Flask应用的启动程序
├── movie.sql          <-- 数据库建表语句
└── req.txt            <-- 项目依赖包
```

## 运行项目

- **安装项目所需依赖包**
    

```
pip install -r req.txt
```

- **导入数据库**


```
mysqldump -u 用户名 -p 数据库名 > 导出的文件名  

示例：mysqldump -u root -p root > movie.sql
```


- **克隆项目到本地**


```
git clone https://github.com/qinbin52qiul/Flask_movie_project.git
```
进入Flask_movie_project目录（按住Shift+鼠标右键，打开在此处打开shell）
```
python manage.py runserver -h 127.0.0.1 -p 5000（端口号任意）

```
在浏览器中访问[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

<font color="#DC143C">注：manage.py文件内容如下（如不是请修改）：</font>
```python
from app import app
from flask_script import Manager

manager = Manager(app)

if __name__ == "__main__":
    # app.run(debug=True)
    manager.run()
```

## 网站部分截图

网站前台

![image](https://raw.githubusercontent.com/qinbin52qiul/MarkdownPhotos/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182039.png)


![image](https://github.com/qinbin52qiul/MarkdownPhotos/blob/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182045.png?raw=true)

![image](https://github.com/qinbin52qiul/MarkdownPhotos/blob/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182049.png?raw=true)


![image](https://github.com/qinbin52qiul/MarkdownPhotos/blob/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182053.png?raw=true)


网站后台

![image](https://github.com/qinbin52qiul/MarkdownPhotos/blob/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182122.png?raw=true)

![image](https://github.com/qinbin52qiul/MarkdownPhotos/blob/master/movie/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20180619182159.png?raw=true)
