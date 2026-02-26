"""
智能植物养护系统 - 配置文件
此文件为系统的唯一配置中心，所有设置在此定义。
"""
#加载环境变量
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量

import os

# ============ 系统基础配置 ============
SYSTEM_CONFIG = {
    "name": "智能植物养护系统",
    "version": "1.0.0",
    "author": "周佳乐，许隽玮，郑淇匀",  
    "debug": True,  # 开发时设为True，部署时建议设为False
    # AI配置 
    "ai_enabled": True,                    # 启用AI功能
    "openai_api_key": os.getenv('OPENAI_API_KEY', ''),  # 从环境变量读取
    "ai_model": "gpt-3.5-turbo",          # 使用这个模型（便宜且够用）
    "ai_max_tokens": 300,                 # AI响应最大长度
    "ai_temperature": 0.7,                # 创造性（0=保守，1=有创意）
}

# ============ 服务器配置 ============
# 此部分配置与Flask应用运行相关
SERVER_CONFIG = {
    "host": "0.0.0.0",  # 允许任何网络接口访问，方便测试
    "port": 5000,       # 服务运行的端口号
    "timeout": 30       # 请求超时时间（秒）
}

# ============ 数据与日志配置 ============
# 此部分配置与数据保存、记录相关
DATA_CONFIG = {
    "save_interval": 300,          # 自动保存数据的间隔（秒），300秒=5分钟
    "history_days": 7,             # 保留历史数据的天数
    "data_file": "data/sensor_data.json", # 传感器数据存储文件名 (已统一)
    "log_file": "system.log",       # 系统运行日志文件名
    "influxdb": {
        "host": os.getenv('INFLUXDB_HOST', 'http://localhost:8086'),  # 从环境变量读取，没有则用默认值
        "token": os.getenv('INFLUXDB_TOKEN', ''),  # 从环境变量读取
        "org": os.getenv('INFLUXDB_ORG', 'my_plant_org'),
        "bucket": os.getenv('INFLUXDB_BUCKET', 'plant_bucket')
    }
}

# ============ 硬件配置（待连接） ============
# 树莓派和Arduino到货并连接后再调整此部分
HARDWARE_CONFIG = {
    "disease_service_url": "http://127.0.0.1:5001",  # AI病害检测服务
    "serial_port": "/dev/ttyACM0",  # Arduino连接的串口（Linux树莓派）
    # "serial_port": "COM3",         # Arduino连接的串口（Windows测试用，注意切换）
    "baud_rate": 9600,               # 串口通信波特率，必须与Arduino程序一致
    "camera_port": 0,                 # 树莓派摄像头端口

    # ========== 以下两项需要硬件同学提供具体值 ==========
    # 1. 浇水控制地址：硬件同学设备上运行的HTTP服务地址
    "water_device_url": " https://leptodactylous-knickknacked-astrid.ngrok-free.dev/api/water",
    
    # 2. 拍照服务地址：树莓派上拍照Flask服务的地址
    "camera_service_url": " https://leptodactylous-knickknacked-astrid.ngrok-free.dev/photo"
}

# ============ 植物养护逻辑配置 ============
# 此部分配置控制自动浇水的行为逻辑
PLANT_CONFIG = {
    "auto_water_threshold": 300,    # 土壤湿度低于此值则触发自动浇水
    "water_duration": 5,            # 单次自动浇水的时长（秒）
    "max_water_per_day": 3000,        # 每日最大浇水总时长（秒），防止过度浇水
    "check_interval": 300           # 自动检查土壤湿度的间隔（秒）
}

# ============ 配置使用说明 ============
# 在其他文件中，你可以这样导入和使用配置：
# from config import SERVER_CONFIG, DATA_CONFIG
# port = SERVER_CONFIG['port']
# data_file = DATA_CONFIG['data_file']