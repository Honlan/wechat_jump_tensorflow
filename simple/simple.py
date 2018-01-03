# -*- coding: utf-8 -*-

import numpy as np
import cv2
import os
import time

# 屏幕截图
def pull_screenshot(path):
    os.system('adb shell screencap -p /sdcard/%s' % path)
    os.system('adb pull /sdcard/%s .' % path)

# 根据x距离跳跃
def jump(distance, alpha):
    press_time = max(int(distance * alpha), 200)

    cmd = 'adb shell input swipe {} {} {} {} {}'.format(bx1, by1, bx2, by2, press_time)
    os.system(cmd)

if not os.path.exists('backup'):
	os.mkdir('backup')

screenshot = 'screenshot.png'
alpha = 0
bx1, by1, bx2, by2 = 0, 0, 0, 0
chess_x = 0
target_x = 0

fix=1.6667
size_str = os.popen('adb shell wm size').read()
if size_str:
	m = re.search(r'(\d+)x(\d+)', size_str)
	if m:
		hxw = "{height}x{width}".format(height=m.group(2), width=m.group(1))
		if hxw == "960x540":
			fix = 3.16

while True:
	pull_screenshot(screenshot)
	image_np = cv2.imread(screenshot)
	image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
	gray = cv2.Canny(image_np, 20, 80)

	HEIGHT = image_np.shape[0]
	WIDTH = image_np.shape[1]

	bx1 = WIDTH / 2
	bx2 = WIDTH / 2
	by1 = HEIGHT * 0.785
	by2 = HEIGHT * 0.785
	alpha = WIDTH * fix

	# 获取棋子x坐标
	stat = {}
	longest = 0
	for i in range(int(HEIGHT * 0.4), int(HEIGHT * 0.6)):
		flag = False
		line = []
		for j in range(int(WIDTH * 0.2), int(WIDTH * 0.8)):
			if image_np[i, j, 0] > 40 and image_np[i, j, 0] < 70 and image_np[i, j, 1] > 40 and image_np[i, j, 1] < 70 and image_np[i, j, 2] > 60 and image_np[i, j, 2] < 110:
				flag = True
				gray[i, j] = 255
				if len(line) > 0 and j - line[-1] > 1:
					flag = False
					break
				else:
					line.append(j)
		if flag:
			stat[np.mean(line)] = stat.get(np.mean(line), 0) + 1
			if len(line) > longest:
				longest = len(line)
	stat = sorted(stat.items(), key=lambda x:x[1], reverse=True)
	chess_x = int(stat[0][0])

	# 获取目标x坐标
	for i in range(int(HEIGHT * 0.3), int(HEIGHT * 0.5)):
		flag = False
		for j in range(WIDTH):
			# 超过朋友时棋子上方的图案
			if np.abs(j - chess_x) < longest:
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
	# 备份检测图
	# cv2.imwrite('backup/%d.png' % int(time.time()), gray)

	print(chess_x, target_x)
	jump(float(np.abs(chess_x - target_x)) / WIDTH, alpha)

	# 等棋子落稳
	time.sleep(np.random.random() + 1)

