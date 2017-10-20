from bs4 import BeautifulSoup
import urllib
import urllib.request
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

page_num=15


def get_paper_url(page_url):
    html = urllib.request.urlopen(page_url).read()
    soup = BeautifulSoup(html, 'html.parser')

    f = open('data-detail.txt', 'a+', encoding='utf-8')
    f.write("链接" + '\t' + "标题" + '\t' + "摘要" + '\t' + "关键词" + '\t' + "分类号" + '\t' +
            "出版物" + '\t' + "引用次数" + '\t' + "下载次数" + '\n')
    all = soup.find_all('div', class_='wz_content')
    for string in all:
        item = string.find('a', target='_blank')  # 文章标题与链接
        href = item.get('href')  # 获取文章url
        # 摘要
        abstract_html = urllib.request.urlopen(href).read()
        soup_detail = BeautifulSoup(abstract_html, "html.parser")
        abstract = soup_detail.find("div", class_="xx_font").get_text().replace("\r", '').replace("\n", '').\
            replace(" ", '').replace('\t', '')
        print(abstract)

        # 作者单位 + 关键词
        # 获取作者单位，处理字符串匹配
        authorUnitScope = soup_detail.find('div', style='text-align:left;', class_='xx_font')
        author_unit = ''
        author_unit_text = authorUnitScope.get_text().replace('\r\n', '')
        # print(author_unit_text)
        au = re.search(r"【学位授予单位】：(.*?)【学位级别】", author_unit_text)
        if au is None:
            author_unit = re.search(r"【作者单位】：(.*?)【关键词】", author_unit_text).group(1).strip()
        else:
            author_unit = au.group(1)

        # 关键词
        kw = re.search(r"【关键词】：(.*?)【", author_unit_text).group(1).strip()
        if kw is not None:
            keywords = kw
        else:
            keywords = ""
        print(kw)

        # 分类号
        cn = re.search(r"【分类号】：(.*?)【", author_unit_text).group(1).strip()
        if cn is not None:
            class_num = cn
        else:
            class_num = ""

        title = item.get_text()  # 获取文章标题
        year_count = string.find('span', class_='year-count')  # 获取文章出处与引用次数
        # year_count = year_count.get_text()
        publish = ''
        reference = ''
        for item in year_count:
            item = item.string
            item = item.replace('\n', '')
            item = item.replace('\r', '')
            if '被引次数' in item:
                reference = item  # 获取被引次数
                m = re.findall('（(.*?)）', reference)
                CiteNum = m[0].replace("（|）", "") if len(m[0]) >= 1 else 0
                DownloadNum = m[1].replace("（|）", "") if len(m[1]) >= 1 else 0

            elif '年' in item:  # 获取文章出处
                publish = item
        f.write(href + '\t' + title + '\t' + abstract + '\t' + keywords + '\t' + class_num + '\t' +
                publish + '\t' + str(CiteNum) +'\t'+str(DownloadNum) + '\n')
        print(href + '\t' + title + '\t' + publish + '\t' + str(CiteNum) +'\t'+str(DownloadNum) +'\n')
    f.close()
