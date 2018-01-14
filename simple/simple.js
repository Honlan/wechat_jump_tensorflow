console.show();

// 设备信息
var WIDTH = device.width, 
    HEIGHT = device.height, 
    TYPE = device.brand + ' ' + device.model;
log('设备信息：', TYPE, '\n分辨率：', WIDTH, '*', HEIGHT);

// 获取截图权限
if (!requestScreenCapture()) {
    toast('请求截图失败，程序结束');
    exit();
}

// 启动微信
launchApp('微信');

// 提示用户进入跳一跳页面
new java.lang.Thread(function() {
    packageName('com.stardust.scriptdroid').className('android.widget.EditText').setText('准备好后点击 确定');
}).start();
console.rawInput('进入微信跳一跳，点击 开始游戏\n点击 确定 开始自动游戏');

do {
    // 获取截图
    var img = captureScreen();

    // 触按位置
    var bx1 = parseInt(WIDTH / 2 + random(-10, 10)),
        bx2 = parseInt(WIDTH / 2 + random(-10, 10)),
        by1 = parseInt(HEIGHT * 0.785 + random(-4, 4)),
        by2 = parseInt(HEIGHT * 0.785 + random(-4, 4));

    // 棋子底部中心找色
    var CHESS_X, CHESS_Y;
    var linemax = 0;
    for (let r = parseInt(HEIGHT * 0.7); r > parseInt(HEIGHT * 0.5);) {
        var line = [];
        for (let c = parseInt(WIDTH * 0.15); c < parseInt(WIDTH * 0.85); c++) {
            var point = images.pixel(img, c, r);
            var red = colors.red(point),
                green = colors.green(point),
                blue = colors.blue(point);
            if (red >= 40 && red <= 70 && green >= 40 && green <= 60 && blue >= 70 && blue <= 105) {
                line.push(c);
            }
        }
        if (line.length > linemax) {
            linemax = line.length;
            CHESS_X = line[Math.floor(line.length / 2)];
            CHESS_Y = r;
        }
        else if (line.length < linemax) {
            break;
        }
        r -= 5;
    }
    log('棋子X坐标：', CHESS_X);

    // 目标块顶部中心X坐标
    var TARGET_X, TARGET_Y;
    for (let r = parseInt(HEIGHT * 0.3); r <= parseInt(HEIGHT * 0.5);) {
        var flag = false;
        for (let c = parseInt(WIDTH * 0.15); c < parseInt(WIDTH * 0.85); c++) {
            if (Math.abs(c - CHESS_X) <= linemax) {
                continue
            }
            var c0 = images.pixel(img, c, r);
            var c1 = images.pixel(img, c, r - 5);
            if (Math.abs(colors.red(c0) - colors.red(c1)) + Math.abs(colors.green(c0) - colors.green(c1)) + Math.abs(colors.blue(c0) - colors.blue(c1)) >= 30) {
                TARGET_X = c;
                TARGET_Y = r;
                flag = true;
                break;
            }
        }
        if (flag) {
            break;
        }
        r += 5;
    }
    // 寻找白点
    var whitepoint = images.findColor(img, '#f5f5f5', {
        region: [TARGET_X - 20, TARGET_Y, 40, 250],
        threshold: 2
    });
    if (whitepoint) {
        TARGET_X = whitepoint.x;
    }
    log('目标块X坐标：', TARGET_X);

    // 跳！
    swipe(bx1, by1, bx2, by2, Math.abs(CHESS_X - TARGET_X) / WIDTH * 1900);
    sleep(random(1500, 2000));
} while (true);