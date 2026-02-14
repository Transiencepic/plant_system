# plant_system/tools/disease_detector.py
"""
病害检测工具 - 调用独立运行的植物病害检测服务
"""
import requests
import json
import os
from config import HARDWARE_CONFIG

# 从配置文件读取病害检测服务地址
DISEASE_SERVICE_URL = HARDWARE_CONFIG.get("disease_service_url", "http://127.0.0.1:5001")

def detect_disease_from_service(image_path):
    """
    调用独立的病害检测服务分析图片。
    
    参数:
        image_path (str): 本地图片文件的路径。
        
    返回:
        tuple: (success: bool, result: dict or str)
        - 如果成功，result为包含预测结果的字典。
        - 如果失败，result为错误信息字符串。
    """
    # 1. 检查图片文件是否存在
    if not os.path.exists(image_path):
        return False, f"图片文件不存在: {image_path}"
    
    # 2. 准备请求（关键修改：端点为 /submit，字段名为 image）
    url = f"{DISEASE_SERVICE_URL}/submit"
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
            
            # 3. 发送POST请求到病害检测服务
            response = requests.post(url, files=files, timeout=30)
        
        # 4. 处理响应
        if response.status_code == 200:
            # 服务返回的是HTML，我们先视为成功，后续再解析
            # 这里先返回原始文本或一个成功标志
            return True, {"status": "success", "html_response": response.text[:500]} # 只截取前500字符便于查看
        else:
            # 服务返回错误状态码
            return False, f"病害检测服务返回错误 (状态码 {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, f"无法连接到病害检测服务，请确保它正在运行: {DISEASE_SERVICE_URL}"
    except requests.exceptions.Timeout:
        return False, "连接病害检测服务超时。"
    except Exception as e:
        return False, f"调用病害检测服务时发生未知错误: {str(e)}"

# 快速测试函数（可选）
def test_detection():
    """测试病害检测服务是否连通"""
    print("🧪 测试病害检测服务连接...")
    
    # 使用病害检测项目自带的测试图片 (你需要先找到一张)
    # 假设测试图片在病害检测项目的 test_images 文件夹里
    test_image_path = r"D:\my_projects\Plant-Disease-Detection\test_images\Tomato_Early_blight.JPG"
    
    if os.path.exists(test_image_path):
        success, result = detect_disease_from_service(test_image_path)
        if success:
            print(f"✅ 测试成功！检测结果: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ 测试失败: {result}")
    else:
        print("⚠️  未找到测试图片，请手动指定一张图片路径进行测试。")
        # 你可以在这里临时指定一个你有的植物叶子图片路径
        # test_image_path = "你的图片路径.jpg"


if __name__ == "__main__":
    # 直接运行此文件时执行测试
    test_detection()