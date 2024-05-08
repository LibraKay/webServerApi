import json
import os
import subprocess
import paramiko
from qc_tool.conftool import logger
from django.http import JsonResponse

build_path = r'/root/coconutstudio/AirTestEngine/airtestengine/build_result'
# build_path = r'F:\WorkSpace_Kay\Dev_Kay\airtestengine\build_result'


class AndroidAutoTestVibe:
    def __init__(self, apkname, apkaddr, brand, model, testcase, logdir, extra, start_time):
        self.apkname = apkname
        self.apkaddr = apkaddr
        self.brand = brand
        self.model = model
        self.testcase = testcase
        self.logdir = logdir
        self.extra = extra
        self.start_time = start_time
        self.is_installed = False
        self.is_runnig = False

    def set_install(self):
        self.is_installed = False if self.is_installed else True

    def set_running(self):
        self.is_runnig = False if self.is_runnig else True

    def get_device(self, brand, model):
        self.device = GetSpecificDevice(brand, model)


def GetDevicesList(models):
    devices = []

    all_devices = GetAllDevices()
    for brand in models:
        if brand not in all_devices:
            raise ValueError("设备库中没有该品牌设备！")
        models_list = dic_models_list(all_devices[brand])
        for model in models[brand]:
            if model in models_list["model"]:
                devices.append(models_list["udid"])
                logger.debug(f'model:{model}, device:{models_list["udid"]}')
            else:
                logger.warning(f'warn:model-{model} is not found in all devices!')
    return devices


def dic_models_list(models_list):
    dic = {}
    for m in models_list:
        dic[m["model"]] = m['udid']
    return dic


def stderr(code, rawcode, message):
    error = {
        "code": code,
        "rawcode": rawcode,
        "message": message
    }
    return error

def stdJsonResponse(result: bool, data = None, error = None):
    res = {"success": result,
           "data": data,
           "error": error}
    return JsonResponse(res)


"""
获得所有的Devices，返回以Brand品牌名为Key，包含所有安卓设备的字典。例：
{“HONOR”:[{"udid": “emulator-5554”,"model": "KNT-UL10",“using”: False/True,"type": "Android"},
        {"udid":"emulator-5556","model":""}],
“OnePlus”:[{},{}],}
"""
def GetAllDevices():
    devices = []
    all_brand_devices = {}
    output_devices = os.popen('adb devices').read().splitlines(False)
    # output_devices.pop()
    for line in output_devices[1:]:
        loc = line.find('\tdevice')
        if loc != -1:
            devices.append(line[:loc])
    for device in devices:
        dic_single_device = {}
        output_brand = os.popen(f'adb -s {device} shell getprop ro.product.brand').read().splitlines(False)[0]
        output_model = os.popen(f'adb -s {device} shell getprop ro.product.model').read().splitlines(False)[0]
        dic_single_device['udid'] = device
        dic_single_device['model'] = output_model

        if output_brand in all_brand_devices:
            all_brand_devices[output_brand].append(dic_single_device)
        else:
            all_brand_devices[output_brand] = [dic_single_device]

    device_json = os.path.join(build_path, "devices.json")
    json.dump(all_brand_devices, open(device_json, 'w'), indent=4)
    return all_brand_devices

"""
根据指定品牌和型号通过adb获得特定设备udid
"""
def GetSpecificDevice(brand, model):
    all_devices = GetAllDevices()
    if not brand in all_devices:
        raise ValueError("无此品牌设备")
    else:
        for device in all_devices[brand]:
            if device["model"] == model:
                return device["udid"]
        raise ValueError("无此型号设备")

def GetSessionIdInLine(line):
    loc = line.find('is created')
    if loc == -1:
        return ""
    else:
        # logger.info("找到了session_id:" + line[:loc].split('build_result')[1][1:])
        return line[:loc].split('build_result')[1][1:]

# def getStdoutSession(p, tstlg, session_id):
#     while True:
#         if p.poll() is None:
#             line = p.stdout.readline()
#             tstlg.write(line)
#             tstlg.flush()
#             if session_id == "":
#                 session_id = GetSessionIdInLine(line)
#         else:
#             tstlg.write("logging-end")
#             return

"""
调用执行脚本入口，并将输出流写入到日志
"""
def RunTestEngine(log, testname, device, testcase, tester):
    with open(log, 'w', encoding='utf-8') as tstlg:
        p = subprocess.Popen(
            fr'python F:\WorkSpace_Kay\Dev_Kay\airtestengine\main.py --testname {testname} --device {device} --devicetype "Android" --testplan {testcase} --performanceTest "False" --tester {tester}',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        tstlg.write("logging-start" + '\n')
        while True:
            if p.poll() is None:
                tstlg.write(p.stdout.readline())
                tstlg.flush()
                logger.info(p.stdout.readline())
                if test_session_id == "":
                    test_session_id = GetSessionIdInLine(p.stdout.readline())
            else:
                tstlg.write("logging-end")
                break