"""
智能植物养护系统 - 后端主程序
作者：许隽玮、郑淇匀、周佳乐
日期：2026-02
"""

from flask import Flask, jsonify, request
import datetime
import json
import os
import random  # 用于生成模拟数据
from flask_cors import CORS

# 导入配置文件
from config import (
    SYSTEM_CONFIG,
    SERVER_CONFIG,
    DATA_CONFIG,
    HARDWARE_CONFIG,
    PLANT_CONFIG
)

# 初始化Flask应用
app = Flask(__name__)

CORS(app)  # 👈 允许所有跨域请求

# 从配置文件读取设置
CONFIG = {
    "port": SERVER_CONFIG["port"],
    "debug": SYSTEM_CONFIG["debug"],
    "data_file": DATA_CONFIG["data_file"],
    "log_file": DATA_CONFIG["log_file"]
}

# 确保数据目录存在
data_dir = os.path.dirname(CONFIG["data_file"])
if data_dir and not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 确保日志目录存在
log_dir = os.path.dirname(CONFIG["log_file"])
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# ============ 初始化数据函数 ============

def init_sensor_data():
    """初始化传感器数据"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "temperature": round(20 + random.random() * 10, 1),  # 20-30°C
        "humidity": round(40 + random.random() * 30, 1),     # 40-70%
        "soil_moisture": random.randint(300, 700),           # 300-700
        "light_level": random.randint(500, 1000),            # 500-1000 lux
        "last_update": current_time
    }

def load_sensor_data():
    """从文件加载传感器数据，如果不存在则初始化"""
    if os.path.exists(CONFIG["data_file"]):
        try:
            with open(CONFIG["data_file"], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            return init_sensor_data()
    else:
        return init_sensor_data()

def save_sensor_data(data):
    """保存传感器数据到文件"""
    try:
        with open(CONFIG["data_file"], 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

# ============ 全局状态 ============

# 传感器数据（从文件加载）
sensor_data = load_sensor_data()

# 系统状态
system_status = {
    "running": True,
    "mode": "manual",  # manual/auto
    "last_watered": None,
    "water_today": 0
}

# ============ API 路由 ============

@app.route('/')
def index():
    """首页"""
    return f'''
    <h1>🌱 智能植物养护系统</h1>
    <p>后端服务运行正常！</p>
    <hr>
    <h3>📡 API接口：</h3>
    <ul>
        <li><a href="/api/status">/api/status</a> - 系统状态</li>
        <li><a href="/api/data">/api/data</a> - 传感器数据</li>
        <li><a href="/api/history/real">/api/history/real</a> - 真实历史数据</li>
        <li><a href="/api/history">/api/history</a> - 历史数据</li>
        <li><a href="/api/config">/api/config</a> - 系统配置</li>
       <li><a href="/api/ai/advice">/api/ai/advice</a> - 🌱 智能浇水建议</li>
        <li>POST /api/water - 控制浇水（手动模式）</li>
        <li>POST /api/mode - 切换系统模式（手动/自动）</li>
        <li>POST /api/sensor - 接收硬件传感器数据</li>
        <li>POST /api/camera/take - 控制拍照（树莓派）</li>
    </ul>
    <hr>
    <p>📍 项目位置：{os.path.abspath('.')}</p>
    <p>🕒 启动时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p>💾 数据文件：{CONFIG['data_file']}</p>
    <p>🔧 当前模式：{system_status['mode']}</p>
    <p>💧 今日已浇水：{system_status['water_today']} 秒</p>
    '''

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    from db_client import get_last_seen
    import datetime
    
    last_seen = get_last_seen()
    hardware_status = "waiting"
    
    if last_seen:
        time_diff = (datetime.datetime.now(datetime.timezone.utc) - last_seen).total_seconds()
        if time_diff < 300:  # 5分钟内
            hardware_status = "online"
        else:
            hardware_status = "offline"
    
    return jsonify({
        "system": "智能植物养护系统",
        "status": "running" if system_status["running"] else "stopped",
        "mode": system_status["mode"],
        "uptime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hardware": hardware_status,  # ✅ 现在会变
        "version": "1.0.0",
        "water_today": system_status["water_today"],
        "last_watered": system_status["last_watered"]
    })

@app.route('/api/data')
def get_data():
    """获取最新的传感器数据（优先从数据库读取）"""
    try:
        # 1. 首先尝试从数据库获取真实数据
        from db_client import query_latest_data
        real_data = query_latest_data()
        
        # 2. 判断是否获取到有效数据
        if real_data and 'temperature' in real_data:
            # 成功从数据库获取到数据，组织返回格式
            sensor_data = {
                "temperature": real_data.get("temperature", 0.0),
                "humidity": real_data.get("humidity", 0.0),
                "soil_moisture": real_data.get("moisture", 0),  # 注意字段名映射
                "light_level": 800,  # 先给一个固定值，因为数据库可能没有这个字段
                "source": "hardware",
                "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            note = "实时数据"
        else:
            # 数据库没有数据，降级到模拟数据
            print("数据库无有效数据，使用模拟数据")
            sensor_data = init_sensor_data()
            sensor_data["source"] = "simulated"
            note = "模拟数据（数据库无数据）"
        
        # 3. 如果依然是模拟数据，应用精细变化逻辑
        if sensor_data.get("source") == "simulated":
            # 温度：白天高晚上低，基于当前时间模拟
            hour = datetime.datetime.now().hour
            base_temp = 20 + hour * 0.3  # 早上20°C，下午升高
            sensor_data["temperature"] = round(base_temp + random.uniform(-2, 2), 1)
            
            # 湿度：随时间缓慢变化
            sensor_data["humidity"] = round(40 + random.uniform(0, 30), 1)
            
            # 土壤湿度：随时间缓慢下降（模拟水分蒸发）
            if "last_simulated" in sensor_data:
                last_time = datetime.datetime.fromisoformat(sensor_data["last_simulated"])
                time_diff = (datetime.datetime.now() - last_time).total_seconds()
                # 每10分钟下降1-2点
                sensor_data["soil_moisture"] -= int(time_diff / 600 * random.uniform(0.1, 0.2))
                sensor_data["soil_moisture"] = max(200, min(800, sensor_data["soil_moisture"]))
            
            sensor_data["last_simulated"] = datetime.datetime.now().isoformat()
        
        # 4. 准备API响应
        response = {
            "success": True,
            "timestamp": sensor_data["last_update"],
            "data": sensor_data,
            "source": sensor_data.get("source", "simulated"),
            "note": note
        }
            
        return jsonify(response)
        
    except Exception as e:
        # 如果发生任何异常（如数据库连接失败），优雅降级
        print(f"获取数据时出错，使用模拟数据降级: {e}")
        sensor_data = init_sensor_data()
        return jsonify({
            "success": True,
            "timestamp": sensor_data["last_update"],
            "data": sensor_data,
            "source": "simulated",
            "note": f"数据库暂时不可用，使用模拟数据。错误: {e}"
        })

@app.route('/api/water', methods=['POST'])
def water():
    """控制浇水"""
    # 检查系统是否运行
    if not system_status["running"]:
        return jsonify({"error": "系统已停止"}), 400
    
    # 检查是否手动模式
    if system_status["mode"] != "manual":
        return jsonify({"error": "当前为自动模式，请切换到手动模式后再操作"}), 400
    
    # 获取请求参数，使用配置中的默认值
    try:
        data = request.get_json()
        seconds = data.get("seconds", PLANT_CONFIG["water_duration"])
    except:
        seconds = PLANT_CONFIG["water_duration"]
    
    # 检查浇水时长是否超过每日限制
    max_today = PLANT_CONFIG["max_water_per_day"]
    if system_status["water_today"] + seconds > max_today:
        return jsonify({
            "error": "超过每日浇水限制",
            "message": f"今日已浇水 {system_status['water_today']} 秒，最多可浇水 {max_today} 秒",
            "remaining": max_today - system_status["water_today"]
        }), 400
    
    # 记录浇水
    system_status["last_watered"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_status["water_today"] += seconds

    # ========== 【新增】调用真实硬件浇水控制 ==========
    try:
        from tools.watering import execute_watering
        hardware_success, hardware_message = execute_watering(seconds)
        # 根据硬件执行结果，决定是否更新本地模拟数据
        if hardware_success:
            # 硬件成功，正常更新土壤湿度模拟值
            sensor_data["soil_moisture"] = max(200, sensor_data["soil_moisture"] - 100)
            hw_note = "（硬件执行成功）"
        else:
            # 硬件失败，可以选择不更新模拟值，或更新较少值
            # sensor_data["soil_moisture"] = sensor_data["soil_moisture"]  # 保持不变
            hw_note = f"（硬件执行失败：{hardware_message}）"
            print(f"[浇水API警告] 硬件控制失败: {hardware_message}")
    except Exception as e:
        # 如果导入或调用工具函数本身出错
        hardware_success = False
        hardware_message = f"调用控制工具时出错: {str(e)}"
        hw_note = f"（系统错误：{hardware_message}）"
        print(f"[浇水API错误] {hardware_message}")
    # ========== 【新增结束】 ==========
    
    # 更新土壤湿度（浇水后上升） - 此处的修改已整合到上方逻辑中
    # 模拟浇水效果：浇水后土壤湿度增加，值越小表示越湿
    # 【原代码已整合，此行可注释或删除】sensor_data["soil_moisture"] = max(200, sensor_data["soil_moisture"] - 100)
    sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 保存数据
    save_sensor_data(sensor_data)
    
    return jsonify({
        "action": "watering",
        "duration": seconds,
        "time": system_status["last_watered"],
        "water_today": system_status["water_today"],
        "new_moisture": sensor_data["soil_moisture"],
        # ========== 【新增】硬件控制结果字段 ==========
        "hardware_success": hardware_success,
        "hardware_message": hardware_message,
        "note": hw_note,
        # ========== 【新增结束】 ==========
        "message": f"成功浇水 {seconds} 秒",
        "remaining_today": PLANT_CONFIG["max_water_per_day"] - system_status["water_today"]
    })

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """切换系统模式：手动/自动"""
    try:
        data = request.get_json()
        new_mode = data.get("mode", "manual")
        
        # 验证模式参数
        if new_mode not in ["manual", "auto"]:
            return jsonify({
                "error": "无效的模式",
                "message": "模式必须是 'manual' 或 'auto'"
            }), 400
        
        # 切换模式
        old_mode = system_status["mode"]
        system_status["mode"] = new_mode
        
        return jsonify({
            "success": True,
            "message": f"系统模式已从 {old_mode} 切换为 {new_mode}",
            "old_mode": old_mode,
            "new_mode": new_mode,
            "auto_config": {
                "water_threshold": PLANT_CONFIG["auto_water_threshold"],
                "water_duration": PLANT_CONFIG["water_duration"],
                "check_interval": PLANT_CONFIG["check_interval"]
            } if new_mode == "auto" else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    """接收硬件发送的传感器数据"""
    try:
        # 获取硬件发送的数据
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['temperature', 'humidity', 'soil_moisture']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": "数据格式错误",
                    "message": f"缺少必要字段: {field}",
                    "required_fields": required_fields
                }), 400
        
        # ========== 更新：写入真实数据库 ==========
        try:
            from db_client import write_sensor_data
            # 将接收到的数据写入InfluxDB
            write_success = write_sensor_data(
                temperature=float(data['temperature']),
                humidity=float(data['humidity']),
                soil_moisture=int(data['soil_moisture'])
            )
            
            if write_success:
                # 同时更新本地内存中的 sensor_data 对象，保持兼容性
                sensor_data.update(data)
                sensor_data["source"] = "hardware"
                sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[API] 硬件数据已成功写入数据库: {data}")
            else:
                # 如果数据库写入失败，可以在这里记录日志或采取其他措施
                print(f"[API] 警告：接收到的硬件数据未能写入数据库: {data}")
                # 我们仍然更新内存数据，但标记来源为模拟，表示不持久
                sensor_data.update(data)
                sensor_data["source"] = "simulated"
                sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception as db_error:
            # 如果数据库操作发生异常（如连接失败），捕获它避免影响API响应
            print(f"[API] 写入数据库时发生异常: {db_error}")
            sensor_data.update(data)
            sensor_data["source"] = "simulated"
            sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # ========== 替换结束 ==========
        
        # 如果是自动模式，检查是否需要浇水
        response = {"action": "none", "message": "数据接收成功"}
        if system_status["mode"] == "auto":
            threshold = PLANT_CONFIG["auto_water_threshold"]
            current_moisture = sensor_data["soil_moisture"]
            
            if current_moisture > threshold:  # 值越大表示越干
                # 检查是否超过每日浇水限制
                max_today = PLANT_CONFIG["max_water_per_day"]
                if system_status["water_today"] < max_today:
                    duration = PLANT_CONFIG["water_duration"]
                    response = {
                        "action": "water",
                        "duration": duration,
                        "reason": f"土壤湿度 {current_moisture} 高于阈值 {threshold}",
                        "message": "需要浇水"
                    }
        
        return jsonify({
            "success": True,
            "message": "传感器数据接收成功",
            "timestamp": sensor_data["last_update"],
            "mode": system_status["mode"],
            "command": response,
            "data_received": {
                "temperature": data.get("temperature"),
                "humidity": data.get("humidity"),
                "soil_moisture": data.get("soil_moisture")
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/real')
def get_real_history():
    """获取真实的数据库历史数据"""
    try:
        from db_client import query_history_data
        
        # 获取查询参数
        hours = request.args.get('hours', default=24, type=int)
        limit = request.args.get('limit', default=100, type=int)
        
        # 限制查询范围（保护数据库）
        hours = min(hours, 168)  # 最多查询7天
        limit = min(limit, 1000)  # 最多返回1000条
        
        # 查询数据库
        history = query_history_data(hours=hours, limit=limit)
        
        if history:
            return jsonify({
                "success": True,
                "source": "database",
                "period_hours": hours,
                "data_count": len(history),
                "data": history
            })
        else:
            # 数据库没有数据，返回模拟历史数据
            now = datetime.datetime.now()
            simulated_data = []
            
            for i in range(min(12, limit)):
                time_point = now - datetime.timedelta(hours=i)
                simulated_data.append({
                    "time": time_point.strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature": round(20 + random.random() * 10, 1),
                    "humidity": round(40 + random.random() * 30, 1),
                    "moisture": random.randint(300, 700)
                })
            
            # 按时间正序排列
            simulated_data.reverse()
            
            return jsonify({
                "success": True,
                "source": "simulated",
                "note": "数据库中没有历史数据，返回模拟数据",
                "period_hours": hours,
                "data_count": len(simulated_data),
                "data": simulated_data
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "error",
            "note": "获取历史数据时出错"
        }), 500

@app.route('/api/history')
def history():
    """历史数据接口（兼容旧版本，重定向到真实数据接口）"""
    return get_real_history()  # 直接调用新函数

@app.route('/api/config')
def get_config():
    """获取当前系统配置"""
    return jsonify({
        "system": SYSTEM_CONFIG,
        "server": SERVER_CONFIG,
        "data": DATA_CONFIG,
        "hardware": HARDWARE_CONFIG,
        "plant": PLANT_CONFIG,
        "current_mode": system_status["mode"],
        "current_data_file": CONFIG["data_file"]
    })

# ============ 拍照API ============
@app.route('/api/camera/take', methods=['POST'])
def take_picture():
    """拍照接口 - 返回可直接访问的图片URL"""
    try:
        from tools.camera_tool import take_photo
        
        success, result = take_photo()
        
        if success:
            # result 是本地路径，例如：data/images/plant_20260211_153000.jpg
            filename = os.path.basename(result)  # 提取文件名
            
            # 获取ngrok公网地址（如果没有则用localhost）
            from config import SERVER_CONFIG
            import requests
            
            # 尝试获取ngrok地址（如果你有更好的方式可以替换）
            base_url = request.host_url.rstrip('/')  # http://localhost:5000 或 ngrok地址
            
            image_url = f"{base_url}/images/{filename}"
            
            return jsonify({
                "success": True,
                "message": "拍照成功",
                "image_url": image_url,      # ✅ 完整URL，前端直接能用
                "image_path": result,        # ✅ 本地路径，备用
                "filename": filename,        # ✅ 文件名
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({
                "success": False,
                "error": result,
                "note": "树莓派摄像头服务可能未启动",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "note": "拍照接口内部错误"
        }), 500

# ============ AI智能建议API ============
@app.route('/api/ai/advice')
def get_ai_advice():
    """获取智能浇水建议"""
    try:
        from tools.ai_advisor import get_watering_advice
        
        # 1. 尝试获取实时数据
        try:
            from db_client import query_latest_data
            real_data = query_latest_data()
            
            if real_data and 'moisture' in real_data:
                # 使用真实数据库数据
                soil = real_data.get("moisture", 450)
                temp = real_data.get("temperature", 25.0)
                hum = real_data.get("humidity", 50.0)
                data_source = "database"
                data_note = "实时传感器数据"
            else:
                # 数据库没有数据，使用模拟
                raise ValueError("数据库无数据")
                
        except Exception as db_error:
            # 2. 数据库失败，使用当前内存数据
            if 'soil_moisture' in sensor_data:
                soil = sensor_data["soil_moisture"]
                temp = sensor_data["temperature"]
                hum = sensor_data["humidity"]
                data_source = "memory"
                data_note = "内存模拟数据"
            else:
                # 3. 最后降级到随机数据
                import random
                soil = random.randint(300, 700)
                temp = round(20 + random.random() * 10, 1)
                hum = round(40 + random.random() * 30, 1)
                data_source = "simulated"
                data_note = "随机模拟数据"
        
        # 获取AI建议
        advice = get_watering_advice(soil, temp, hum)
        
        # 构建响应
        response = {
            "success": True,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": data_source,
            "data_note": data_note,
            "sensor_data": {
                "soil_moisture": soil,
                "temperature": temp,
                "humidity": hum
            },
            "advice": advice,
            "system_info": {
                "mode": system_status["mode"],
                "water_today": system_status["water_today"],
                "last_watered": system_status["last_watered"],
                "max_water_per_day": PLANT_CONFIG["max_water_per_day"]
            }
        }
        
        # 如果是自动模式，可以立即执行浇水建议
        if system_status["mode"] == "auto" and advice["should_water"]:
            response["auto_action"] = {
                "action": "watering",
                "duration": advice["suggested_duration"],
                "reason": "AI建议自动浇水"
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "获取AI建议时出错"
        }), 500

# ============ 植物病害检测API ============

@app.route('/api/disease/detect', methods=['POST'])
def detect_disease_api():
    """智能检测植物病害 - 返回格式化JSON"""
    image_path = None  # 提前声明，用于finally清理
    try:
        from tools.camera_tool import get_latest_image
        from tools.disease_detector import detect_disease_from_service
        
        # 获取图片（上传或最新）
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                import tempfile
                _, temp_path = tempfile.mkstemp(suffix='.jpg')
                file.save(temp_path)
                image_path = temp_path
                print(f"[病害检测] 保存上传图片到临时文件: {image_path}")
        
        if not image_path:
            success, latest_path = get_latest_image()
            if success:
                image_path = latest_path
                print(f"[病害检测] 使用最新拍摄图片: {image_path}")
            else:
                return jsonify({
                    "success": False,
                    "error": "未找到可分析的图片",
                    "message": "请先拍照或直接上传一张植物叶片图片。"
                }), 400
        
        # 调用病害检测服务
        detect_success, detect_result = detect_disease_from_service(image_path)
        
        if detect_success:
            # 从HTML中提取病害信息
            html = detect_result.get("html_response", "")
            
            # 简单规则匹配
            disease_name = "未知病害"
            treatment = "暂无治疗方案"
            prevention = "暂无预防措施"
            confidence = "low"
            
            if "Tomato___Early_blight" in html:
                disease_name = "番茄早疫病"
                treatment = "使用代森锰锌或百菌清，每隔7-10天喷施一次"
                prevention = "避免叶片潮湿，保持通风，轮作非茄科作物"
                confidence = "high"
            elif "Tomato___Late_blight" in html:
                disease_name = "番茄晚疫病"
                treatment = "使用霜脲氰或烯酰吗啉，及时清除病叶"
                prevention = "控制湿度，避免夜间灌溉"
                confidence = "high"
            elif "Tomato___healthy" in html:
                disease_name = "健康"
                treatment = "无需治疗"
                prevention = "保持当前养护方式"
                confidence = "high"
            
            return jsonify({
                "success": True,
                "message": "病害检测完成",
                "disease_name": disease_name,
                "confidence": confidence,
                "treatment": treatment,
                "prevention": prevention,
                "image": os.path.basename(image_path),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({
                "success": False,
                "error": detect_result,
                "message": "病害检测服务执行失败"
            }), 500
            
    except Exception as e:
        print(f"[病害检测] 错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "病害检测接口内部错误"
        }), 500
    
    finally:
        # ========== ✅ 关键修复：删除临时文件 ==========
        if image_path and 'temp' in image_path:
            try:
                os.remove(image_path)
                print(f"[病害检测] 已删除临时文件: {image_path}")
            except Exception as e:
                print(f"[病害检测] 删除临时文件失败: {e}")

# ============ 静态文件访问 ============
@app.route('/images/<filename>')
def get_image(filename):
    """提供图片访问"""
    from flask import send_from_directory
    import os
    
    # 图片存储目录
    image_dir = os.path.join('data', 'images')
    
    # 检查文件是否存在
    if not os.path.exists(os.path.join(image_dir, filename)):
        return jsonify({
            "success": False,
            "error": "图片不存在"
        }), 404
    
    return send_from_directory(image_dir, filename)

# ============ 主程序 ============

def print_banner():
    """打印启动横幅"""
    banner = f"""
    ========================================
        智能植物养护系统 - 后端服务
    ========================================
    项目路径: {os.path.abspath('.')}
    服务地址: http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}
    启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    数据文件: {CONFIG['data_file']}
    ========================================
    配置信息:
      自动浇水阈值: {PLANT_CONFIG['auto_water_threshold']}
      单次浇水量: {PLANT_CONFIG['water_duration']}秒
      每日最大浇水: {PLANT_CONFIG['max_water_per_day']}秒
      检查间隔: {PLANT_CONFIG['check_interval']}秒
    ========================================
API列表:
  GET  /              - 系统首页
  GET  /api/status    - 系统状态
  GET  /api/data      - 传感器数据
  GET  /api/history   - 历史数据
  GET  /api/config    - 系统配置
  GET  /api/ai/advice  - 智能浇水建议（规则引擎）
  POST /api/water     - 控制浇水（手动模式）
  POST /api/mode      - 切换系统模式
  POST /api/sensor    - 接收硬件数据
  POST /api/camera/take - 控制拍照================
    提示: 按 Ctrl+C 停止服务
    ========================================
    """
    print(banner)

if __name__ == '__main__':
    print_banner()
    app.run(
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        debug=SYSTEM_CONFIG['debug']
    )