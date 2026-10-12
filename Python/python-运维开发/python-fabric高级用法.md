---
title: Python Fabric高级用法
tags:
  - python/devops
  - python/fabric
  - python/ssh
aliases:
  - Fabric高级用法
  - Fabric2进阶
date: 2026-04-16
---

# Python Fabric高级用法

- 参考链接:https://cloud.tencent.com/developer/article/2336612

## fabric

> [!info] fabric简介
> fabric是基于paramiko的进一步封装,使用起来更加方便。fabric共有三个版本:fabric1、fabric2、fabric3,其中fabric3是非官方版本,所以不推荐使用,建议使用fabric2版本。 官方文档:www.fabfile.org/

相关笔记: [[python-Linux-operation]]

### 安装

```python
pip install fabric
#或者
pip install fabric2
#都是安装最新的官方版本。
```

---

### 连接

```sh
from fabric import Connection

conn = Connection(f"{user}@{host}:{port}",
                    connect_kwargs={"password": password},
                    connect_timeout=5,  # 5s超时
                  )

# 多个命令之间用&&或;连接
conn.run("ls")
```

- 关于`run()`方法的参数说明:

| 参数       | 解释                                                         |
| ---------- | ------------------------------------------------------------ |
| hide=True  | 服务器的输出信息不会在控制台打印                             |
| warn=True  | 忽略异常信息(即exit code不等于0的命令),会将异常信息输出到stderr,若设置False则会报SystemExit异常,之前在测试环境就是因为没有处理这个SystemExit异常(SystemExit和Exception是同级关系),导致整个进程崩溃 |
| pty=True   | 交互式伪终端时使用,其他不建议使用                           |
| watchers   | 监听Responder列表,自动响应                                  |
| out_stream | 文件对象,可以记录命令输出信息(fabric1版本的参数好像是stdout) |
| err_stream | 文件对象,可以记录命令错误输出信息                           |

- `ret = run()`方法返回值:

```
ret.stdout.strip()  # 正常输出
ret.stderr.strip()  # 异常输出
ret.failed  # 执行状态True or False
```

---

### 执行交互式命令

- 如果需要用户主动输入命令,可以使用==Responder==,第一个参数为需要匹配的字符串,第二个参数为响应的内容。由于交互式终端原因,此处需要设置`pty=True`,否则运行会提示:`no tty present and no askpass program specified`,若提示`xx user is not in the sudoers file. This incident will be reported`,需要通过登录root用户,修改sudoers文件。

> [!warning] 注意事项
> 模式匹配字符串要转义,否则会匹配不到,进而一直阻塞无响应(凡是需要用户介入的操作,都会一直卡在那里直到给出响应);response内容必须以`\n`紧接结尾,相当于输入完成后执行回车操作。

```python
from invoke import Responder
from fabric import Connection

sudopass = Responder(pattern=fr'\[sudo\] password for {user}:',
                     response=f'{password}\n',)
conn = Connection(f"{user}@{host}:{port}", connect_kwargs={"password": password})
# 如果要监听多个,则放入列表中传递给watchers
conn.run("sudo whoami", pty=True, watchers=[sudopass])
```

- with用法:

```python
# 执行完自动关闭
with Connection(f"{user}@{host}:{port}", connect_kwargs={"password": password}) as c:
    c.run("cd /home")

# with cd: 退出with上下文之后会回到当前登录用户的家目录
conn = Connection(f"{user}@{host}:{port}", connect_kwargs={"password": password})
with conn.cd("/home/yuqiuwen/PythonProjects/zhongxin/"):
    # 以下操作均在当前目录下执行
    ...

# with settings在fabric2中遗弃了
```

---

### 执行本地命令

```python
# Connection.local方法(实际上是invoke.run的装饰器)
conn.local("dir")

# 或者invoke.run
from invoke import run
```

---

### 操作多台机器

```python
from fabric import SerialGroup as Group

results = Group('web1', 'web2', 'mac1').run('uname -s')
print(results)
<GroupResult: {
    <Connection 'web1'>: <CommandResult 'uname -s'>,
    <Connection 'web2'>: <CommandResult 'uname -s'>,
    <Connection 'mac1'>: <CommandResult 'uname -s'>,
}>
for connection, result in results.items():
     print("{0.host}: {1.stdout}".format(connection, result))

web1: Linux
web2: Linux
mac1: Darwin
from fabric import SerialGroup as Group

# 当目标机器文件不存在时执行上传和解压缩操作
def upload_and_unpack(c):
    if c.run('test -f /opt/mydata/myfile', warn=True).failed:
        c.put('myfiles.tgz', '/opt/mydata')
        c.run('tar -C /opt/mydata -xzvf /opt/mydata/myfiles.tgz')

# 如果用户名不同的话可以用这种方式:
# Group('user@host1', 'user2@host2', 'user3@host3', connect_kwargs={'password': '123456'})
for connection in Group('host1', 'host2', 'host3', user='root', connect_kwargs={'password': '123456'}):
    upload_and_unpack(connection)
```

---

### 上传文件

> [!note] 上传文件说明
> fabric只能上传单个文件,如果想上传多个文件,有两种方案:本地打包之后上传,然后在远程服务器执行解压操作,或者通过遍历文件夹循环调用get上传,本地目录遍历用到了`pathlib2.Path`中的`rglob`方法。注意:远程路径如果不存在会报错。

```python
conn = Connection(f"{user}@{host}:{port}", connect_kwargs={"password": password})
sftp = conn.sftp()

def put(local_path, remote_path):
    local_path, remote_path = Path(local_path), Path(remote_path)

    if local_path.is_dir():
        for path in local_path.rglob('[!.]*'):  # 过滤掉以点开头的文件
            # 拼接远程路径,relative_to获取相对路径
            remote = remote_path.joinpath(path.relative_to(local_path))
            if path.is_file():
                check_remote_path(remote.parent, is_mkdir=True)  # 目标机器上不存在此路径需要创建
                conn.put(normpath(path), normpath(remote))

    # 上传单个文件
    else:
        check_remote_path(remote_path.parent, is_mkdir=True)
        if remote_isdir(remote_path):  # 若远程路径是一个目录,就将本地文件名作为默认名字
            remote_path = remote_path.joinpath(local_path.name)
        conn.put(normpath(local_path), normpath(remote_path))

def check_remote_path(remote_path, is_mkdir=False):
    """
    判断目标机器路径是否存在
    :param remote_path:
    :param is_mkdir: 若为True,则会创建此路径
    :return:
    """

    remote_path = normpath(remote_path)
    try:
        sftp.lstat(remote_path)
        return True
    except FileNotFoundError:
        if is_mkdir:
            try:
                sftp.mkdir(remote_path)
            except PermissionError:
                ret = conn.run(f"sudo mkdir {remote_path}", pty=True, watchers=[sudopass])
                return not ret.failed
        else:
            return False
```

---

### 下载文件

- fabric下载文件的方法和paramiko有略微细节差异,fabric下载文件时若本地路径不存在会自动创建,并且本地路径如果没提供文件名,会以远程文件名作为默认值,但前提是本地路径以`/`结尾,如果没有`/`,将以路径最后一部分作为文件名。

```python
def traverse_remote_files(remote_path: Path, local_path: Path):
    files_attr = sftp.listdir_attr(normpath(remote_path))
    for file_attr in files_attr:
        filename = file_attr.filename
        if filename.startswith('.'):  # 过滤以点开头的目录或文件
            continue
        # 此处的local和remote可能为目录,也可能为文件
        local, remote = local_path.joinpath(filename), remote_path.joinpath(filename)
        # 若为目录,则递归调用
        if stat.S_ISDIR(file_attr.st_mode):  # st_mode判断文件类型(目录还是文件)
            yield from traverse_remote_files(remote, local)
        else:
            yield remote

def remote_isdir(remote_path):
    """
    检查一个远程路径是否为目录
    :param remote_path:
    :return:
    """
    attr = sftp.lstat(normpath(remote_path))
    return stat.S_ISDIR(attr.st_mode)

def get(remote_path, local_path):
    local_path, remote_path = Path(local_path), Path(remote_path)
    if remote_isdir(remote_path):
        filepaths = traverse_remote_files(remote_path, local_path)
        for filepath in filepaths:
            relpath = filepath.relative_to(remote_path)
            local = local_path.joinpath(relpath)

            try:
                conn.get(normpath(filepath), normpath(local))
            except FileNotFoundError:
                print("文件不存在")
    else:
        if not local_path.suffix:   # 如果本地路径没有提供文件名,默认为远程文件名
            local_path = local_path.joinpath(remote_path.name)
        try:
            conn.get(normpath(remote_path), normpath(local_path))
        except FileNotFoundError:
            print("文件不存在")
```

---

## fab命令

fab --help查看具体命令含义,这里列举的是fabric2的常用fab命令参数,和fabric1版本有很大不同。

| 参数 | 解释                                        |
| ---- | ------------------------------------------- |
| -l   | 列举任务列表(被@task装饰的函数才能被识别) |
| -c   | 从指定的任务模块名加载(默认为fabfile.py)  |
| -r   | 从指定的根目录路径查找任务模块              |
| -f   | 指定配置文件路径                            |
| -H   | 指定目标主机,多个主机逗号隔开              |
| -V   | 显示Fabric、Paramiko、Invoke版本            |
| -w   | 和warn=True效果一样,出现异常不会结束       |

### 示例

```python
@task
def task1(c, param):
    print(f"hello world, today is {param}")

@task
def task2(c):
    ...

# 如果入口文件为fabfile.py,可以直接执行 fab -H localhost task2
```

> [!important] 注意事项
> 其中被`@task`装饰的函数必须有一个参数,否则会报:`TypeError: Tasks must have an initial Context argument!`。 假如入口文件不是fabfile.py且不指定的话,会报`Can't find any collection named 'fabfile'!`,fabric2中通过-c来指定加载的任务列表,**官方API文档也说明了:--collection后面的参数是模块名而不是具体文件名**。

- 比如上述的task函数存在于服务器`/home/yuqiuwen/PythonProjects/zhongxin/fab.py`路径下。

```python
"""通过本地调用远程服务器的脚本"""

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# fabric2中通过--参数名的形式来传递变量值,如果参数有空格,要用引号
conn.run(f"fab -c /home/yuqiuwen/PythonProjects/zhongxin/fab task1 --param '{now}'")
# 或者 -r指定查找目录
# conn.run(f"fab -r /home/yuqiuwen/PythonProjects/zhongxin/ -c fab task1 --param '{now}'")

>>> output: hello world, today is 2022-10-30 14:19:23

"""通过本地调用本地的脚本"""

from invoke import run

# windows环境下貌似给now参数加引号也会报错,不知道什么原因
run(f"fab -c 本地脚本路径 task1 --param '{now}'", out_stream=f, err_stream=f)
```

- 除此之外,还可以通过fab -l -F指定显示格式:

```sh
shell复制代码> fab -r ./ -c fab  -l -F json
output: {"name": "fab", "help": null, "default": null, "tasks": [{"name": "task1", "help": null, "aliases": []}, {"name": "task2", "help": null, "aliases": []}], "collections": []}
```

---

## 封装

```python
from fabric import Connection
from pathlib import Path
import stat
import logging

class FabConnection:
    def __init__(self, host, user, password, port=22, mylogger=None):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._sftp = None
        self._conn = None
        self.mylogger = mylogger
        self.connect()

    def connect(self):
        # 密钥文件方式
        # connect_kwargs={"key_filename": "/home/myuser/.ssh/private.key"},
        conn = Connection(f"{self._user}@{self._host}:{self._port}", connect_kwargs={"password": self._password})
        self._conn = conn
        self._sftp = conn.sftp()

    def get(self, remote_path, local_path):
        local_path, remote_path = Path(local_path), Path(remote_path)

        if self.remote_isdir(remote_path):
            filepaths = self.traverse_remote_files(remote_path, local_path)
            for filepath in filepaths:
                relpath = filepath.relative_to(remote_path)
                local = local_path.joinpath(relpath)

                try:
                    self._conn.get(self.normpath(filepath), self.normpath(local))
                    self.writer(f"download {relpath} successful!")
                except FileNotFoundError:
                    self.writer(f"FileNotFoundError: {filepath} -> {local}", level='error')

        else:
            if not local_path.suffix:   # 如果本地路径没有提供文件名,默认为远程文件名
                local_path = local_path.joinpath(remote_path.name)
            try:
                self._conn.get(self.normpath(remote_path), self.normpath(local_path))
                self.writer(f"download {remote_path} successful!")
            except FileNotFoundError:
                self.writer(f"FileNotFoundError: {remote_path} -> {local_path}", level='error')

    def put(self, local_path, remote_path):
        local_path, remote_path = Path(local_path), Path(remote_path)

        if local_path.is_dir():
            for path in local_path.rglob('[!.]*'):
                # 拼接远程路径,relative_to获取相对路径
                remote = remote_path.joinpath(path.relative_to(local_path))
                if path.is_file():
                    self.check_remote_path(remote.parent, is_mkdir=True)  # 目标机器上不存在此路径需要创建
                    self._conn.put(self.normpath(path), self.normpath(remote))
                    self.writer(f"upload {path} successful!")

        # 上传单个文件
        else:
            self.check_remote_path(remote_path.parent, is_mkdir=True)
            if self.remote_isdir(remote_path):  # 若远程路径是一个目录,就将本地文件名作为默认名字
                remote_path = remote_path.joinpath(local_path.name)

            self._conn.put(self.normpath(local_path), self.normpath(remote_path))
            self.writer(f"upload the file {local_path} successful!")

    def traverse_remote_files(self, remote_path: Path, local_path: Path):
        files_attr = self._sftp.listdir_attr(self.normpath(remote_path))
        for file_attr in files_attr:
            filename = file_attr.filename
            if filename.startswith('.'):  # 过滤以点开头的目录或文件
                continue
            # 此处的local和remote可能为目录,也可能为文件
            local, remote = local_path.joinpath(filename), remote_path.joinpath(filename)
            # 若为目录,则递归调用
            if stat.S_ISDIR(file_attr.st_mode):  # st_mode判断文件类型(目录还是文件)
                yield from self.traverse_remote_files(remote, local)
            else:
                yield remote

    def close(self):
        if self._conn:
            self._conn.close()
        if self._sftp:
            self._sftp.close()
        self._conn, self._sftp = None, None

    def writer(self, message, level=None):
        """
        自定义写入文件方法,同时支持logger或文件对象
        :param message:
        :param level:
        :return:
        """
        if self.mylogger:
            if isinstance(self.mylogger, logging.Logger):
                if not level:
                    self.mylogger.info(message)
                elif level == 'error':
                    self.mylogger.error(message)
                else:
                    self.mylogger.warning(message)
            else:
                self.mylogger.write(message + "\n")
        else:
            print(message + "\n")

    @staticmethod
    def normpath(path):
        """
        由于windows和linux操作系统不同,路径格式会出现不统一的情况,反斜杠不处理的话会出现很多问题
        替换windows路径中的\
        :param path:
        :return:
        """
        if isinstance(path, Path):
            path = str(path)
        return path.replace('\\', '/')

    def remote_isdir(self, remote_path):
        """
        检查一个远程路径是否为目录
        :param remote_path:
        :return:
        """
        attr = self._sftp.lstat(self.normpath(remote_path))
        return stat.S_ISDIR(attr.st_mode)

    def check_remote_path(self, remote_path, is_mkdir=False):
        """
        判断目标机器路径是否存在
        :param remote_path:
        :param is_mkdir: 若为True,则会创建此路径
        :return:
        """

        remote_path = self.normpath(remote_path)
        try:
            self._sftp.lstat(remote_path)
            return True
        except FileNotFoundError:
            if is_mkdir:
                try:
                    self._sftp.mkdir(remote_path)
                except PermissionError:
                    ret = self.run(f"sudo mkdir {remote_path}", pty=True, watchers=[self.sudo_pass])
                    return not ret[2]
            else:
                return False

    @property
    def sudo_pass(self):
        sudopass = Responder(pattern=fr'[sudo] password for {self._user}:', response=f'{self._password}\n', )
        return sudopass

    def run(self, cmd, hide=False, warn=True, pty=False, watchers=None):
        # hide=True控制台不打印运行信息,当out_stream不为空时,hide参数无效
        ret = self._conn.run(cmd,
                             hide=hide,
                             warn=warn,
                             pty=pty,
                             out_stream=self.mylogger,
                             err_stream=self.mylogger,
                             watchers=watchers,
                             encoding="utf8"
                             )
        stdout, stderr = ret.stdout.strip(), ret.stderr.strip()
        return stdout, stderr, ret.failed

    @property
    def conn(self):
        return self._conn

demo = FabConnection(host='172.16.101.222',user='xj',password='<password>')
demo.get('/home/xj/Desktop/dir_a','./')
demo.put('./','/home/xj/Desktop/dir_cc')
demo.run('ls -l')
```
