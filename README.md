# 深度学习 - 微信跳一跳

### 2018.01.14更新

`simple`目录下增加了`simple.js`，思路同`simple.py`，使用`JavaScript`编写，在安卓上安装`Auto.js`之后运行该脚本即可，好处是直接在手机上运行，不需要连电脑

### 2018.01.05更新

标注数据增加到1200张图片，并且用更准的`faster_rcnn_inception_v2_coco`模型重新训练了一遍

### 项目介绍

知乎文章：[https://zhuanlan.zhihu.com/p/32553763](https://zhuanlan.zhihu.com/p/32553763)

感谢[Chao](https://github.com/loveu520)、[奋逗逗](https://github.com/liuzhenhui)对于标注数据做出的贡献

### 所需环境

- `Python3.6`、`OpenCV2`、`TensorFlow`等
- `adb`，用于调试安卓手机，参考[https://github.com/wangshub/wechat_jump_game](https://github.com/wangshub/wechat_jump_game)

### 文件介绍

`simple`目录中的`simple.py`使用`OpenCV2`检测棋子和目标块的位置，简单粗暴，`simple_ios.py`是对应的IOS版本

![simple检测结果](imgs/simple检测结果.gif)
 
`tensorflow`目录包括以下文件：

- `wechat_jump_label_map.pbtxt`：物体类别映射文件；
- `utils`：提供辅助功能的文件；
- `frozen_inference_graph_frcnn_inception_v2_coco.pb`：训练好的物体检测模型，共1200张标注数据，使用`faster_rcnn_inception_v2_coco`训练；
- `wechat_auto_jump.py`：自动跳一跳的代码

![物体检测结果](imgs/物体检测结果.gif)

`label.zip`提供了标注的工具，使用[labelImg](https://github.com/tzutalin/labelImg)进行物体检测标注，使用方法可以参考`物体检测标注说明.pdf`

![labelImg标注示例](imgs/标注示例.png)