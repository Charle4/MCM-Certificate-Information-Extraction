# 爬取美赛获奖证书, 以控制号命名, 以PDF的格式保存到'paper_年份'文件夹中. 

import os
import requests
from threading import Thread, BoundedSemaphore
from tqdm import tqdm
import time
from threading import Lock

# 全局参数
year = int(os.environ.get('YEAR', 2023)) # 竞赛年份
num_range = int(os.environ.get('NUM_RANGE', 30000)) # 证书编号范围
max_retries = int(os.environ.get('MAX_RETRIES', 3)) # 最大尝试下载次数
max_threads = int(os.environ.get('MAX_THREADS', 20)) # 最大线程数
retry_interval = float(os.environ.get('RETRY_INTERVAL', 0.1)) # 重试间隔时间

class MCMCertificateCrawler:
    """美赛证书爬取类"""
    def __init__(self, control_number: int, semaphore: BoundedSemaphore, downloaded_numbers: list, lock: Lock, pbar: tqdm):
        """
        MCMCertificateCrawler类的构造函数. 

        Args:
            control_number (int): 要下载的证书的控制编号. 
            semaphore (BoundedSemaphore): 用于限制同时运行的线程数量的信号量. 
            downloaded_numbers (list): 已经下载的证书的控制编号列表. 
            lock (Lock): 用于同步进度条更新的锁. 
            pbar (tqdm): 用于显示下载进度的进度条. 
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.103 Safari/537.36'
        }
        self.control_number = control_number
        self.semaphore = semaphore
        self.downloaded_numbers = downloaded_numbers
        self.lock = lock
        self.pbar = pbar

    def download_pdf(self):
        """
        下载指定编号的证书. 

        Returns:
            response (requests.Response): 请求的响应, 包含了证书的PDF文件的内容. 
        """
        url = f"http://www.comap-math.com/mcm/{year}Certs/{str(self.control_number)}.pdf"
        response = requests.get(url=url, headers=self.headers)
        return response

    def save_pdf(self):
        """
        保存指定编号的证书的PDF文件. 如果文件已经被下载, 或者文件不存在, 那么这个方法将不会做任何事情. 

        Returns:
            None.
        """
        self.semaphore.acquire()
        if self.control_number in self.downloaded_numbers:
            with self.lock:
                self.pbar.update()
            self.semaphore.release()
            return

        retries = 0
        while retries < max_retries:
            try:
                path = f"./paper_{year}/{str(self.control_number)}.pdf"
                response = self.download_pdf()
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    break  # 文件下载成功, 跳出循环
                elif response.status_code == 404:
                    break  # 404错误 (证书不存在), 直接跳出循环
                else:
                    retries += 1
                    time.sleep(retry_interval)
            except requests.exceptions.RequestException as e:
                print(f"Error at control_number {self.control_number}: {e}")
                retries += 1
                time.sleep(retry_interval)

        # 更新进度条
        with self.lock:
            self.pbar.update()
        self.semaphore.release()

def download(control_numbers: list):
    """
    下载并保存指定编号的证书. 

    Args:
        control_numbers (list): 要下载的证书的控制编号列表. 
    
    Returns:
        None.
    """
    semaphore = BoundedSemaphore(value=max_threads)
    threads = []

    lock = Lock()
    with tqdm(total=len(control_numbers), desc="Downloading") as pbar:
        for control_number in control_numbers:
            mcc = MCMCertificateCrawler(control_number, semaphore, downloaded_numbers, lock, pbar)
            t = Thread(target=mcc.save_pdf)
            t.start()
            threads.append(t)

        # 等待所有线程结束
        for t in threads:
            t.join()

        # 如果进度条没有完成, 手动完成它
        if not pbar.n == pbar.total:
            pbar.update(pbar.total - pbar.n)

def get_downloaded_numbers(dir: str) -> list:
    """
    从给定的目录中获取已经下载的证书的控制编号列表。
    
    Args:
        dir (str): 包含已经下载的证书的目录。

    Returns:
        downloaded_numbers (list): 已经下载的证书的控制编号列表。
    """
    downloaded_numbers = []
    download_filelist = os.listdir(dir)
    for filename in download_filelist:
        filenum = int(filename[:-4]) # 从文件名中提取证书编号
        downloaded_numbers.append(filenum)
    return downloaded_numbers

if __name__ == '__main__':
    # 构造控制编号列表
    all_control_list = [int(f"{year % 100}00000") + i for i in range(1, num_range)]

    # 确保证书保存的目录存在
    dir = f'./paper_{year}/'
    if not os.path.exists(dir):
        os.makedirs(dir)

    # 获取已下载的证书编号列表
    downloaded_numbers = get_downloaded_numbers(dir)

    # 下载证书
    download(all_control_list)
