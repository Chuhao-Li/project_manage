#!/usr/bin/env python3
import os
import sys
import re

# 根据pipeline.snk.py，搜集所有脚本，生成有统一入口的、便于浏览的、层次分明的html文件。
# 储存在 static/step_code目录下。

usage = "break_snakemake.py script/pipeline.snk.py"

if len(sys.argv) == 1 or '-h' in sys.argv:
    print(usage)
    exit(1)

def collect_script(text, step_name, paths=set()):
    # 工作目录：已经复制好script的report目下。
    if step_name == "all":
        return paths
    if paths == set():
        p = f"script/{step_name}/log.sh"
        t = open(p).read()
        collect_script(t, step_name, set([p]))
    # 收集在script目录下的脚本
    this_paths = set(re.findall(r"script/\S+\.(?:py|r|sh)", text, re.M))
    # 收集在step目录下的脚本，这些脚本会存放在script/step_name/目录下
    this_paths2 = set(re.findall(r"script/{step_name}/\S+\.(?:py|r|sh)".format(step_name=step_name), text, re.M))
    new_paths = this_paths & this_paths2 - paths
    if new_paths:
        paths.update(new_paths)
        for i in new_paths:
            t = open(i).read()
            collect_script(t, step_name, paths=paths)
    return paths

# 要求snk文件的rules之间必须间隔1行。
snk_file = open(sys.argv[1]).read().split('\n\n')

# 要求已经存在static文件夹。
if not os.path.exists("static/step_code"):
    os.mkdir("static/step_code")
else:
    answer = input("static/step_code 目录已存在，要替代其下面所有文件吗？(Y/n)")
    if answer != "Y":
        exit()

# 对于每个步骤，生成对应步骤的html文件。
for block in snk_file:
    block = block.strip()
    if not block:
        continue
    rules = re.findall(r"^rule ", block, re.M) # 搜寻所有步骤
    assert len(rules) == 1, f"rule number in block not equal to 1! \n\n{block}"
    rule_name = re.search(r"^rule ([^:]+)", block, re.M).group(1) # 获取步骤名称。
    outfile = f"static/step_code/{rule_name}.html"
    # 生成步骤html。
    with open(outfile, 'w') as f:
        # 标题
        print(f'<h1 id="step_title">{rule_name}</h1><hr>', file=f)
        # 描述
        print("<h3>description</h3>", file=f)
        if os.path.exists(f'script/{rule_name}.desc'):
            print(open(f'script/{rule_name}.desc').read(), end="", file=f)
        # 步骤代码
        print("<h3>step code</h3>", file=f)
        print("<pre>", file=f)
        print('<code id="step_code" class="python">', file=f)
        print(block, file=f)
        print("</code></pre>", file=f)
        # 脚本代码选择
        print("<h3>相关脚本</h3>", file=f)
        print('<select id="scripts">', file=f) # pipeline.html中对该Id绑定了事件。选中时会在script_code中显示相关代码。
        script_paths = collect_script(block, rule_name, paths=set())
        print(f'<option value="">选择脚本({len(script_paths)}个可选)</option>', file=f)
        for i in script_paths:
            print(f'<option value="{i}">{i}</option>', file=f)
        print('<select/>\n<pre><code id="script_code"></code></pre></div>', file=f)

    
