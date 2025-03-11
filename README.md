## 安装python、adb
自行安装

## 模拟器尺寸
1080x1920

## 安装依赖
```
pip install -r requirements.txt
```
## 编辑配置文件
config.ini将IP的值改为模拟器名，可用以下命令查看
```
adb devices
```
## 运行（5x5）
```
python keshimon55.py
```
## 运行（6x6）
```
python keshimon66.py
```
## 修改55、66.py代码里的最后一行,自行设置间隔
```
time.sleep(0.1)
```