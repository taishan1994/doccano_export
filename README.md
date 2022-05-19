# doccano_export
使用doccano标注工具同时导出实体和关系数据为空的解决办法。标注平台地址：https://github.com/doccano/doccano

# 安装
其实安装挺简单的：
```shell
pip install doccano
# Initialize database.
doccano init
# Create a super user.
doccano createuser --username admin --password pass
# Start a web server.
doccano webserver --port 8000
```
然后再打开一个命令行：
```shell
doccano task
```
在浏览器打开127.0.0.1:8000，登陆后新建一个命名实体识别项目，勾选上关系抽取及多人合作。其它的一些标注方法这里就不展开了。

# 导出数据
找到db.sqlite3的位置，替换doccano_export.py里面的，然后替换project_id为自己的项目id。最后执行该文件。在同目录下会生成doccano_ext.json。
