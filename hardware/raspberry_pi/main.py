from flask import Flask, request, jsonify
import serial
import time
import cv2
import requests
import threading
app = Flask(__name__)
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
YOUR_BACKEND_URL = "https://ratio-kaylie-severally.ngrok-free.dev/api/sensor"
ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
time.sleep(2)
cap = cv2.VideoCapture(0)
def upload_sensor_data(temp, humi, soil):
    data = {
        "temperature": temp,
        "humidity": humi,
        "soil_moisture": soil
    }
    try:
        headers = {'ngrok-skip-browser-warning': 'true'}
        response = requests.post(YOUR_BACKEND_URL, json=data, headers=headers, timeout=5)
        print(f"[UPLOAD] : {response.status_code}")
    except Exception as e:
        print("[UPLOAD] failed:", e)
def read_and_upload_loop():
    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("PUMP_DONE"):
                print("[ARDUINO]", line)
                continue
            temp, humi, soil = line.split(",")
            temp = float(temp)
            humi = float(humi)
            soil = int(soil)
            print(f"[SENSOR] temperature:{temp}C, humidity:{humi}%, soil:{soil}")
            upload_sensor_data(temp, humi, soil)
        except Exception as e:
            print("[SERIAL] failed:", e)
        time.sleep(1)
@app.route("/api/water", methods=['POST'])
def water():
    try:
        data = request.get_json()
        seconds = data.get('seconds', 5)
        print(f"[WATER] get: watering for {seconds} seconds")
        cmd = f"PUMP:{seconds}\n"
        ser.write(cmd.encode())
        print(f"[SERIAL] send: {cmd.strip()}")
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                resp = ser.readline().decode().strip()
                print(f"[SERIAL] roger: {resp}")
                if resp == "PUMP_DONE":
                    break
            time.sleep(0.1)
        return jsonify({
            "success": True,
            "message": f"watering for {seconds} seconds to Arduino"
        })
    except Exception as e:
        print(f"[WATER] failed: {e}")
        return jsonify({
            "success": False,
            "message": f"failed: {str(e)}"
        }), 500
@app.route("/photo", methods=["GET"])
def photo():
    cap = None
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            return jsonify({"error": "Camera not opened"}), 500
        ret, frame = cap.read()
        if not ret:
            ret, frame = cap.read()
        if not ret:
            return jsonify({"error": "Failed to read frame"}), 500
        save_path = "/tmp/photo.jpg"
        cv2.imwrite(save_path, frame)
        return send_file(save_path, mimetype='image/jpeg')  
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cap is not None:
            cap.release()
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
if __name__ == "__main__":
    threading.Thread(target=read_and_upload_loop, daemon=True).start()
    print("[INFO] on ")
    
    print("[INFO] Flask is on 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
from flask import Flask, request, jsonify
import serial
import time
import cv2
import requests
import threading
app = Flask(__name__)
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
YOUR_BACKEND_URL = "https://ratio-kaylie-severally.ngrok-free.dev/api/sensor"
ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
time.sleep(2)
cap = cv2.VideoCapture(0)
def upload_sensor_data(temp, humi, soil):
    data = {
        "temperature": temp,
        "humidity": humi,
        "soil_moisture": soil
    }
    try:
        headers = {'ngrok-skip-browser-warning': 'true'}
        response = requests.post(YOUR_BACKEND_URL, json=data, headers=headers, timeout=5)
        print(f"[UPLOAD] : {response.status_code}")
    except Exception as e:
        print("[UPLOAD] failed:", e)
def read_and_upload_loop():
    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("PUMP_DONE"):
                print("[ARDUINO]", line)
                continue
            temp, humi, soil = line.split(",")
            temp = float(temp)
            humi = float(humi)
            soil = int(soil)
            print(f"[SENSOR] temperature:{temp}C, humidity:{humi}%, soil:{soil}")
            upload_sensor_data(temp, humi, soil)
        except Exception as e:
            print("[SERIAL] failed:", e)
        time.sleep(1)
@app.route("/api/water", methods=['POST'])
def water():
    try:
        data = request.get_json()
        seconds = data.get('seconds', 5)
        print(f"[WATER] get: watering for {seconds} seconds")
        cmd = f"PUMP:{seconds}\n"
        ser.write(cmd.encode())
        print(f"[SERIAL] send: {cmd.strip()}")
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                resp = ser.readline().decode().strip()
                print(f"[SERIAL] roger: {resp}")
                if resp == "PUMP_DONE":
                    break
            time.sleep(0.1)
        return jsonify({
            "success": True,
            "message": f"watering for {seconds} seconds to Arduino"
        })
    except Exception as e:
        print(f"[WATER] failed: {e}")
        return jsonify({
            "success": False,
            "message": f"failed: {str(e)}"
        }), 500
@app.route("/photo", methods=["GET"])
def photo():
    cap = None
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            return jsonify({"error": "Camera not opened"}), 500
        ret, frame = cap.read()
        if not ret:
            ret, frame = cap.read()
        if not ret:
            return jsonify({"error": "Failed to read frame"}), 500
        save_path = "/tmp/photo.jpg"
        cv2.imwrite(save_path, frame)
        return send_file(save_path, mimetype='image/jpeg')  
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cap is not None:
            cap.release()
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
if __name__ == "__main__":
    threading.Thread(target=read_and_upload_loop, daemon=True).start()
    print("[INFO] on ")
    
    print("[INFO] Flask is on 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
