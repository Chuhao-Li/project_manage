#!/usr/bin/env python3
import os
import sys
import json
from bs4 import BeautifulSoup

usage = "generate_html.py readme.md # 渲染图表标签，把图表、静态文件复制到report目录"
if len(sys.argv) == 1 or '-h' in sys.argv:
    print(usage)
    exit(0)

infile = os.path.abspath(sys.argv[1])
project_path = os.path.dirname(infile)
project_name = os.path.basename(project_path)

doc = BeautifulSoup(open(infile), "html.parser")

fig_doc_path = f"{project_path}/doc/figures.json"
if os.path.exists(fig_doc_path):
    fig_doc = json.load(open(fig_doc_path))
    figures = doc.find_all("div", "figure")
    for index, fig in enumerate(figures):
        index = index + 1
        Id = fig.attrs['id']
        fig_info = fig_doc[Id]
        content = f'<div class="fig_caption"><b>Figure.&nbsp;{index}&nbsp;{fig_info["caption"]}</b></div>' + \
                  f'<div class="fig_image"><img src="{fig_info["path"]}"></div>' + \
                  f'<div class="fig_description"><p><b>NOTE:&nbsp;</b>{fig_info["description"]}</p></div>' + \
                  f'<div align="right"><a href="static/template/{Id}.html" target="_blank" class="btn btn-outline-dark btn-sm mr-4">full size table</a></div>'
        content = BeautifulSoup(content, "html.parser")
        fig.append(content)
        # 获取class为fig_ref，且href属性为这张图的Id的a标签。把内容修改为Fig + index。

tab_doc_path = f"{project_path}/doc/tables.json"
if os.path.exists(tab_doc_path):
    tab_doc = json.load(open(tab_doc_path))
    tables = doc.find_all("div", "table")
    for index, tab in enumerate(tables):
        index = index + 1
        Id = tab.attrs['id']
        tab_info = tab_doc[Id]
        if tab_info['format'] == "csv":
            content = f'<div class="fig_caption"><b>Table.&nbsp;{index}&nbsp;{tab_info["caption"]}</b></div>'
            if 'collapse_tab' not in tab.attrs['class']:
                content += f'<table data-path="{tab_info["path"]}" class="display compact"></table>'
            content += f'<div class="fig_description"><p><b>NOTE:&nbsp;</b>{tab_info["description"]}</p></div>' + \
                       f'<div align="right"><a href="static/template/full_table.html?path={tab_info["path"]}" target="_blank" class="btn btn-outline-dark btn-sm mr-4">full size table</a>' + \
                       f'<a href="{tab_info["path"]}" class="btn btn-outline-dark btn-sm">download table</a></div>'
        elif tab_info['format'] == "picture":
            content = f'<div class="fig_caption"><b>Table.&nbsp;{index}&nbsp;{tab_info["caption"]}</b></div>' + \
                      f'<div class="fig_image"><img src="{tab_info["path"]}"></div>' + \
                      f'<div class="fig_description"><p><b>NOTE:&nbsp;</b>{tab_info["description"]}</p></div>'
        content = BeautifulSoup(content, "html.parser")
        tab.append(content)

data_doc_path = f"{project_path}/doc/data.json"
if os.path.exists(data_doc_path):
    data_doc = json.load(open(data_doc_path))
    data = doc.find_all("div", "supplement_data")
    for index, dat in enumerate(data):
        index = index + 1
        Id = dat.attrs['id']
        dat_info = data_doc[Id]
        content = f'<a href="{dat_info["path"]}">Supplementary file.&nbsp;{index}&nbsp;{dat_info["caption"]}</a>'
        content = BeautifulSoup(content, "html.parser")
        dat.append(content)

template = BeautifulSoup(open("/home/lch/Database/projects/index.html"), "html.parser")
template.find_all("h1", "card-title")[0].string = project_name
template.find_all("div", "article-body")[0].append(doc)

report_paths = [f"{project_path}/report", f"{project_path}/report/tables", f"{project_path}/report/figures", f"{project_path}/report/data"]
for i in report_paths:
    if not os.path.exists(i):
        os.mkdir(i)

# 写入index.html
with open(f'{project_path}/report/index.html', 'w') as f:
    print(template.prettify(), file=f)

# 复制静态文件到report
if not os.path.exists(f"{project_path}/report/static"):
    os.system(f"cp -r /home/lch/Database/projects/static {project_path}/report/")


# 复制图表和数据到report
if os.path.exists(fig_doc_path):
    for k,v in fig_doc.items():
        p2 = f'{project_path}/report/{v["path"]}'
        if "ori-path" in v:
            p1 =  f'{project_path}/{v["ori-path"]}'
            if (not os.path.exists(p2)) and os.path.exists(p1):
                command = f"cp {p1} {p2}"
                print(command)
                os.system(command)
        if not os.path.exists(p2):
            print(f"{p2}不存在，请检查。")
        else:
            with open(f"{project_path}/report/static/template/{k}.html", "w") as f:
                print('<html><head><meta charset="utf-8"></head><body>', file=f)
                print(f'<h1>{v["caption"]}</h1><hr><img src="../../{v["path"]}"/><p>{v["description"]}</p>', file=f)
                print('</body></html>', file=f)

if os.path.exists(tab_doc_path):
    for k,v in tab_doc.items():
        p2 = f'{project_path}/report/{v["path"]}'
        if "ori-path" in v:
            p1 =  f'{project_path}/{v["ori-path"]}'
            if (not os.path.exists(p2)) and os.path.exists(p1):
                command = f"cp {p1} {p2}"
                print(command)
                os.system(command)
        if not os.path.exists(p2):
            print(f"{p2}不存在，请检查。")

if os.path.exists(data_doc_path):
    for k,v in data_doc.items():
        p2 = os.path.abspath(f'{project_path}/report/{v["path"]}')
        if "ori-path" in v:
            p1 =  os.path.abspath(f'{project_path}/{v["ori-path"]}')
            if (not os.path.exists(p2)) and os.path.exists(p1):
                if v["format"] == "directory":
                    dirname = os.path.dirname(p1)
                    basename = os.path.basename(p1)
                    command = f"tar -zcvf {p2} -C {dirname} {basename}"
                else:
                    command = f"cp {p1} {p2}"
                print(command)
                os.system(command)
            if not os.path.exists(p2):
                print(f"{p2}不存在，请检查。")
                
