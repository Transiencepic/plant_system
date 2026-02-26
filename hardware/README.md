# 硬件模块说明

## 整体架构
- **树莓派**：运行主控程序 `raspberry_pi/ main.py `，负责与 Arduino 通信、上传数据到后端、提供拍照和浇水接口
- **Arduino**：运行 `arduino/plant_monitor.ino`，连接传感器并控制水泵

## 硬件清单
| 组件 | 型号/规格 | 数量 | 用途 |
|------|-----------|------|------|
| 树莓派 | 4B | 1 | 主控，运行通信服务 |
| Arduino | Uno| 1 | 连接传感器和执行器 |
| 温湿度传感器 | DHT11 | 1 | 测量空气温湿度 |
| 土壤湿度传感器 | 模拟量 | 1 | 测量土壤湿度 |
| 水泵 | 5V | 1 | 浇水执行器 |
| 继电器模块 | 5V | 1 | 控制水泵开关 |
| 摄像头 | USB或CSI | 1 | 拍摄植物照片 |

## 实物接线图
![接线图](raspberry_pi/2BACC472B0073E230DB73DB5B570B905.jpg)

## 通信协议
1. **Arduino → 树莓派**：每2秒发送一次传感器数据，格式 `温度,湿度,土壤值`
2. **树莓派 → Arduino**：浇水指令格式 `PUMP:秒数`

## 运行说明
### Arduino
1. 用 Arduino IDE 打开 `arduino/plant_monitor.ino`
2. 选择正确的开发板（ Arduino Uno）和端口
3. 上传代码

### 树莓派
1. 安装依赖：
```bash
pip install flask pyserial opencv-python requests
```
2.修改配置：
在 raspberry_pi/ main.py  中设置正确的串口号（如 /dev/ttyUSB0）
设置你的后端 ngrok 地址
3.运行
```bash
cd hardware/raspberry_pi
python  main.py 
```

### API接口（树莓派提供）
|接口|方法|说明|
|-----|-----|------|
|/api/water|POST|接收浇水指令，转发给 Arduino|
|/photo|GET|拍照并返回图片|
|/sensor|GET|实时读取传感器数据|
