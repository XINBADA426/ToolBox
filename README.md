# ToolBox
This is the script I used for bioinfo analysis

## fq
Scripts to deal with fq/fq.gz files

### fqcombain.py
合并分批下机的原始数据

### fq_remove.py
利用过滤后的fq文件，提取原始fq文件中的reads


## fa
Scripts to deal with fa files

### ORFfinder.py
寻找最长转录本


## table
Scripts to deal with tables

### formattable.py
以较为美观的方式打印表格

### columntool.py
表格列名重命名
按照指定列名重排表格

### group_mean.py
计算各组均值


## igv
Scripts to use igv to plot pic


## one_gene_bam.py
使用基因序列及基因比对bam文件获取read在该基因的分布情况


## stat
Scripts to do stat analysis

### correlation_analysis.py
利用两个表达量表做相关性分析


## db
一些常用的处理数据库的脚本

### cazy
处理CAZy数据库的脚本

### phi
处理PHI数据库的脚本

### taxon
处理物种相关信息的脚本


## network
处理网络图的一些脚本
- `modify4gephisvg.py`：修饰gephi生成的svg图形
