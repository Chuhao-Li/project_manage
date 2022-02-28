#!/usr/bin/env python3

import os
import re

steps = [i for i in os.listdir("./") if re.match(r"_\d\d\d", i)]

steps.sort()

print("generating script/pipeline.snk.py...")
with open("script/pipeline.snk.py", "w") as f:
    # 打印目标文件
    for line in open("script/target"):
        print(line, end="", file=f)
    for i in steps:
        snk = open(f"{i}/snk.txt").read()
        print("", file=f)
        print(snk, file=f, end="")

print("collecting script of each step to the script folder...")
for i in steps:
    p = f"script/{i}"
    if not os.path.exists(p):
        os.mkdir(p)
    os.system(f"cp {i}/log.sh {p}")
    os.system(f"cp {i}/readme.md {p}")
    rscript = [i for i in os.listdir(i) if i.endswith(".r")]
    pyscript = [i for i in os.listdir(i) if i.endswith(".py")]
    for j in rscript + pyscript:
        os.system(f"cp {i}/{j} {p}")

template = '''
<h1 id="step_title">{title}</h1><hr>
<h3>description</h3>
{description}
<h3>step code</h3>
<pre>
<code id="step_code" class="python">
{step_code}
</code></pre>
<h3>相关脚本</h3>
<select id="scripts">
{options}
<select/>
<pre><code id="script_code">{entry}</code></pre></div>
'''

print("generating a html file for each step...")
script_dir = os.path.dirname(os.path.abspath(__file__))
os.system(f"cp {script_dir}/template/general/pipeline.html report")

if not os.path.exists("report/static/step_code"):
    os.makedirs("report/static/step_code")

# for rule all:
title = "all"
description = open(f"readme.md").read()
step_code = open(f"script/target").read()
n_options = 0
options = ""
entry = ""
output = template.format(title=title, description=description, step_code=step_code, n_options=n_options, options=options, entry="")
with open("report/static/step_code/all.html", "w") as f:
    print(output, file=f)

# for other rules: 
for i in steps:
    title = i
    description = open(f"{i}/readme.md").read()
    step_code = open(f"{i}/snk.txt").read()
    entry = open(f"{i}/log.sh").read()
    scripts = re.findall(r"{i}/\S+\.(?:r|sh|py)".format(i=i), entry)
    if scripts:
        for j in range(len(scripts)):
            p = scripts[j]
            if p.startswith(i):
                scripts[j] = f"script/{p}"
        scripts = set(scripts)
        n_options = len(scripts)
        options = [f'<option value="{j}">{j}</option>' for j in scripts]
        
        '<option value="script/{title}/log.sh">({n_options}个可选)</option>'
        options = "\n".join(options)
    else:
        n_options = 0
        options = ""
    options = f'<option value="script/{i}/log.sh">log.sh (还有{n_options}个可选)</option>' + options
    output = template.format(title=title, description=description, step_code=step_code, n_options=n_options, options=options, entry=entry)
    with open(f"report/static/step_code/{i}.html", "w") as f:
        print(output, file=f)
