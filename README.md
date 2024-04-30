# 机器人对话功能模块
# 使用教程

### 启动对话服务
打开两个窗口，分别执行如下程序：

窗口1：
```
source ~/.bashrc
conda activate auto
rasa run --enable-api -m "rasa/models/nlu-20230605-081816-ancient-tributary.tar.gz"
```

窗口2：
### 
```
source ~/.bashrc
conda activate auto
python rasa/ser.py
```
