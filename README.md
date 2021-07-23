# export_es_pdf

**将elasticsearch官网文档导出pdf**

> 运行环境：

1. `python 3.8`
2. 安装`wkhtmltopdf `下载地址： https://wkhtmltopdf.org/downloads.html

> 修改`main.py`中配置：

```python
#导出pdf文件保存目录
save_path='c:\\self\\code\\es_book\\out'

#wkhtmltopdf的安装路径
path_wkthmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'

```

> 运行

```shell
pip install -r requirements.txt
python main.py
```

