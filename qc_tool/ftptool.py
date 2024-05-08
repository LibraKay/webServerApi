from ftplib import FTP
import os


class FTPTool:
    def __init__(self, host, username, password):
        self.ftp = None
        self.ftp_connect(host, username, password)

    # connect ftp server
    def ftp_connect(self, host, username, password):
        self.ftp = FTP()
        try:
            self.ftp.connect(host, 21)
        except Exception:
            raise RuntimeError(f"连接ftp服务器{host}失败")
        try:
            self.ftp.login(username, password)
        except Exception:
            raise RuntimeError(f"ftp服务器用户名密码错误")

    # download file from ftp server
    def download_file(self, remote_path, local_path):
        bufsize = 1024
        fp = open(local_path, 'wb')
        self.ftp.retrbinary('RETR ' + remote_path, fp.write, bufsize)
        self.ftp.set_debuglevel(0)
        fp.close()

    # upload file to ftp server
    def upload_file(self, remote_path, local_path):
        bufsize = 1024
        fp = open(local_path, 'rb')
        self.ftp.storbinary('STOR ' + remote_path, fp, bufsize)
        self.ftp.set_debuglevel(0)
        fp.close()

    # check ftp folder whether exist
    # remote_path 最后不能添加\ or /
    def initial_ftp_folder(self, remote_path_folder):
        try:
            pathres = os.path.split(remote_path_folder)
            path_folder = pathres[0]
            temp = self.ftp.nlst(path_folder)
            if remote_path_folder not in temp:
                self.ftp.mkd(remote_path_folder)
            else:
                raise RuntimeError("ftp服务器remote路径已经存在")
        except Exception as e:
            raise RuntimeError(f"ftp服务器创建文件夹失败: {e}")

    # ftp 服务器为linux
    def upload_folder(self, remote_path_folder, local_path_folder):
        '''
        TODO 上传文件夹
        '''
        for item in os.listdir(local_path_folder):
            item_remote_path = remote_path_folder + '/' + item
            print("remote_path: " + item_remote_path)
            item_local_path = os.path.join(local_path_folder, item)
            print("local_path: " + item_local_path)
            self.upload_file(item_remote_path, item_local_path)


    def download_folder(self, remote_path_folder, local_path_folder):
        '''
        TODO 下载文件夹
        '''


if __name__ == '__main__':
    try:
        ftp_agent = FTPTool('192.168.189.92', 'anonymous', 'DIn4ro3jmENO')
        root_dir = 'qiuqiu1/script'
        test_num = ''
        remote_path_folder = os.path.join(root_dir, test_num)
        local_path_folder = 'E:\\QC\\QiuqiuAirtest\\script'
        # ftp_agent.initial_ftp_folder(remote_path_folder)
        ftp_agent.upload_folder(remote_path_folder, local_path_folder)
    except RuntimeError as e:
        print(e)

