import cv2
import numpy as np
import os
import configparser
import time
from sklearn.cluster import KMeans

os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # 限制 CPU 线程数，防止报错

# 读取配置文件，获取 ADB 设备 IP
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
device_ip = config.get('emulator', 'IP')

filename = 'screenshot.png'

# 获取截图**
os.system(f"adb -s {device_ip} shell screencap -p /sdcard/{filename}")
os.system(f"adb -s {device_ip} pull /sdcard/{filename}")

# 读取截图**
img = cv2.imread(filename)
if img is None:
    print("未请检查 ADB 连接。")
    exit()

# 定义网格区域**
x1, y1 = 30, 565
x2, y2 = 1056, 1583

grid_width = 162   # 每个格子的宽度
grid_height = 162  # 每个格子的高度
gap = 8            # 网格之间的间隔

# 计算网格数量**
num_cols = (x2 - x1 + gap) // (grid_width + gap)
num_rows = (y2 - y1 + gap) // (grid_height + gap)

# 存储每个网格的特征**
features = []
grid_positions = []

# 提取每个网格的图像特征**
for i in range(num_cols):
    for j in range(num_rows):
        start_x = x1 + i * (grid_width + gap)
        start_y = y1 + j * (grid_height + gap)
        end_x = start_x + grid_width
        end_y = start_y + grid_height

        # 裁剪网格图像**
        grid_crop = img[start_y:end_y, start_x:end_x]

        # 计算颜色直方图特征**
        hist = cv2.calcHist([grid_crop], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        features.append(hist)
        grid_positions.append((start_x, start_y, end_x, end_y))

# 进行 KMeans 聚类**
num_clusters = min(len(features), 18)  # 限制类别最多 18 种
kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)
labels = kmeans.fit_predict(features)

print("结果:", labels)  # 调试输出

# 复制图像并绘制编号**
grid_img = img.copy()

# 颜色配置**
text_color = (0, 0, 0)  # 纯白色
outline_color = (255, 255, 255)     # 纯黑色描边
font_scale = 3                # 文字大小
thickness = 6                 # 文字厚度（白色）
outline_thickness = 10        # 黑色描边厚度

# 在网格内绘制编号**
click_positions = []

for idx, (start_x, start_y, end_x, end_y) in enumerate(grid_positions):
    label = labels[idx]
    
    # 计算中心点**
    center_x = (start_x + end_x) // 2
    center_y = (start_y + end_y) // 2
    click_positions.append((label, center_x, center_y))

    # 先绘制黑色描边**
    cv2.putText(grid_img, str(label), (center_x - 30, center_y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, outline_color, outline_thickness, cv2.LINE_AA)
    
    # 再绘制白色文字**
    cv2.putText(grid_img, str(label), (center_x - 30, center_y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness, cv2.LINE_AA)

    # 画网格框**
    cv2.rectangle(grid_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

# 保存并显示最终结果**
cv2.imwrite("grid_clustered.png", grid_img)
#os.system("grid_clustered.png")  # Windows 自动打开图片

# 按照编号排序（从小到大点击）**
click_positions.sort()

# 归类相同编号的点击点
click_dict = {}
for label, x, y in click_positions:
    if label not in click_dict:
        click_dict[label] = []
    click_dict[label].append((x, y))

# 逐个编号执行点击
for label, positions in sorted(click_dict.items()):
    tap_commands = " && ".join([f"adb -s {device_ip} shell input tap {x} {y}" for x, y in positions])
    
    print(f"点击编号 {label} 的所有坐标: {positions}")
    
    # 一次性执行多个点击
    os.system(tap_commands)
    time.sleep(0.1)  # 防止过快
