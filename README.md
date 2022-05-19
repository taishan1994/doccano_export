# doccano_export
使用doccano标注工具同时导出实体和关系数据为空的解决办法。doccano版本：1.6.2。标注平台地址：https://github.com/doccano/doccano

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
找到db.sqlite3的位置，替换doccano_export.py里面的，然后替换project_id为自己的项目id。最后执行该文件。在同目录下会生成doccano_ext.json。就可以用于百度的UIE的微调任务了。
补充：windows用户db.sqlite3在C:\Users\用户名\doccano\，Linux用户在：/home/用户名/doccano/下。

# 使用UIE进行微调
地址：https://github.com/PaddlePaddle/PaddleNLP/tree/develop/model_zoo/uie
### 步骤
```python
python doccano.py --doccano_file ./data/doccano_ext.json --task_type "ext" --save_dir ./data --splits 0.1 0.9 0
python finetune.py --train_path "./data/train.txt" --dev_path "./data/dev.txt" --save_dir "./checkpoint" --learning_rate 1e-5 --batch_size 16 --max_seq_len 512 --num_epochs 100 --model "uie-base" --seed 1000 --logging_steps 10 --valid_steps 100 --device "cpu"
```
### 结果
```python
[2022-05-19 10:22:20,558] [    INFO] - We are using <class 'paddlenlp.transformers.ernie.tokenizer.ErnieTokenizer'> to load 'ernie-3.0-base-zh'.
[2022-05-19 10:22:20,559] [    INFO] - Already cached C:\Users\Administrator\.paddlenlp\models\ernie-3.0-base-zh\ernie_3.0_base_zh_vocab.txt
global step 10, epoch: 10, loss: 0.00012, speed: 0.01 step/s
global step 20, epoch: 20, loss: 0.00006, speed: 0.01 step/s
global step 30, epoch: 30, loss: 0.00004, speed: 0.01 step/s
global step 40, epoch: 40, loss: 0.00003, speed: 0.01 step/s
global step 50, epoch: 50, loss: 0.00003, speed: 0.01 step/s
global step 60, epoch: 60, loss: 0.00002, speed: 0.01 step/s
global step 70, epoch: 70, loss: 0.00002, speed: 0.01 step/s
global step 80, epoch: 80, loss: 0.00002, speed: 0.01 step/s
global step 90, epoch: 90, loss: 0.00002, speed: 0.01 step/s
global step 100, epoch: 100, loss: 0.00001, speed: 0.01 step/s
Evaluation precision: 0.95238, recall: 0.95238, F1: 0.95238
best F1 performence has been updated: 0.00000 --> 0.95238
```
### 评估
```python
python evaluate.py --model_path "./checkpoint/model_best" --test_path "./data/dev.txt"  --batch_size 16 --max_seq_len 512
```
### 结果
```python
Evaluation precision: 0.95238, recall: 0.95238, F1: 0.95238
```
### 预测
```python
from pprint import pprint
from paddlenlp import Taskflow

schema = ['出发地', '目的地', '费用', '时间']
# 设定抽取目标和定制化模型权重路径
my_ie = Taskflow("information_extraction", schema=schema, task_path='./checkpoint/model_best')
pprint(my_ie("城市内交通费7月5日金额114广州至佛山"))
```
