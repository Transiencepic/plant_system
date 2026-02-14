# tools/watering.py
import requests
import json
from config import HARDWARE_CONFIG

def execute_watering(seconds):
    """
    向硬件设备发送浇水指令。
    参数: seconds (int) - 浇水持续时间，单位秒。
    返回: (success: bool, message: str)
    """
    # 1. 从配置中读取硬件地址
    url = HARDWARE_CONFIG.get("water_device_url")
    if not url:
        return False, "配置错误：未找到浇水设备地址（water_device_url）"

    # 2. 准备请求（严格遵循你定义的格式）
    payload = {"seconds": int(seconds)}  # 确保是整数
    headers = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'   # ✅ 就是这里！
    }

    # 3. 发送请求并处理响应
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # 判断是否成功（HTTP状态码为2xx）
        if 200 <= response.status_code < 300:
            return True, f"浇水指令发送成功。设备响应：{response.text}"
        else:
            return False, f"设备响应异常，状态码：{response.status_code}， 详情：{response.text}"
            
    except requests.exceptions.Timeout:
        return False, "连接硬件设备超时，请检查设备是否在线。"
    except requests.exceptions.ConnectionError:
        return False, f"无法连接到硬件设备，请检查地址是否正确：{url}"
    except Exception as e:
        return False, f"发生未知错误：{str(e)}"