# 深度学习 - 微信跳一跳

### 所需环境

- `Python`和`TensorFlow`
- `adb`，参考[https://github.com/wangshub/wechat_jump_game](https://github.com/wangshub/wechat_jump_game)

### 文件介绍

`simple`目录下的`simple.py`使用`OpenCV`检测棋子和目标块的位置
 
`tensorflow`目录下包括以下文件：

- `retrain`：其中包含了模型的配置文件，以及物体类别映射文件；
- `utils`：提供辅助功能的文件；
- `wechat_jump_inference_graph`：训练好的模型；
- `wechat_auto_jump.py`：直接运行即可