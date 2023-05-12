# OCR识别证书内容并写入csv文件, 包含'control_number', 'student1', 'student2', 'student3', 'advisor', 'university'和'prize'信息.

import os
import csv
from PIL import Image
import pytesseract
import io
from pdf2image import convert_from_bytes
from tqdm import tqdm
import concurrent.futures
import threading
from functools import partial
import re
from typing import List, Tuple

# 设置全局变量
year = int(os.environ.get('YEAR', 2023)) # 请将这里的年份替换为你需要的年份
MAX_CONCURRENT_TASKS = int(os.environ.get('MAX_CONCURRENT_TASKS', 4)) # 设置最大并发任务数量, 请根据自己的电脑性能调整这个值, 这个量过大会导致程序卡死

# 创建一个信号量, 用于限制同时运行的任务数量
semaphore = threading.Semaphore(MAX_CONCURRENT_TASKS)

csv_lock = threading.Lock()

def pdf_to_image(pdf_file_path: str) -> Image:
    """
    将PDF文件转换为图像

    Args:
        pdf_file_path (str): PDF文件路径

    Returns:
        Image: 返回的PIL Image对象
    """
    with open(pdf_file_path, 'rb') as f:
        images = convert_from_bytes(f.read(), fmt='png')
    return images[0]

def ocr_extract(img: Image) -> str:
    """
    从图像中提取文本

    Args:
        img (Image): PIL Image对象

    Returns:
        str: 提取出的文本
    """
    text = pytesseract.image_to_string(img, lang='eng')
    return text

def preprocess_content(content: str) -> str:
    """
    预处理PDF内容, 删除空行

    Args:
        content (str): 需要处理的PDF内容

    Returns:
        str: 处理后的内容
    """
    content = re.sub(r'\n\s*\n', '\n', content)
    return content

def extract_info(pdf_content: str) -> Tuple[List[str], str, str, str]:
    """
    从PDF内容中提取信息

    Args:
        pdf_content (str): 需要处理的PDF内容, 这是一个字符串, 其中包含了从PDF中OCR提取出的所有文本. 
    
    Returns:
        students (List[str]): 一个列表, 其中包含了所有学生的名字. 每个名字都是一个字符串. 
        advisor (str): 指导老师的名字, 这是一个字符串. 
        university (str): 大学的名称, 这是一个字符串. 
        prize (str): 获得的奖项, 这是一个字符串. 
    """
    university_pattern = r'(?<=\nOf\n).*'
    team_pattern = r'(?<=Be It Known That The Team Of\n)([\s\S]*?)(?=\nOf)'
    prize_pattern = r'(?<=Was Designated As\n).*'

    university = re.search(university_pattern, pdf_content, re.I)  # 添加 re.I 参数
    university = university.group().strip() if university else ''
    team = re.search(team_pattern, pdf_content, re.I)  # 添加 re.I 参数
    team = [line for line in team.group().strip().split("\n") if "Advisor" not in line] if team else []
    advisor = team[-1] if team else ''  # 取最后一个名字为指导老师
    students = team[:-1] if team else []  # 取除了最后一个名字之外的所有名字为学生名字
    prize = re.search(prize_pattern, pdf_content, re.I)  # 添加 re.I 参数
    prize = prize.group().strip() if prize else ''

    return students, advisor, university, prize
    
def process_file(semaphore: threading.Semaphore, filename: str, directory: str, csvwriter: csv.writer, processed_files: set) -> None:
    """
    使用OCR技术从指定的PDF文件中提取信息, 并将提取的信息写入CSV文件. 

    Args:
        semaphore (threading.Semaphore): 用于限制同时运行的任务数量的信号量. 
        filename (str): 要处理的PDF文件的文件名. 
        directory (str): PDF文件所在的目录. 
        csvwriter (csv.writer): 用于写入CSV文件的CSV写入器. 
        processed_files (set): 已经处理过的文件的集合. 
    
    Returns:
        None.
    """
    control_number = filename[:-4]
    if control_number in processed_files:
        return

    try:
        with semaphore:
            img = pdf_to_image(os.path.join(directory, filename))
            pdf_content = ocr_extract(img)
            pdf_content = preprocess_content(pdf_content)
            students, advisor, university, prize = extract_info(pdf_content)

            # 确保学生列表有三个元素
            students += [''] * (3 - len(students))
            with csv_lock:
                csvwriter.writerow([control_number, students[0], students[1], students[2], advisor, university, prize])
    except Exception as e:
        print(f"Error processing file {filename}: {e}")

def extract_and_save_info(year: int) -> None:
    """
    从指定年份的PDF中提取信息并保存到CSV文件中

    Args:
        year (int): 需要处理的年份

    Returns:
        None.
    """
    directory = f'paper_{year}'
    filenames = os.listdir(directory)

    csv_filename = f'certificates_{year}.csv'
    processed_files = set()
    if os.path.isfile(csv_filename):
        with open(csv_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip the headers
            for row in reader:
                processed_files.add(row[0])

    with open(csv_filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if not processed_files:
            csvwriter.writerow(['control_number', 'student1', 'student2', 'student3', 'advisor', 'university', 'prize'])

        process_file_partial = partial(process_file, semaphore, directory=directory, csvwriter=csvwriter, processed_files=processed_files)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_file_partial, filename) for filename in filenames}
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(filenames), desc="Processing PDFs"):
                pass

if __name__ == '__main__':
    # 提取信息并保存到CSV文件中
    extract_and_save_info(year)
