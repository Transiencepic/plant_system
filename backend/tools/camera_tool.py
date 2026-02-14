# tools/camera_tool.py
"""
最简单的摄像头工具
只有一个功能：从树莓派拍照
"""
import requests
import datetime
import os
from config import HARDWARE_CONFIG


def take_photo():
    """
    从树莓派拍照并保存到本地
    返回: (成功与否, 图片路径或错误信息)
    """
    # 1. 获取摄像头地址
    camera_url = HARDWARE_CONFIG.get("camera_service_url", "http://192.168.1.247:5000/capture")
    
    print(f"[camera_tool] 正在调用的硬件地址是: {camera_url}")

    # 2. 创建保存目录
    save_dir = "data/images"
    os.makedirs(save_dir, exist_ok=True)
    
    # 3. 生成文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plant_{timestamp}.jpg"
    filepath = os.path.join(save_dir, filename)
    
    try:
        # 4. 请求拍照（✅ 加上请求头）
        headers = {
            'ngrok-skip-browser-warning': 'true'   # 就是这里！
        }
        response = requests.get(camera_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            # 5. 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return True, filepath
        else:
            return False, f"拍照失败: 状态码{response.status_code}"
            
    except Exception as e:
        return False, f"连接摄像头失败: {str(e)}"

def get_latest_image():
    """
    获取最新保存的图片文件路径。
    这里实现一个简单版本：假设图片都保存在 'data/images' 目录，并返回最新的一个。
    """
    import os
    import glob
    
    save_dir = "data/images"
    if not os.path.exists(save_dir):
        return False, f"图片目录不存在: {save_dir}"
    
    # 获取目录下所有的jpg文件
    image_files = glob.glob(os.path.join(save_dir, "*.jpg"))
    if not image_files:
        return False, "没有找到图片文件"
    
    # 按修改时间排序，获取最新的
    latest_file = max(image_files, key=os.path.getmtime)
    return True, latest_file

# 测试代码
if __name__ == "__main__":
    print("测试拍照功能...")
    success, result = take_photo()
    
    if success:
        print(f"✓ 拍照成功！保存到: {result}")
    else:
        print(f"✗ 拍照失败: {result}")
        print("提示：请确保树莓派摄像头服务正在运行")