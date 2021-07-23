import re
import os
import shutil
import pdfkit


import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader, PdfFileMerger


host='https://www.elastic.co/guide/en/elasticsearch/reference/7.13/'


#导出pdf文件保存目录
save_path='c:\\self\\code\\es_book\\out'

#wkhtmltopdf的安装路径
path_wkthmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'


toc_list=list()
def load_main_toc():
    '''
    解析es目录页有哪些类别 一个类别将产生一个pdf

    :return:
    '''
    print('start load toc....')
    url=host+'index.html'
    r = requests.get(url)
    print('request toc....')
    html=bs_preprocess(r.text)
    soup=BeautifulSoup(html,features="html.parser")

    container=soup.select('ul.toc')

    index=0
    for c in container[0].children:
        #去掉首位和rest_api
        if index in[0,33]:
            index+=1
            continue

        title=c.select('span a')[0]
        li_list=c.select('ul li')

        items = list()
        i=1
        for li in li_list:
            sub_title=li.select('span a')[0]
            items.append({"index":i,"title":title_preprocess(sub_title.text),"url":host+sub_title.attrs['href']})
            i+=1


        chapter={"index":index,"title":title_preprocess(title.text),"url":host+title.attrs['href'],"items":items}
        toc_list.append(chapter)
        index+=1

    print('toc loaded....')


def gen_pdf():

    if   os.path.exists(save_path):
        shutil.rmtree(save_path)

    os.makedirs(save_path)

    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    for toc in toc_list:
        toc_index=toc.get("index")

        if toc_index==30:
            #rest_api 单独执行
            continue;
        current_path = "{0}".format(save_path)

        pdf_file = "{0}\\{2}_{1}.pdf".format(current_path,toc.get('title'),toc.get('index'))

        print('start gen pdf:',toc.get('title'))

        #获取每一类下所有的url 导出为pdf
        urls=[item.get("url") for item in toc.get('items')]
        urls.insert(0,toc.get("url"))

        """
        设置javascript-delay 不然会报错301 会导致程序运行变慢 如果有其他好方法麻烦告诉我
        rest_api 因为连接数太多 所以执行到这里一定报错 
        rest_api需要每一个url生成一个pdf 最后使用merge_pdf合并
        """
        options = {'enable-local-file-access': None,'javascript-delay':len(urls)*5000}

        pdfkit.from_url(urls, pdf_file, configuration=config,options=options)



def process_rest_pdf():

    rest_path="{0}\\rest_api".format(save_path)
    os.makedirs(rest_path)

    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    for toc in toc_list:
        toc_index=toc.get("index")

        if toc_index!=30:
            continue

        print('start gen pdf:', toc.get('title'))
        pdf_file = "{0}\\0_{1}.pdf".format(rest_path,toc.get('title'))
        pdfkit.from_url(toc.get('url'), pdf_file, configuration=config)


        for item in toc.get('items'):
            print('start gen pdf:', item.get('title'))
            pdf_file = "{0}\\{2}_{1}.pdf".format(rest_path, item.get('title'),item.get('index'))
            pdfkit.from_url(item.get('url'), pdf_file, configuration=config)







def merge_pdf(title):
    #合并指定目录下的pdf文件

    file_path = "{0}\\{1}".format(save_path, title)

    path = os.path.abspath(file_path)
    files=os.listdir(file_path)
    files.sort(key=lambda x: int(x.split('_')[0]))


    files_list = [path + '\\' + file for file in files]
    print('start merge...')
    merger = PdfFileMerger(strict=False)

    for filename in files_list:
        file = open(filename, 'rb')
        file_read = PdfFileReader(file)

        (path, name) = os.path.split(filename)

        (bookmark, extension) = os.path.splitext(name)
        bookmark = bookmark.split('_')[1]
        merger.append(file_read, bookmark, import_bookmarks=False)

        file.close()
    merger.write("{0}\\{1}.pdf".format(save_path, title))
    merger.close()
    print('merge done...')



def bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)  # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)  # convert newlines to spaces
    # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html)  # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html)  # remove whitespaces after closing tags
    return html

def title_preprocess(title):
    #title中的？和：去掉
    return re.sub('[\\?:]',"",title)


if __name__ == '__main__':

    load_main_toc()
    gen_pdf()

    process_rest_pdf()
    merge_pdf("rest_api")

    print('done....')