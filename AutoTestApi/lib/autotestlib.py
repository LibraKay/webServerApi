import re
import subprocess
import time
from threading import Thread
from AutoTestApi.lib.responselib import *
from AutoTestApi.lib.loggerlib import *

device_json = os.path.join(info_path, "devices.json")
test_engine_fpath = '/root/coconutstudio/AutoTestEngine/autotestengine/main.py'
test_engine_log_dir = '/root/coconutstudio/AutoTestEngine/autotestengine/logs'
temps = '/root/coconutqa/temps'
# test_engine_fpath = r"E:\Work_Kay\AutotestEngine\main.py"
# test_engine_log_dir = r"E:\Work_Kay\AutotestEngine\logs"
# temps = r"E:\Work_Kay"


def all_devices_install_apk(devices, apk, apkname):
    th_alldevices = []
    d_failed = []
    for device in devices:
        ls_device = [device, True]
        thread = Thread(target=single_device_install_apk, args=(ls_device, apk, apkname))
        thread.start()
        th_alldevices.append((ls_device, thread))
    for tu_thread in th_alldevices:
        tu_thread[1].join()
        logger.info(f'{tu_thread[0][0]} install finished, result:{tu_thread[0][1]}')
        if not tu_thread[0][1]:
            d_failed.append(tu_thread[0][0])
    return d_failed


def single_device_install_apk(ls_device, apk, apkname):
    def install_apk(ls_device, apk):
        install = subprocess.Popen(
            f'adb -s {ls_device[0]} install {apk}',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        while True:
            if install.poll() is None:
                time.sleep(3)
            else:
                logger.info(f"{ls_device[0]} apk install finished")
                break
        ls_device[1] = False if install.stdout.read().splitlines()[1] != "Success" else True
        install.communicate()

    check_apk = subprocess.Popen(
        f'adb -s {ls_device[0]} shell pm list packages {apkname}',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    time.sleep(1)
    if check_apk.stdout.read():
        logger.warn(f"{ls_device[0]}'s already installed {apkname}!uninstall first")
        check_apk.communicate()
        uninstall = subprocess.Popen(
            f'adb -s {ls_device[0]} uninstall {apkname}',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        uninstall.communicate()
        install_apk(ls_device, apk)
    else:
        check_apk.communicate()
        install_apk(ls_device, apk)


def GetDevicesList(device):
    devices = []
    all_devices = GetAllDevices()

    def dic_models_list(allmodels):
        dic = {}
        for m in allmodels:
            dic[m["model"]] = m['udid']
        return dic

    if not device:
        logger.error('运行设备为空！')
        raise ValueError('运行设备为空！')
    for brand in device:
        if brand not in all_devices:
            logger.error('设备库中没有该品牌设备！')
            raise ValueError("设备库中没有该品牌设备！")
        models_list = dic_models_list(all_devices[brand])
        for model in device[brand]:
            if model in models_list:
                devices.append(models_list[model])
                logger.info(f'brand:{brand},model:{model},device:{models_list[model]}')
            else:
                logger.warn(f'warn:model-{model} is not found in all devices!')
    return devices


def GetAllDevices():
    """
    获得所有的Devices，返回以Brand品牌名为Key，包含所有安卓设备的字典。例：
    {“HONOR”:[{"udid": “emulator-5554”,"model": "KNT-UL10",“using”: False/True,"type": "Android"},
            {"udid":"emulator-5556","model":""}],
    “OnePlus”:[{},{}],}
    """
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
        dic_single_device['is_busy'] = False

        if output_brand in all_brand_devices:
            all_brand_devices[output_brand].append(dic_single_device)
        else:
            all_brand_devices[output_brand] = [dic_single_device]

    json.dump(all_brand_devices, open(device_json, 'w'), indent=4)
    return all_brand_devices


def SetDevicesBusy(devices):
    """
    设置info/devices.json里对应的设备状态
    :return:
    """


def DealWithCaseLog(testname, testcase):
    """
    将testname-testcase-device的日志json化
    最终得到的格式：文件名testname_result.json，内容为
    "testcase1":[{"device":"device1", "test_case_id": "id1", "result": successs,
    "start_time": "1663581928.6617868", "end_time": "1663581936.129839"},
    {"device":"device2", "test_case_id": "id2", "result": failed,
    "start_time": "1663581928.6617868", "end_time": "1663581936.129839"},]
    "testcase2":[etc.]
    :param testname:
    :param testcase: example-"testcase1,testcase2"
    :return: path of json file
    """
    res_data = {}
    testcases = testcase.strip().split(',')
    for tc in testcases:
        res_data[tc] = []
        log = os.path.join(test_engine_log_dir, testname, tc, tc + "_log.txt")
        with open(log, 'r', encoding='utf-8') as l:
            content = l.read()
        tu_result_list = re.findall(r'result:(.+?);(.+?);(.+?);(.+?);(.+?);', content, re.M | re.I)
        for tu_result in tu_result_list:
            device_data = {'device': tu_result[0],
                           'test_case_id': tu_result[1],
                           'result': tu_result[2],
                           'start_time': tu_result[3],
                           'end_time': tu_result[4]}
            res_data[tc].append(device_data)
    result_json_file = os.path.join(info_path, testname + '_result.json')
    json.dump(res_data, open(result_json_file, 'w'), indent=4)
    return result_json_file, res_data


class AndroidTestVibe:
    def __init__(self, apkname=None, apkaddr=None, device=None, testcase=None, logdir=None, extra=None):
        self.apkname, self.apkaddr, self.device, self.testcase, self.logdir, self.extra \
            = apkname, apkaddr, GetDevicesList(device), testcase, logdir, extra
        self.all_installed = False

    def remove_failed_device(self, failed):
        self.device = [device for device in self.device not in failed]

    def set_installed(self):
        self.all_installed = False if self.all_installed else True
