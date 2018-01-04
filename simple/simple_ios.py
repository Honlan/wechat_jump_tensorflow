# -*- coding: utf-8 -*-

# 已测试MacOS + IOS，要正确运行下面代码，请先配置：
# 使用开发者账号Xcode真机调试WDA（WebDriverAgent）
# 参考网址 https://testerhome.com/topics/7220
# 安装openatx/facebook-wda支持使用Python调用WDA
# 参考网址 https://github.com/openatx/facebook-wda

import numpy as np
import cv2
import time
import wda

# iPhone 6s 按压时间参数修正，其它型号iPhone请自行修改
fixtime = 2.255

c = wda.Client()
s = c.session()

screenshot = 'jump_ios.png'

# 屏幕截图
def pull_screenshot():
    c.screenshot(screenshot)

# 根据x距离跳跃
def jump(distance, alpha):
    press_time = max(int(distance * alpha), 200) / 1000.0
    print('press time: {}'.format(press_time))
    s.tap_hold(200, 200, press_time)

alpha = 0
bx1, by1, bx2, by2 = 0, 0, 0, 0
chess_x = 0
target_x = 0

while True:
	pull_screenshot()
	image_np = cv2.imread(screenshot)
	image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
	gray = cv2.Canny(image_np, 20, 80)

	HEIGHT = image_np.shape[0]
	WIDTH = image_np.shape[1]

	bx1 = WIDTH / 2
	bx2 = WIDTH / 2
	by1 = HEIGHT * 0.785
	by2 = HEIGHT * 0.785
	alpha = WIDTH * fixtime

	# 获取棋子x坐标
	linemax = []
	for i in range(int(HEIGHT * 0.4), int(HEIGHT * 0.6)):
		line = []
		for j in range(int(WIDTH * 0.15), int(WIDTH * 0.85)):
			if image_np[i, j, 0] > 40 and image_np[i, j, 0] < 70 and image_np[i, j, 1] > 40 and image_np[i, j, 1] < 70 and image_np[i, j, 2] > 60 and image_np[i, j, 2] < 110:
				gray[i, j] = 255
				if len(line) > 0 and j - line[-1] > 1:
					break
				else:
					line.append(j)

		if len(line) > 5 and len(line) > len(linemax):
			linemax = line

		if len(linemax) > 50 and len(line) == 0:
			break

	chess_x = int(np.mean(linemax))

	# 获取目标x坐标
	for i in range(int(HEIGHT * 0.3), int(HEIGHT * 0.5)):
		flag = False
		for j in range(WIDTH):
			# 超过朋友时棋子上方的图案
			if np.abs(j - chess_x) < len(linemax):
				continue
			if not gray[i, j] == 0:
				target_x = j
				flag = True
				break
		if flag:
			break

	# 修改检测图
	gray[:, chess_x] = 255
	gray[:, target_x] = 255
	# 保存检测图
	cv2.imwrite('backup/%d.png' % int(time.time()), gray)

	print(chess_x, target_x)
	jump(float(np.abs(chess_x - target_x)) / WIDTH, alpha)

	# 等棋子落稳
	time.sleep(np.random.random() + 1.4)
