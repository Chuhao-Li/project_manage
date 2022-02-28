#!/usr/bin/env python3
import os
import re
import sys
import time
from datetime import datetime
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))

def parse_config():
    config_path = "/home/seyx/project/project_info.xls"
    config_dict = {}
    for line in open(config_path):
        # name, start, update, status, owner, description
        sline = line.rstrip('\n').split('\t')
        config_dict[sline[0]] = sline[1:]
    return config_dict

def save_config(config_dict):
    os.system("mv /home/seyx/project/project_info.xls /home/seyx/project/project_info.xls.backup")
    with open("/home/seyx/project/project_info.xls", 'w') as f:
        for k,v in config_dict.items():
            line = f"{k}\t" + "\t".join(v)
            print(line, file=f)

def update_config(args):
    '''
    用到args.name, args.owner, args.status, args.description几个参数。
    '''
    config_dict = parse_config()
    args.name = args.name.rstrip('/').split('/')[-1]
    name_version = args.name
    # 如果已有同一项目，那就打个新版本，然后获取旧项目中的owner、deseciption信息
    if args.name in config_dict:
        flag = input(f"项目{args.name}已存在，覆盖(0)/更新(1)/取消(2)？\n")
        if flag == "1":
            ok = False
            versions = [i for i in config_dict if i.startswith(args.name)]
            versions.sort()
            while not ok:
                print("已存在版本：")
                for i in versions:
                    print(i)
                tag = input("请输入新版本号：\n")
                if not f"{args.name}_{tag}" in versions:
                    ok = True
                else:
                    cover = input("版本已存在，是否覆盖？是(1)/否(2)。")
                    if cover == "1":
                        ok=True
                    print()
            name_version = f"{args.name}_{tag}"
            last_version = sorted(versions)[-1]
            # name: [start, update, status, owner, description]
            owner = config_dict[last_version][3]
            description = config_dict[last_version][4]
        elif flag == "0":
            owner = args.owner if args.owner else input("请输入项目所有者，用逗号分隔：\n")
            description = args.description if args.description else input("请输入项目描述：\n")
        else:
            exit()
    # 如果是新项目，那么owner, description都要重新输入。
    else: 
        owner = args.owner if args.owner else input("请输入项目所有者，用逗号分隔：\n")
        description = args.description if args.description else input("请输入项目描述：\n")
    status = args.status if args.status else input("请输入项目状态completed(1)/uncomplete(2)：\n")
    status = "completed" if status == "1" else "uncomplete"
    start = re.search(r'^\d{4}-\d{2}-\d{2}', args.name).group()
    end = datetime.now().strftime('%Y-%m-%d')
    config_dict[name_version] = [start, end, status, owner, description]
    save_config(config_dict)
    return name_version

def get_this():
    cwd = os.getcwd()
    if cwd.startswith(project_path + '/'):
        r = cwd.replace(project_path+ '/', '').split('/')[0]
    else:
        print('不在项目目录中，无法使用this！')
        exit()
    return r

def get_project_path(name):
    if (not name) or name == "this":
        name = get_this()
        path = f"{project_path}/{name}"
    elif name.startswith("/"):
        path = os.path.abspath(name)
    else:
        path = f"{project_path}/{name}"
    return path

def publish(args):
    dir1 = get_project_path(args.name)
    args.name = dir1
    name_version = update_config(args)
    # args.name = args.name.rstrip('/')
    # dir1 = f"{project_path}/{args.name}"
    if not os.path.exists(dir1):
        print("project {args.name} not exist! ")
        exit()
    dir1_r = f"{dir1}/report"
    dir2 = f"/home/seyx/project/{name_version}"
    # 删除之前的文件
    if os.path.exists(dir2):
        flag = input(f"{dir2} 已存在，是否删除？(Y/n)\n")
        if flag == "Y":
            os.system(f"rm -r {dir2}")
        else:
            exit()
    if os.path.exists(f"{dir2}.tar.gz"):
        os.system(f"rm {dir2}.tar.gz")
    # 拷贝新的文件
    os.system(f"cp -r {dir1_r} {dir2}")
    os.system(f"tar -zcvf {dir2}.tar.gz -C /home/seyx/project {name_version}")
    print("publish finished. ")

def create_step(step_name, prefix=None, input_f=""):
    '''
    构建新的步骤文件夹。根据已有的文件夹编号自动编码。
    '''
    steps = [i for i in os.listdir(prefix) if re.match(r"_\d\d\d", i)]
    if steps:
        step_names = [i[4:] for i in steps]
        step_codes = [int(i[1:4]) for i in steps]
        last_step_code = sorted(step_codes)[-1]
        this_step_code = str(last_step_code+1).zfill(3)
    else:
        this_step_code = "000"
        step_names = []
    coded_name = "_" + this_step_code + step_name
    if prefix:
        step_dir = prefix + '/' + coded_name
    else:
        step_dir = os.path.abspath(coded_name)
    if step_name in step_names:
        print(f"{step_name} already exists! ")
        return
    else:
        os.mkdir(step_dir)
    os.system(f"touch {step_dir}/log.sh")
    with open(f"{step_dir}/snk.txt", "w") as f:
        print(f"rule {coded_name}: ", file=f)
        print(f"    input: \n        '{input_f}'", file=f)
        print("    output: \n        ''", file=f)
        print(f"    shell: \n        'bash {coded_name}/log.sh'", file=f)
    os.system(f"touch {step_dir}/readme.md")
    print(f"create step {step_name} done. ")

def create(args):
    m = re.search(r'(?:\d{4}-\d{2}-\d{2}){0,1}\w+', args.name)
    if not m:
        sys.stderr.write(f"项目名含有非法字符！\n")
        exit(1)
    m = re.match(r'\d{4}-\d{2}-\d{2}', args.name)
    if not m:
        sys.stderr.write(f"项目名{args.name}没有指定日期，使用当前日期。\n")
        args.name = str(datetime.now().date()) + "_" + args.name
    path = f"{project_path}/{args.name}"
    if os.path.exists(path):
        sys.stderr.write(f"项目已存在！\n")
        exit(1)
    os.mkdir(path)
    os.mkdir(f"{path}/script")
    os.mkdir(f"{path}/doc")
    os.mkdir(f"{path}/subproject")
    create_step("first", prefix=path, input_f="script/target")
    with open(f"{path}/script/target", "w") as f:
        print("rule all: ", file=f)
        print("    input: ", file=f)
        print("        ''", file=f)
    os.system(f"cp {script_dir}/template/pipeline.snk.py {path}/script")
    os.system(f"cp {script_dir}/template/readme.template.md {path}/readme.md")
    os.system(f"cp {script_dir}/template/general/report_data.template.json {path}/doc/report_data.json")
    os.system(f"cp {script_dir}/template/general/report_content.template.html {path}/doc/report_content.html")
    print(f"项目{args.name}创建完毕!")

def show(args):
    '''
    显示最近的数据分析项目
    '''
    projects = [i for i in os.listdir(project_path) if re.match(r'\d{4}-\d{2}-\d{2}', i)]
    if args.keyword:
        projects = [i for i in projects if re.search(args.keyword, i, re.I)]
    projects.sort()
    for i in projects[-args.num:]:
        print(f"{project_path}/{i}")

def report(args):
    '''
    生成报告。
    内容：doc/report_content.html
    模板：提供可选的模板，主要是用于渲染图表。
    数据：doc/report_data.json，需要放到报告中的图表和数据，以及数据的描述。
    脚本：script/*，包括脚本和脚本相关的文档。以script/pipeline.snk.py为入口。
    之前使用的是generate_html.py来拷贝文件和渲染html；用break_snakemake.py来生成分析流程图页面。
    后面可能改用create_report.py。这个脚本是在generate_html.py的基础上经过优化的。
    doc/report_content.html中定义了各种标签以及标签的class name, 包括图、表、数据等。这些标签是固定的，所以写的时候需要注意遵守该版本的规范。
    generate_html.py也是把内容插入到模板中固定的标签中。所以如果开发新的模板，需要使用相同的标签。主要是文章的body以及title。
    '''
    # render html
    # copy figures and tables
    path = get_project_path(args.name)
    proj_name = os.path.basename(path)
    doc = f"{path}/doc/report_content.html"
    if not os.path.exists(doc):
        sys.stderr.write(f"项目文档文件{doc}不存在！")
        exit(1)
    report_path = f"{path}/report"
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    # os.system(f"generate_html.py {path}/doc/report_content.html")
    os.system(f"{script_dir}/create_report.py -o {path}/report -r {path}/doc/report_content.html -s {path}/doc/report_data.json -t {script_dir}/template/general/index.html --title {proj_name}")

    # create pipeline html
    if args.script:
        os.system(f"{script_dir}/collect_script.py")
        if os.path.exists(f"{path}/report/script"):
            tmp = input(f"{path}/report/script 已存在，是否更新？是(1)/否(0)")
            if tmp == "1":
                os.system(f"rm -r {path}/report/script")
                os.system(f"cp -r {path}/script {path}/report/")
        else:
            os.system(f"cp -r {path}/script {path}/report/")
        print("生成pipeline.svg...")
        if not os.path.exists(f"report/figures"):
            os.makedirs("report/figures")
        os.system("snakemake -s script/pipeline.snk.py --dag |dot -Tsvg >report/figures/pipeline.svg")
        os.chdir(f"{path}/report")
        print("生成static/step_code...")
        os.system("break_snakemake.py script/pipeline.snk.py")
        os.system("cp /home/lch/Database/projects/pipeline.html ./")
    print("report done. ")

def new_step(args):
    create_step(args.name)


project_path = "/home/lch/Project"

parser = argparse.ArgumentParser()
parser.description = "manager my project"
subparsers = parser.add_subparsers(help='')
t1 = subparsers.add_parser('publish', help='publish report to seyx')
t1.add_argument('name', help='project name')
t1.add_argument('--description', help='project description')
t1.add_argument('--sub', action="store_true", help='publish subproject')
t1.add_argument('--status', help='project status, completed(1)/uncomplete(2)')
t1.add_argument('--owner', help='输入项目所有者，用逗号分隔')
t1.set_defaults(func=publish)

t2 = subparsers.add_parser('create', help='create project directory')
t2.add_argument('name', help='project name')
t2.add_argument('--sub', action="store_true", help='create subproject')
t2.set_defaults(func=create)

t3 = subparsers.add_parser('show', help='show recent projects')
t3.add_argument('-n', '--num', default=10, type=int, help='how many project to show')
t3.add_argument('-k', '--keyword', help='show projects with keyword')
t3.set_defaults(func=show)

#   --header HEADER       报告标题
#   -o OUTDIR, --outdir OUTDIR
#   -r REPORT, --report REPORT
#   -s SRC, --src SRC     标签信息.json
#   -t TEMPLATE, --template TEMPLATE
#   --sub 指定子项目
#   --script 同时发布分析流程，调用break_snakemake.py生成分析流程报告。应当把每个步骤的script（log.sh等）和文档搜集到script目录中。
#   --all_files 把每个步骤的输出文件都包含到报告中，而不仅仅是report_content.html中用到的文件。
#   --prequisite 把原始数据也打包到报告中。
t4 = subparsers.add_parser('report')
t4.add_argument('name', default="this", help='project name')
t4.add_argument('--sub', action="store_true", help='report subproject')
t4.add_argument('--script', action="store_true", help='also report script')
t4.set_defaults(func=report)

t5 = subparsers.add_parser('new_step', help='create new step')
t5.add_argument('name', help='step name')
t5.set_defaults(func=new_step)

args = parser.parse_args()
args.func(args)
