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
PATH_TO_CKPT = 'wechat_jump_inference_graph/frozen_inference_graph.pb'
PATH_TO_LABELS = 'retrain/wechat_jump_label_map.pbtxt'
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

# 数据增强
def data_augmentation(path):
    image_np = cv2.imread(path)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    WIDTH = image_np.shape[1]
    HEIGHT = image_np.shape[0]
    images = np.ones((9,) + image_np.shape) * 255.

    images[0, :int(0.95 * HEIGHT), :int(0.95 * WIDTH), :] = image_np[int(0.05 * HEIGHT):, int(0.05 * WIDTH):, :]
    images[1, :int(0.95 * HEIGHT), :, :] = image_np[int(0.05 * HEIGHT):, :, :]
    images[2, :int(0.95 * HEIGHT), int(0.05 * WIDTH):, :] = image_np[int(0.05 * HEIGHT):, :int(0.95 * WIDTH), :]

    images[3, :, :int(0.95 * WIDTH), :] = image_np[:, int(0.05 * WIDTH):, :]
    images[4, :, :, :] = image_np[:, :, :]
    images[5, :, int(0.05 * WIDTH):, :] = image_np[:, :int(0.95 * WIDTH), :]

    images[6, int(0.05 * HEIGHT):, :int(0.95 * WIDTH), :] = image_np[:int(0.95 * HEIGHT), int(0.05 * WIDTH):, :]
    images[7, int(0.05 * HEIGHT):, :, :] = image_np[:int(0.95 * HEIGHT), :, :]
    images[8, int(0.05 * HEIGHT):, int(0.05 * WIDTH):, :] = image_np[:int(0.95 * HEIGHT), :int(0.95 * WIDTH), :]

    return image_np, images, WIDTH, HEIGHT

# 还原平移
def process_boxes(boxes):
    for i in range(boxes.shape[1]):
        # ymin, xmin, ymax, xmax
        boxes[0, i, 0] += 0.05
        boxes[0, i, 1] += 0.05
        boxes[0, i, 2] += 0.05
        boxes[0, i, 3] += 0.05

        boxes[1, i, 0] += 0.05
        boxes[1, i, 2] += 0.05

        boxes[2, i, 0] += 0.05
        boxes[2, i, 1] -= 0.05
        boxes[2, i, 2] += 0.05
        boxes[2, i, 3] -= 0.05

        boxes[3, i, 1] += 0.05
        boxes[3, i, 3] += 0.05

        boxes[5, i, 1] -= 0.05
        boxes[5, i, 3] -= 0.05

        boxes[6, i, 0] -= 0.05
        boxes[6, i, 1] += 0.05
        boxes[6, i, 2] -= 0.05
        boxes[6, i, 3] += 0.05

        boxes[7, i, 0] -= 0.05
        boxes[7, i, 2] -= 0.05

        boxes[8, i, 0] -= 0.05
        boxes[8, i, 1] -= 0.05
        boxes[8, i, 2] -= 0.05
        boxes[8, i, 3] -= 0.05
    return boxes

# 获取物体识别结果
def get_positions(chess_x, boxes, classes, scores, category_index):
    cp = [1, chess_x, 1, chess_x]
    tp = [1, 1, 1, 1]
    target_type = ''
    min_score_thresh = .5
    count = 0

    for i in range(boxes.shape[0]):
        if scores[i] > min_score_thresh:
            if boxes[i][0] < 0.3 or boxes[i][2] > 0.8:
                continue
            count += 1
            if category_index[classes[i]]['name'] == 'chess':
                cp = boxes[i]
            elif boxes[i][0] < tp[0]:
                tp = boxes[i]
                target_type = category_index[classes[i]]['name']
    print(count)
    return cp, tp, target_type

loop = 1
alpha = 1800
chess_x = 0.311
chess_x_prev = 0
target_x = 0
distance = 0
WIDTH = 0
HEIGHT = 0
bx1, by1, bx2, by2 = 0, 0, 0, 0
screenshot = 'screenshot.png'

# 根据x距离跳跃
def jump(distance, target_type, alpha):
    press_time = max(int(distance * alpha), 200)

    cmd = 'adb shell input swipe {} {} {} {} {}'.format(bx1, by1, bx2, by2, press_time)
    os.system(cmd)

    if target_type in ['waste', 'magic', 'shop', 'music']:
        print('=' * 5, target_type , '=' * 5)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        while True:
            pull_screenshot(screenshot)
            image_np, images, WIDTH, HEIGHT = data_augmentation(screenshot)
            
            bx1 = WIDTH / 2
            bx2 = WIDTH / 2
            by1 = HEIGHT * 0.785
            by2 = HEIGHT * 0.785

            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections], 
                feed_dict={image_tensor: images})
            boxes = process_boxes(boxes)

            boxes = np.reshape(boxes, (-1, boxes.shape[-1]))
            scores = np.reshape(scores, (-1))
            classes = np.reshape(classes, (-1)).astype(np.int32)

            vis_util.visualize_boxes_and_labels_on_image_array(image_np, boxes, classes, scores, category_index, use_normalized_coordinates=True, line_thickness=8)
            cv2.imwrite('detection.png', cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

            cp, tp, target_type = get_positions(chess_x, boxes, classes, scores, category_index)
            chess_x = (cp[1] + cp[3]) / 2
            target_x = (tp[1] + tp[3]) / 2
            
            # if loop > 1:
                # alpha *= distance / np.abs(chess_x - chess_x_prev)

            distance = np.abs(chess_x - target_x)

            print(distance, target_type, alpha, chess_x, target_x)
            jump(distance, target_type, alpha)

            chess_x_prev = chess_x
            chess_x = target_x
            loop += 1

            time.sleep(1)
