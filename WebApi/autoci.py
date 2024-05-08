import json
import sys
import time
import logging
from shutil import copyfile, copytree
from autocilib import *
import threading

# 分发函数
def dispatcher(request):
    # 将请求参数统一放入request 的 params 属性中，方便后续处理

    # GET请求 参数在url中，同过request 对象的 GET属性获取
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST', 'PUT', 'DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)

    # 根据不同的action分派给不同的函数进行处理
    action = request.params['action']

    if action == 'auto_ci_test':
        return AutoCITest(request)

    if action == 'get_log_list':
        return GetLogList(request)

    if action == 'get_temp_logs':
        return GetTempLogs(request)

    # if action == 'list':
    #     return list(request)

    # elif action == 'add':
    #     return add(request)

    # elif action == 'modify':
    #     return modify(request)

    # elif action == 'del':
    #     return del(request)
    #
    # else:
    #     return JsonResponse({'ret': 1, 'msg': '不支持该类型http请求'})


"""
获得所有任务日志列表
"""
def GetLogList(request):
    ret_loglist = []
    loglist = [f for f in os.listdir(build_path) if os.path.isdir(os.path.join(build_path, f))]
    for log in loglist:
        dic_loglist = {}
        dic_loglist['session_id'] = log
        dic_loglist['time'] = time.ctime(os.path.getmtime(os.path.join(build_path, log)))
        dic_loglist['size'] = os.path.getsize(os.path.join(build_path, log))
        ret_loglist.append(dic_loglist)

    return stdJsonResponse(True, data=ret_loglist)


"""
获得暂存log列表，用于检查进度
"""
def GetTempLogs(request):
    templogs = [f for f in os.listdir(build_path) if os.path.isfile(os.path.join(build_path, f))]
    return stdJsonResponse(True, data=templogs)


"""
检查任务进度，用于轮询，任务未结束则返回任务已经过时间，任务结束则返回0
"""
def CheckProcess(request, testname):
    temp_output = os.path.join(build_path, testname + "_log.txt")
    if not os.path.exists(temp_output):
        return JsonResponse({"res": 0})
    with open(temp_output, 'r', encoding='utf-8') as f:
        start_time = float(f.readline().split(':')[1].strip('\n'))
    now_time = time.time()
    spdtime = now_time - start_time
    return JsonResponse({"res": spdtime})


"""
CI触发自动化集成接口
"""
def AutoCITest(request):
    info = request.params['data']
    start_time = time.time()
    testvibe = AndroidAutoTestVibe(info['apkname'], info['apkaddr'], info['brand'], info['model'], info['testcase'],
                                   info['logdir'], info['extra'], start_time)

    testvibe.get_device(testvibe.brand, testvibe.model)

    testname = testvibe.testcase + "_" + time.strftime('%Y%m%d%H%M%S', time.localtime(start_time))

    test_output = os.path.join(build_path, testname + "_log.txt")
    logger.info("本次测试终端日志地址：" + test_output)

    with open(test_output, 'w', encoding='utf-8') as f:
        f.write('start_time:' + str(start_time) + '\n')

    tester = "AutoCI"
    test_session_id = ""
    logger.info("执行设备：" + testvibe.device + "，品牌：" + testvibe.brand + "，型号：" + testvibe.model)

    # 通过SFTP获得包体、安装apk
    transport = paramiko.Transport(('nas.xxx.xxx', 22))
    transport.connect(username='ci', password='verygame123')
    sftp = paramiko.SFTPClient.from_transport(transport)

    tempdl = '/root/coconutqa/tmpdl'
    tempapk = os.path.join(tempdl, 'test.apk')
    sftp.get(testvibe.apkaddr, tempapk)
    logger.info("获得包体：" + testvibe.apkaddr)

    install = subprocess.Popen(
        f'adb -s {testvibe.device} install {tempapk}',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    while True:
        if install.poll() is None:
            time.sleep(2)
        else:
            logger.info("apk install finished")
            break
    if install.stdout.read().splitlines()[1] != "Success":
        error = stderr(1, 0, "apk install faied")
        os.remove(tempapk)
        return stdJsonResponse(False, error=error)
    testvibe.set_install()
    os.remove(tempapk)

    # 调用自动化测试入口

    # 子线程
    # child_run = threading.Thread(target=RunTestEngine, args=(
    #     test_output, testname, device, testcase, tester
    # ))
    # child_run.start()
    # child_run.join()

    # temp_output = os.popen(f'python3 /root/coconutstudio/AirTestEngine/airtestengine/main.py --testname {testname} --device {device} --devicetype "Android" --testplan {testcase} --performanceTest "False" --tester {tester}').read()
    #
    # content = temp_output.split('\n')
    # i = 0
    # while i < len(content) or test_session_id == "":
    #     test_session_id = GetSessionIdInLine(content[0])

    try:
        with open(test_output, 'a', encoding='utf-8') as tstlg:
            # p = subprocess.Popen(
            #     fr'python F:\WorkSpace_Kay\Dev_Kay\airtestengine\main.py --testname {testname} --device {device} --devicetype "Android" --testplan {testcase} --performanceTest "False" --tester {tester}',
            #     stdout=subprocess.PIPE,
            #     universal_newlines=True)

            testvibe.set_running()
            p = subprocess.Popen(
                f'python3 /root/coconutstudio/AirTestEngine/airtestengine/main.py --testname {testname} --device {testvibe.device} --devicetype "Android" --testplan {testvibe.testcase} --performanceTest "False" --tester {tester}',
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True)
            tstlg.write("logging-start" + '\n')
            while True:
                if p.poll() is None:
                    tstlg.write(p.stdout.readline())
                    tstlg.flush()
                    logger.debug(p.stdout.readline())
                    if test_session_id == "":
                        test_session_id = GetSessionIdInLine(p.stdout.readline())
                else:
                    tstlg.write("logging-end")
                    break
            testvibe.set_running()
            # th = threading.Thread(target=getStdoutSession, args=(
            #     p, tstlg, test_session_id))
            # th.start()

        # 获得session id 先用笨办法，上面实时获取的readline办法无法正确获得。
        # with open(test_output, 'r', encoding='utf-8') as f:
        #     content = f.readlines()
        #     i = 0
        #     while i < len(content) or test_session_id == "":
        #         test_session_id = GetSessionIdInLine(content[0])
    except:
        os.remove(test_output)
        error = stderr(1, 0, "Unexpected error:" + str(sys.exc_info()[0]))
        return stdJsonResponse(False, error=error)

    remote_file = os.path.join('CoconutCI/logs_AutoTest', testname + '_log.txt')
    sftp.put(test_output, remote_file)
    transport.close()

    if test_session_id == "":
        os.remove(test_output)
        error = stderr(1, 0, "未找到本次测试的session id，请检查日志")
        return stdJsonResponse(False, error=error)

    logging.info("session id为：" + test_session_id)

    test_log_dir = os.path.join(build_path, test_session_id)

    copyfile(test_output, os.path.join(test_log_dir, testname + "_log.txt"))
    os.remove(test_output)

    if testvibe.logdir != "":
        try:
            copytree(test_log_dir, os.path.join(testvibe.logdir, test_session_id))
        except:
            error = stderr(1, 0, "导出日志错误，请检查参数")
            return stdJsonResponse(False, error=error)

    return stdJsonResponse(True)


"""
查看指定日志
"""
def GetLog(request, session, testcase):
    logger.info(request.GET)
    session_dir = os.path.join(build_path, session)
    log_dir = os.path.join(session_dir, testcase)
    if not os.path.isdir(session_dir) or not os.path.isdir(log_dir):
        return JsonResponse({'ret': 1, 'error': '没有查询到该任务日志'})
    ret_log = []
    with open(os.path.join(log_dir, 'log.txt'), 'r', encoding='utf-8') as f:
        fl = f.readlines()
        for line in fl:
            ret_log.append(line.strip('\n'))
    return JsonResponse({'ret': 0, 'log': ret_log})
