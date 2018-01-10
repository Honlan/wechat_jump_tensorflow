# -*- coding: utf-8 -*-

import numpy as np
import tensorflow as tf
import time
import os
from utils import label_map_util
from utils import visualization_utils as vis_util
import cv2

if tf.__version__ != '1.4.0':
    raise ImportError('Please upgrade your tensorflow installation to v1.4.0!')

# 模型配置
PATH_TO_CKPT = 'frozen_inference_graph_frcnn_inception_v2_coco.pb'
PATH_TO_LABELS = 'wechat_jump_label_map.pbtxt'
NUM_CLASSES = 7

# 加载模型
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        od_graph_def.ParseFromString(fid.read())
        tf.import_graph_def(od_graph_def, name='')

# 加载类别
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# 屏幕截图
def pull_screenshot(path):
    os.system('adb shell screencap -p /sdcard/%s' % path)
    os.system('adb pull /sdcard/%s .' % path)

# 读取图片
def read_image(path):
    image_np = cv2.imread(path)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

    WIDTH = image_np.shape[1]
    HEIGHT = image_np.shape[0]
    image_np_expanded = np.expand_dims(image_np, axis=0)

    return image_np, image_np_expanded, WIDTH, HEIGHT

# 获取物体识别结果
def get_positions(boxes, classes, scores, category_index):
    cp = [1, 1, 1, 1]
    tp = [1, 1, 1, 1]
    target_type = ''
    min_score_thresh = .5

    for i in range(boxes.shape[0]):
        if scores[i] > min_score_thresh:
            if boxes[i][0] < 0.3 or boxes[i][2] > 0.8:
                continue
            if category_index[classes[i]]['name'] == 'chess':
                cp = boxes[i]
            elif boxes[i][0] < tp[0]:
                tp = boxes[i]
                target_type = category_index[classes[i]]['name']

    return cp, tp, target_type

# 一些变量
loop = 1
alpha = 1800
chess_x = 0
target_x = 0
distance = 0
screenshot = 'screenshot.png'

# 根据x距离跳跃
def jump(distance, target_type, alpha, bx1, by1, bx2, by2):
    press_time = max(int(distance * alpha), 200)

    cmd = 'adb shell input swipe {} {} {} {} {}'.format(bx1, by1, bx2, by2, press_time)
    os.system(cmd)

    if target_type in ['waste', 'magic', 'shop', 'music']:
        print('=' * 10, target_type , '=' * 10)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        while True:
            pull_screenshot(screenshot)
            image_np, image_np_expanded, WIDTH, HEIGHT = read_image(screenshot)
            
            bx1 = WIDTH / 2 + int(np.random.rand() * 10 - 5)
            bx2 = WIDTH / 2 + int(np.random.rand() * 10 - 5)
            by1 = HEIGHT * 0.785 + int(np.random.rand() * 4 - 2)
            by2 = HEIGHT * 0.785 + int(np.random.rand() * 4 - 2)

            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections], 
                feed_dict={image_tensor: image_np_expanded})

            boxes = np.reshape(boxes, (-1, boxes.shape[-1]))
            scores = np.reshape(scores, (-1))
            classes = np.reshape(classes, (-1)).astype(np.int32)

            vis_util.visualize_boxes_and_labels_on_image_array(image_np, boxes, classes, scores, category_index, use_normalized_coordinates=True, line_thickness=8)
            cv2.imwrite('detection.png', cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

            # 计算棋子和目标块位置
            cp, tp, target_type = get_positions(boxes, classes, scores, category_index)
            chess_x = (cp[1] + cp[3]) / 2
            target_x = (tp[1] + tp[3]) / 2
            distance = np.abs(chess_x - target_x)

            # 跳！
            jump(distance, target_type, alpha, bx1, by1, bx2, by2)
            print(distance, target_type)

            # 等棋子落稳
            loop += 1
            time.sleep(np.random.rand() + 1)

            # 跳累了休息一会
            rest_jump = np.random.rand() * 50 + 50
            rest_time = np.random.rand() * 5 + 5
            if loop > rest_jump:
                loop = 1
                print('已经跳了 %d 下，休息 %d 秒' % (rest_jump, rest_time))
                time.sleep(rest_time)
