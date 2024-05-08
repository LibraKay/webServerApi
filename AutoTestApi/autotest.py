import sys
import traceback
import paramiko
from shutil import copytree
from AutoTestApi.lib.autotestlib import *


def AutoCITest(request):
    """
    CI触发自动化集成接口
    :param request:HTTP request
    :return: stdJsonresponse
    """
    request_data = request.params['data']
    try:
        req_start_time = time.time()
        testname = time.strftime('%Y%m%d%H%M%S', time.localtime(req_start_time))
        testlog = os.path.join(info_path, testname + '_log.txt')
        logger.update_filehandler(testlog)
        logger.info(f'req_start_time:{time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(req_start_time))}')
        testvibe = AndroidTestVibe(request_data['apkname'], request_data['apkaddr'], request_data['device'], request_data['testcase'], request_data['logdir'], request_data['extra'])
        logger.info(f'testinfo--testname:{testname}, apkname:{testvibe.apkname}, apkaddr:{testvibe.apkaddr}, device:{request_data["device"]}, device_list:{testvibe.device}, testcase:{testvibe.testcase}, logdir:{testvibe.logdir}, extra:{testvibe.extra}')

        # get apk file via sftp
        #transport = paramiko.Transport((ip, port))
        #transport.connect(username='', password='')
        #sftp = paramiko.SFTPClient.from_transport(transport)
        temp_apk = os.path.join(temps, 'test.apk')
        #sftp.get(testvibe.apkaddr, temp_apk)
        logger.info("download apk:" + testvibe.apkaddr)

        # all devices install temp apk
        failed_devices = all_devices_install_apk(testvibe.device, temp_apk, testvibe.apkname)
        if failed_devices:
            logger.error(f'install failed device list:{failed_devices}')
            testvibe.remove_failed_device(failed_devices)
        os.remove(temp_apk)
        testvibe.set_installed()

        # running test engine
        logger.info(f'start running script')
        cmd = ['python3', test_engine_fpath, "--testname", testname, "--device", ','.join(testvibe.device),
               "--testcase", testvibe.testcase]
        # p = subprocess.Popen(cmd, shell=True,
        #                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

        result_json_file, res_data = DealWithCaseLog(testname, testvibe.testcase)
        logger.info(f'testname:{testname} result: {res_data}')
        #remote_file = os.path.join('CoconutCI/logs_AutoTest', testname + '_result.json')
        #sftp.put(result_json_file, remote_file)
        #transport.close()

        if testvibe.logdir:
            copytree(os.path.join(test_engine_log_dir, testname), os.path.join(testvibe.logdir, testname))

        req_end_time = time.time()
        logger.info(f'req_end_time:{time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(req_end_time))}')

        return stdJsonResponse(True, data=res_data)

    except ValueError as verr:
        logger.error(f'ValueError:{verr}')
        error = stderr(1, 0, verr)
        return stdJsonResponse(False, error=error)
    except:
        logger.error(f'unexpected error:{sys.exc_info()[0]}, traceback:{traceback.format_exc()}')
        error = stderr(2, 0, f'unexpected error:{sys.exc_info()[0]}, traceback:{traceback.format_exc()}')
        return stdJsonResponse(False, error=error)


Action2Handler = {
    'AutoCITest': AutoCITest,
}


def dispatcher(request):
    return dispatcherBase(request, Action2Handler)
