项目名称

项目背景

项目任务

项目计划

项目进度

目录结构：
```
doc/ # 项目文档
  figure.json # 图表信息
  report.html # 分析结果报告
ref/ # 相关文献资料
data/ # 运行项目所需数据
report/ # 项目最终报告。
subproject/ # 子项目
script/ # 脚本
  pipeline.snk.py # 流程文件
  step001/ # 运行某步骤相关脚本
    rule__001.sh # 该步骤的顶层脚本
    rule__001.md # 该步骤的文档
    script1.py # 该步骤的相关脚本
    script2.py # 该步骤的相关脚本
step001/ # 各步骤生成的数据。
  readme.md # 对应script/step001/rule__001.md
  log.sh # 对应对应script/step001/rule__001.sh
step002/ # 与step001类似
```
