import os
import subprocess

# 设置需要处理的年份
years = ['2023', '2022']

# 设置其他全局变量
# os.environ['NUM_RANGE'] = '30000'
# os.environ['MAX_RETRIES'] = '3'
# os.environ['MAX_THREADS'] = '20'
# os.environ['RETRY_INTERVAL'] = '0.1'
# os.environ['MAX_CONCURRENT_TASKS'] = '4'

for year in years:
    # 设置年份环境变量
    os.environ['YEAR'] = year

    # 运行程序
    subprocess.call(['python', '1_mcm_certificate_downloader.py'])
    subprocess.call(['python', '2_extract_info_from_downloaded_pdfs.py'])
