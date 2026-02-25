from flask import Flask, request, jsonify
import serial
import time
import cv2
import requests
import threading

app = Flask(__name__)

# ============ 配置区 ============
SERIAL_PORT = "/dev/ttyUSB0"  # 根据实际修改
BAUD_RATE = 9600
YOUR_BACKEND_URL = “https://ratio-kaylie-severally.ngrok-free.dev/api/sensor"

# ============ 初始化 ============
ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
time.sleep(2)

cap = cv2.VideoCapture(0)

# ============ 功能函数 ============
def upload_sensor_data(temp, humi, soil):
    """上传传感器数据到你的后端"""
    data = {
        "temperature": temp,
        "humidity": humi,
        "soil_moisture": soil
    }
    try:
        headers = {'ngrok-skip-browser-warning': 'true'}
        response = requests.post(YOUR_BACKEND_URL, json=data, headers=headers, timeout=5)
        print(f"[UPLOAD] 状态码: {response.status_code}")
    except Exception as e:
        print("[UPLOAD] 上传失败:", e)

def read_and_upload_loop():
    """循环读取串口数据并上传"""
    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line:
                continue
                
            # 过滤掉 Arduino 的回复消息
            if line.startswith("PUMP_DONE"):
                print("[ARDUINO]", line)
                continue
                
            temp, humi, soil = line.split(",")
            temp = float(temp)
            humi = float(humi)
            soil = int(soil)
            print(f"[SENSOR] 温度:{temp}°C, 湿度:{humi}%, 土壤:{soil}")

            upload_sensor_data(temp, humi, soil)
        except Exception as e:
            print("[SERIAL] 读取错误:", e)
        time.sleep(1)

# ============ 浇水接口（你调他）============
@app.route("/api/water", methods=['POST'])
def water():
    """接收你的浇水指令，通过串口通知Arduino控制水泵"""
    try:
        data = request.get_json()
        seconds = data.get('seconds', 5)
        
        print(f"[WATER] 收到指令: 浇水 {seconds} 秒")
        
        # 通过串口发送指令给 Arduino
        cmd = f"PUMP:{seconds}\n"
        ser.write(cmd.encode())
        print(f"[SERIAL] 发送: {cmd.strip()}")
        
        # 等待 Arduino 回复（可选，可以立即返回成功）
        # 等待时间不超过 2 秒
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                resp = ser.readline().decode().strip()
                print(f"[SERIAL] 收到: {resp}")
                if resp == "PUMP_DONE":
                    break
            time.sleep(0.1)
        
        return jsonify({
            "success": True,
            "message": f"已发送浇水{seconds}秒指令给Arduino"
        })
        
    except Exception as e:
        print(f"[WATER] 错误: {e}")
        return jsonify({
            "success": False,
            "message": f"浇水失败: {str(e)}"
        }), 500

# ============ 拍照接口 ============
@app.route("/photo", methods=["GET", "POST"])
def photo():
    try:
        if not cap.isOpened():
            return jsonify({"status": "error", "message": "Camera not opened"})

        ret, frame = cap.read()
        if not ret:
            return jsonify({"status": "error", "message": "Failed to read frame"})
        
        save_path = "/tmp/photo.jpg"
        cv2.imwrite(save_path, frame)

        return jsonify({
            "status": "success", 
            "message": "Photo saved", 
            "file_path": save_path
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============ 传感器实时查询接口 ============
@app.route("/sensor")
def sensor():
    try:
        line = ser.readline().decode("utf-8").strip()
        t, h, s = line.split(",")
        return jsonify({
            "temperature": float(t),
            "humidity": float(h),
            "soil_moisture": int(s)
        })
    except:
        return jsonify({"error": "read error"}), 500

# ============ 主程序 ============
if __name__ == "__main__":
    # 启动传感器读取线程
    threading.Thread(target=read_and_upload_loop, daemon=True).start()
    print("[INFO] 传感器读取线程已启动")
    
    print("[INFO] Flask服务启动在端口8080")
    app.run(host="0.0.0.0", port=8080, debug=False)