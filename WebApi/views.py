import json
import logging
import os
import subprocess
import sys
import time
from urllib.parse import parse_qs

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from WebApi.configReader import *
from qc_tool.mongoApi import Mongo_Handler
from qc_tool.remotetool import RemoteClient


# Create your views here.
root_path = os.path.dirname(os.path.abspath(__file__))
os.environ['WORKSPACE'] = root_path
sys.path.append(root_path)
tool_root_path = os.path.join(root_path, "..")
tool_path = os.path.join(tool_root_path, "qc_tool")
test_module_path = os.path.join(tool_root_path, "script")
sys.path.append(tool_path)
sys.path.append(test_module_path)

@require_http_methods(['GET'])
def test(request):
    return HttpResponse("test")

@require_http_methods(['GET'])
def getTestModules(request):
    '''
    获取可测试模块
    '''
    print(request)
    test_module = os.path.join(test_module_path, "testplan.json")
    with open(test_module, 'r', encoding='utf-8') as f:
        data_load = f.read()
    test_module_dic = json.loads(data_load)
    return __succeedResponse(test_module_dic)


@require_http_methods(['GET'])
def getTestData(request):
    db = request.GET.get('db')
    collection = request.GET.get('collection')
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    draw = int(request.GET.get('draw'))
    sort_val = request.GET.get('sort')

    if sort_val is None:
        sort_val = "start_time"

    try:
        starttime = request.GET.get('starttime')
        endtime = request.GET.get('endtime')
    except:
        print("starttime and endtime is empty")

    query_filter = {}
    try:
        sessionid = request.GET.get('filter')
        if sessionid is not None:
            query_filter = {"sessionid": sessionid}
    except Exception as e:
        print("filter is none")
    # dic = {}
    # if starttime is not None:
    #     dic["$gte"] = int(starttime)
    # if endtime is not None:
    #     dic["$lte"] = int(endtime)
    #
    # time_dic = {}
    # if len(dic) > 0:
    #     time_dic["start_time"] = dic

    default_sort = sort_val
    mongo_handler = Mongo_Handler(mongo_ip, mongo_port, db, collection)
    dic = mongo_handler.page_query(query_filer=query_filter, start=start, length=length, sort=default_sort)
    dic['draw'] = draw
    return __succeedResponse(dic)


@require_http_methods(['GET'])
def getDevices(request):
    remote = RemoteClient("192.168.123.240", 22, "coconutqa", "coconutstudio")
    stdin, stdout, stderr = remote.ssh_client.exec_command(f"adb devices")
    # out = stdout.read()
    # print(out)
    # stdin, stdout, stderr = remote.ssh_client.exec_command(f"~/Documents/resource/platform-tools/adb -s 192.168.211.16 shell getprop ro.product.model")
    out = stdout.readline()
    deviceList = []
    while out != "\n":
        loc = out.find("\tdevice")
        if loc != -1:
            loc = out.find(":")
            deviceList.append(out[:loc])
        out = stdout.readline()
    deviceInfo = []
    for device in deviceList:
        deviceDic = {}
        deviceDic["udid"] = device
        stdin, stdout, stderr = remote.ssh_client.exec_command(f"~/Documents/resource/platform-tools/adb -s {device} shell getprop ro.product.model")
        deviceDic["model"] = stdout.readline().replace("\n", "").replace("\r", "")
        stdin, stdout, stderr = remote.ssh_client.exec_command(f"~/Documents/resource/platform-tools/adb -s {device} shell getprop ro.product.brand")
        deviceDic["brand"] = stdout.readline().replace("\n", "").replace("\r", "")
        deviceDic["type"] = "Android"
        deviceInfo.append(deviceDic)
    dic = {}
    dic["data"] = deviceInfo

    remote.closeConnection()
    return __succeedResponse(dic)


@require_http_methods(['GET'])
def insertData(request):
    temp_dic, db, collection = load_params(request.GET)
    temp_dic['state'] = int(temp_dic['state'])
    temp_dic['start_time'] = float(temp_dic['start_time'])
    mongo_handler = Mongo_Handler(mongo_ip, mongo_port, db, collection)
    result = mongo_handler.insert_one_data(temp_dic)
    dic = {"ret": result}
    return __succeedResponse(dic)


@require_http_methods(['POST'])
def updateData(request):
    temp_dic, db, collection, key = load_params(request.GET)
    temp_dic['state'] = int(temp_dic['state'])
    # temp_dic['start_time'] = float(temp_dic['start_time'])
    temp_dic['end_time'] = float(temp_dic['end_time'])
    # temp_dic['test_result'] = True if temp_dic['test_result'] == 'True' else False
    temp_dic['test_result'] = json.loads(temp_dic['test_result'])
    mongo_handler = Mongo_Handler(mongo_ip, mongo_port, db, collection)
    result = mongo_handler.update_one_data(key, temp_dic)
    dic = {"ret": result}
    return __succeedResponse(dic)


@require_http_methods(['GET'])
def startTest(request):
    remote = RemoteClient("192.168.184.172", 22, "zt-2012497", "123")
    test_name = request.GET.get('testname')
    device = request.GET.get('device')
    device_type = request.GET.get('devicetype')
    test_plan = request.GET.get('testplan')
    # test_plan = ','.join(test_plan_data)
    perf_test = request.GET.get('perftest')
    stdin, stdout, stderr = remote.ssh_client.exec_command(
        f"export LANG='zh_CN.UTF-8'; cd ~/Documents/airtest/AirtestEngine; /Library/Frameworks/Python.framework/Versions/3.6/bin/python3 main.py --testname {test_name} --device {device} --devicetype {device_type} --testplan {test_plan} --performanceTest {perf_test} &>log.txt")
    # stdin, stdout, stderr = remote.ssh_client.exec_command(
    #     f"export LANG='zh_CN.UTF-8'; locale")
    # err = stderr.read().decode('utf-8')
    # out = stdout.read().decode('utf-8')
    # print(std, flush=True)
    dic = {"ret": "success"}
    remote.closeConnection()
    return __succeedResponse(dic)


@require_http_methods(['POST'])
def uploadFile(request):
    file = request.FILES['file']
    if not file:
        return __errRespone('', '上传文件不能为空')
    file_path = os.path.join("/var/ftp/pub/apk", file.name)
    if "apk" not in file.name:
        return __errRespone('', "should choose an apk file")
    # file_path = os.path.join("F://temp", file.name)
    try:
        f = open(file_path, 'wb')
        for i in file.chunks():
            f.write(i)
        f.close()
        get_apk_info(file_path, file.name)
        return __succeedResponse({"ret": "succeed"})
    except Exception as e:
        return __errRespone('', e)


def get_apk_info(file_path, file_name):
    package_name = subprocess.getoutput(f"/opt/androidSdk/build-tools/31.0.0/aapt dump badging {file_path} "
                                        f"| grep package | awk '{{print $2}}'").split("=")[1].split("'")[1]
    activity_name = subprocess.getoutput(f"/opt/androidSdk/build-tools/31.0.0/aapt dump badging {file_path} "
                                        f"| grep activity | awk '{{print $2}}'").split("=")[1].split("'")[1]
    apk_name = subprocess.getoutput(f"/opt/androidSdk/build-tools/31.0.0/aapt dump badging {file_path} "
                                    f"| grep application-label-zh-CN").split(":")[1].split("'")[1]
    db = "autotest"
    collection = "apkinfo"
    temp_dic = {
        "apk_name": apk_name,
        "package_name": package_name,
        "activity_name": activity_name,
        "file_name": file_name,
        "time": round(time.time())
    }
    mongo_handler = Mongo_Handler("127.0.0.1", 27017, db, collection)
    result = mongo_handler.insert_one_data(temp_dic)
    dic = {"ret": result}



def load_params(queryDict):
    temp_dic = {}
    key = ""
    for element in queryDict:
        if element == "db":
            db = queryDict.get('db')
            continue
        if element == "collection":
            collection = queryDict.get('collection')
            continue
        if element == "key":
            key = queryDict.get('key')
            continue
        temp_dic[element] = queryDict.get(element)
    if key == "":
        return temp_dic, db, collection
    else:
        return temp_dic, db, collection, key


# handle response
def __succeedResponse(info, msg='succeed'):
    res = __response()
    res['status'] = 0
    res['data'] = info
    res['msg'] = msg
    return JsonResponse(res, safe=False)


def __errRespone(info, msg='failed'):
    res = __response()
    res['status'] = 1
    res['data'] = info
    res['msg'] = msg
    return JsonResponse(res, safe=False)


def __response():
    return {'status': '', 'data': '', 'msg': ''}


def log(request):
    params = parse_qs(request.environ['QUERY_STRING'])
    sessionid = params["sessionid"][0]
    data = get_data(sessionid)
    return render(request, 'log.html', {'data': data})


FTPPATH = "/var/ftp/pub/build_result"
def get_data(sessionid):
    datapath = os.path.join(FTPPATH, sessionid, "data.json")
    with open(datapath, 'r', encoding='utf-8') as f:
        data_load = f.read()
    data = json.loads(data_load)
    data = json.dumps(data)
    return data