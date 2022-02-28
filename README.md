# 生物信息分析项目管理软件

# 软件功能和接口
项目目录生成
project_manage.py create -n project_name

项目分支, 子项目，探索性分析
project_manage.py create
--sub 指定子项目

实际分析：生成子目录、编写脚本、运行脚本、编写步骤说明。
project_manage.py new_step -n step_name

生成分析报告
project_manage.py report
  --header HEADER       报告标题
  -o OUTDIR, --outdir OUTDIR
  -r REPORT, --report REPORT
  -s SRC, --src SRC     标签信息.json
  -t TEMPLATE, --template TEMPLATE
  --sub 指定子项目
  --script 同时发布分析流程，调用break_snakemake.py生成分析流程报告。应当把每个步骤的script（log.sh等）和文档搜集到script目录中。
  --all_files 把每个步骤的输出文件都包含到报告中，而不仅仅是report_content.html中用到的文件。
  --prequisite 把原始数据也打包到报告中。

发布分析报告: 需要自动匹配报告系统中已有的项目，合并到里面去。
project_manage.py publish 
--sub 指定子项目

seyx更改项目显示方式：
同一个项目在顶层只显示1个。对于同一个项目的所有版本、子项目，都在点击之后呈现。
1. project_name
2. main/subproject/branch
3. version description
4. detail description
5. status

# 实际使用场景。
1. 写顶层readme.md和report_content.html文件。项目一开始，应当先写文字的计划。顶层readme.md主要写分析策略、项目进度和目录架构。report_content.html主要写背景、目的、分析结果、讨论等。由于顶层的readme.md需要嵌入到pipeline.html中，标题最好只保留2层，从h4开始。

2. 写顶层snakefile。然后写snakefile。大概的写，那些输入输出文件可能不太清楚，主要是定义步骤的名字以及步骤之间的依赖关系。后面参照这个来再写每个步骤的详细的snakefile。
然后执行snakefile中的步骤

3. 写步骤readme.md, snk.txt, log.sh。每一步操作，都应该在snakemake中登记。输入文件、输出文件、使用的脚本。这可以直接写到该步骤目录的snk.txt中，后面再合并到总的snakefile。
不在snakefile中写命令，任何简单的命令都写在步骤的log.sh中。
还应当把log.sh转化成容易阅读的readme.md，写清楚每个步骤的说明。这就是文章的材料与方法。
4. 每得到一个结果，就可以更新report_content.html和report_data.json文件。这就是文章的结果与分析部分。

5. 编译script目录。

6. 编译报告。所有步骤执行完成后，就可以生成报告并发布。

当项目需要更新时，所有改动的脚本、脚本说明、输出文件等都需要更新，这些基本都会改动原来的文件，因此，重新生成报告时，需要把原来的报告删除掉或者移动、备份到别的地方。

# 开发进度：
完善模板，测试当前脚本，看一下效果。
2022-02-28: readme.md需要转化为html。
