# webServerApi
based Django, wrote in 2022

- 测试脚本引擎AutotestEngine:
- 自动化测试WebServer:
- 测试用例脚本:

工作流、工作环境
![image](https://github.com/LibraKay/webServerApi/assets/56251957/cfbccc7a-ded5-4fdf-8d6d-c83bb8f8db08)

TeamcityCI通过请求测试WebServer，对请求携带的指定设备、testcase调用TestEngine入口，并获得返回的测试报告testname_result.json
请求方式：buildstep的命令行中执行curl命令，具体参数见WebServerAPI/Proto

测试数据、测试报告暂存于服务器，后期可考虑使用数据库存放
脚本引擎以及测试服务器均部署于root@***.***.***

测试脚本引擎AutotestEngine
说明
项目gitlab：
基于airtest的多设备、多case的脚本调用工具。Airtest脚本客户端工具:https://airtest.netease.com/
配置
测试用例路径配置于utils.py中的ScriptsDir变量
测试日志
- logs/testname/testcase/device，每一级都有该级别的日志。
- 总日志目录logs，下一级为testname文件夹（每次调用测试脚本需要指定本次测试的testname，CI触发WebAPI调用时testname默认为当时的时间，确保独一无二）。
- testname下包含：
  1. 该次testname日志testname_log.txt，记录本次test开始和结束时间，在main.py中调用并打印，可自定义任意需要日志内容。
  2. 该次testname中指定运行的所有testcase日志（分别位于每个testcase文件夹内）。
- testcase下包含：
  1. 该条testcase运行日志testcase_log.txt，包含每个设备的执行结果，有log和html形式展现。
  2. 该条testcase被每个设备执行的日志，分别位于每个device文件夹内。
  3. 执行进度case_process.json，记录执行情况（所有设备是否执行完毕）。
- device下包含：该设备执行该条testcase产生的log.txt以及产生的html文件。
Branch
- main分支为锁定分支，有修改需求需要新建分支修改后发起issue、merge request以merge至main
安装依赖
通过pip安装根目录的requirements.txt中的配置包
pip install -r requirements.txt
启动命令
python/python3 main.py 
    --testname demo                             #测试名称
    --device emulator-5554,emulaotr-5556        #设备号：以逗号隔开，usb连接写udid，wifi使用iip
    --testcase test1,test2                      #需要运行的testcase，用逗号隔开
可选参数（待拓展）：--devicetype 默认为安卓 --performanceTest 性能测试开关

自动化测试WebServer
说明
项目gitlab：
基于python django框架的webserver，用于接受http请求发起测试任务、查询日志、设备列表等功能
服务器路径: folder /root/coconutstudio/webapiserver
配置
目前主要使用的app为AutoTestApi，
CI响应逻辑在AutoTestApi/autotest.py中，
引擎入口路径、测试日志路径等为写在AutoTestApi/lib/autotestlib.py中的变量，
所有连接设备存放在AutoTestApi/info/devices.json，在每次调用GetAllDevices时初始化，记录所有设备信息以及状态，标识是否使用中。
日志、响应结果
服务器处理请求日志存放在AutoTestApi/info/testname_log.txt，引擎测试结果存放在同目录下的testname_result.json
安装依赖
通过pip安装根目录的requirements.txt中的配置包
pip install -r requirements.txt
启动命令
启动 webapiserver，需要使用python3(机器有python2和3的环境以及venv)
python3 manage.py runserver 0.0.0.0:1024
本地调试时，需要根据本地python环境修改入口命令python/python3（包括调用引擎入口）

WebServerAPI/Proto
url：host/test/api
CI集成自动测试通信协议：host/test/api  HTTP Method:POST 
data为request.body
需要携带参数action，以被服务端分发函数识别执行操作
运行流程为：通过sftp从nas取包-对所有设备进行安装apk-
请求消息样式：
{
    "action":"AutoCITest",
    "data":{
        "apkname":    "com.cis.jiangnan.huawei",
        "apkaddr":"CoconutCI/CIS_FrameworkValidator/HuaWei/JANA-Huawei_555/com.cis.jiangnan.huawei-HuaWei-2.1.0-86-Signed-2022_08_18_15_17_20.apk",
"device": {"HONOR":["KNT-UL10","honor1","honor2"], "OnePlus": ["oneplus1", "oneplus2"], "XiaoMi": "all"}
        "testcase":     "test1,test2"
        "logdir":         "/root/coconutqa/log/autocitest", 没有则为""
        "extra":          没有则为""
    }
}
返回：执行成功则返回携带测试result的data，失败返回error code 1or2以及错误堆栈data
携带result的返回消息格式为json
[图片]
同时服务器端产生测试result日志json文件于info文件夹下，并将该文件通过sftp上传至nas

待开发内容
ToDoList
服务端通过获取对应单个testcase和device的log.txt以获得测试结果并合并为json
服务器端设备json文件独立于业务逻辑，设置初始化接口，获取设备列表方式为读取该json文件
任务执行时将设备json文件标识为busy状态，实时改变，方便外部接口动态查看设备是否繁忙
并发访问处理
aab安装（目前仅支持apk）
iOS设备测试支持
可优化的待开发内容
Mongo数据库
- mongo数据库的存储位置为
docker run -d -p 27017:27017 -v /var/ftp/mongodb:/data/db --name mongo mongo
使用上述命令启动mongo，mongo数据在/var/ftp/mongodb里

网页VUE+vite【待开发】
项目：https://developer.coconut.is:3737/francis.zheng/ciscoconuttest
使用了vite+vue框架
接入了mongo数据库，并展示测试结果。.
FTP服务
服务器需要搭建FTP服务器，接收引擎运行的断言截图。同时作为资源层让网页报表端读取截图
1. 安装vsftpd
  - centos使用yum
  - ubuntu使用apt-get
2. 安装完毕后将对应的配置文件vsftpd.conf修改
  - centos 对应路径为 /etc/vsftpd/vsftpd.conf
  - ubuntu 对应路径为 /etc/vsftpd.conf
  - 若是找不到，使用 find / -name vsftpd.conf 来查找

ps1： 开启匿名访问（已经在vsftpd.conf配置），匿名访问地址为/srv/ftp（对应的参数为anon_root）
ps2： ftp服务路径 /srv/ftp/[文件夹] 中根目录文件夹权限设置为 755
                   根目录文件夹内文件夹权限设置为777

3. 运行
4. systemctl start vsftpd


nginx服务
路由ftp服务，可以考虑用http.server全面替换
启动命令
docker run -d -p 19000:80 -v /opt/coconuttest/conf.d:/etc/nginx/conf.d -v /var/ftp/pub:/home/ftp --name test-nginx nginx
- nginx配置在路径/opt/coconutest/conf.d中
- ftp挂载了/var/ftp/pub目录

