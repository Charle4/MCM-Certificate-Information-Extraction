# MCM Certificate Information Extraction

## 美赛证书爬取与信息提取

## 项目介绍

该项目使用 Python 脚本从美国大学生数学建模竞赛 (MCM) 的官方网站下载获奖证书, 并从下载的证书 PDF 文件中提取团队信息, 包括团队编号、团队成员姓名、指导老师姓名、学校名称以及获奖等级, 提取后的信息会保存到 CSV 文件中.

## 项目特点与优势

- **高效处理**: 利用多线程技术与并行文件处理策略, 实现快速的证书下载与信息提取.
- **稳定运行**: 引入重试机制与详尽的异常处理, 确保网络或文件问题不影响程序运行.
- **可配置性**: 提供灵活的参数配置, 满足不同需求和硬件条件.
- **用户友好**: 使用 `tqdm` 库动态展示任务进度, 直观了解任务完成情况.
- **代码优化**: 采用模块化设计, 使代码更清晰、易于维护和扩展.

## 安装依赖项

项目需要 Python 3.6 或更高版本, 使用了以下 Python 第三方库: `requests`, `tqdm`, `PIL`, `pytesseract`, `pdf2image`:

```bash
pip install requests tqdm pillow pytesseract pdf2image
```

安装 `pytesseract` 和 `pdf2image` 库之前, 需要先安装 [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) 和 [Poppler](https://poppler.freedesktop.org/).

#### 安装 Tesseract OCR

Tesseract 是一个 OCR 引擎, 用来从 PDF 文件中提取文本.

- **Ubuntu/Debian**

```bash
sudo apt-get install tesseract-ocr
```

- **MacOS** (使用 Homebrew)

```bash
brew install tesseract
```

- **Windows**

访问 [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载.

安装完成后, 请确保`tesseract`命令在系统的PATH中.

#### 安装 Poppler

Poppler 是一个 PDF 渲染库, 用来将 PDF 文件转换为图像.

- **Ubuntu/Debian**

```bash
sudo apt-get install poppler-utils
```

- **MacOS** (使用 Homebrew)

```bash
brew install poppler
```

- **Windows**

可以[在这里](https://github.com/oschwartz10612/poppler-windows/releases/)下载预构建的二进制文件.

安装完成后, 请确保`pdfimages`和`pdfinfo`命令在系统的 PATH 中.

## 快速开始

1. 安装所有必要的 Python 库和系统依赖项.

2. 设置 `0_run_mcm_programs.py` 中的年份列表为你想要处理的年份.

3. 运行  `0_run_mcm_programs.py`, 这个脚本将为列表中的每个年份运行 `1_mcm_certificate_downloader.py` 和 `2_extract_info_from_downloaded_pdfs.py`:

   ```bash
   python 0_run_mcm_programs.py
   ```

4. 对于每个年份, `1_mcm_certificate_downloader.py` 将下载该年份的所有获奖证书 PDF 文件, 下载的文件将保存在 `paper_{year}` 的文件夹中, 其中 `{year}` 是当前处理的年份.

5. 对于每个年份, `2_extract_info_from_downloaded_pdfs.py` 将从下载的 PDF 文件中提取信息, 提取的信息将保存在 `certificates_{year}.csv` 的 CSV 文件中, 其中 `{year}` 是当前处理的年份.

6. 查看 CSV 文件, 表头为: control_number, student1, student2, student3, advisor, university, prize.

运行时间参考:
![](https://raw.githubusercontent.com/Charle4/Image-Hosting-Service/main/picgo/202305121934478.png)

## 程序介绍

### 0_run_mcm_programs.py

这个脚本用于运行 `1_mcm_certificate_downloader.py` 和 `2_extract_info_from_downloaded_pdfs.py` 来处理多年的数据.

- `years`: 需要处理的年份列表. 将这个列表设置为你想要处理的年份.

### 1_mcm_certificate_downloader.py

这个脚本用于从 MCM 官方网站下载指定年份的所有获奖证书 PDF 文件.

- `year`: 竞赛年份. 通过环境变量 `YEAR` 设置.
- `num_range`: 证书编号范围. 默认为 30000, 这常足够覆盖所有证书编号. 
- `max_retries`: 最大尝试下载次数. 默认为 3, 如果网络连接不稳定, 你可以当增加这个值.
- `max_threads`: 最大线程数. 默认为 20, 这个值越大, 下载速度越快, 但是也会对你的网络接和系统资源造成更大的压力. 请根据你的网络连接和系统性能来调整这个值.
- `retry_interval`: 重试间隔时间. 默认为 0.1 秒, 如果你的网络连接不稳定, 你可以适当增加这个值.

### 2_extract_info_from_downloaded_pdfs.py

这个脚本用于从下载的 PDF 文件中提取信息, 并将提取的信息保存到 CSV 文件中. 

- `year`: 竞赛年份. 通过环境变量 `YEAR` 设置.
- `MAX_CONCURRENT_TASKS`: 最大并发任务数量. 默认为 4, 这个值越大, 信息提取的速度越快, 但是也会对你的系统资源造成更大的压力. 请根据你的系统性能来调整这个值.
