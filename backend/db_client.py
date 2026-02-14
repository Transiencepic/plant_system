# db_client.py
"""
InfluxDB 数据库客户端工具函数
此文件封装所有与数据库的交互，保持 app.py 简洁。
"""
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from config import DATA_CONFIG  # 导入我们刚刚测试成功的配置

def get_influx_client():
    """获取一个配置好的InfluxDB客户端实例（用完建议.close()关闭）"""
    config = DATA_CONFIG["influxdb"]  # 读取配置
    client = influxdb_client.InfluxDBClient(
        url=config["host"],
        token=config["token"],
        org=config["org"]
    )
    return client

def write_sensor_data(temperature, humidity, soil_moisture):
    """
    向数据库写入一条传感器数据。
    参数应为浮点数（温度、湿度）和整数（土壤湿度）。
    """
    config = DATA_CONFIG["influxdb"]
    client = get_influx_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # 构建数据点（对应Arduino的格式）
    point = influxdb_client.Point("environment") \
        .tag("location", "arduino") \
        .field("temperature", float(temperature)) \
        .field("humidity", float(humidity)) \
        .field("moisture", int(soil_moisture))
    
    try:
        # 写入数据
        write_api.write(bucket=config["bucket"], record=point)
        success = True
    except Exception as e:
        print(f"[db_client] 写入数据库失败: {e}")
        success = False
    finally:
        client.close()  # 记得关闭连接
    
    return success

def query_latest_data():
    """
    从数据库查询最新的一条传感器数据（优化版）。
    直接查询最后一条记录，而不是查询1小时再过滤。
    """
    config = DATA_CONFIG["influxdb"]
    client = get_influx_client()
    query_api = client.query_api()
    
    # 优化查询：直接获取最后一条记录
    query = f'''
    from(bucket: "{config['bucket']}")
      |> range(start: -24h) 
      |> filter(fn: (r) => r._measurement == "environment")
      |> last()
    '''
    
    data = {}
    try:
        result = query_api.query(query)
        
        # 解析查询结果
        for table in result:
            for record in table.records:
                field_name = record.get_field()  # temperature, humidity, moisture
                field_value = record.get_value()
                data[field_name] = field_value
        
        # 如果没有获取到完整数据，返回空字典
        if not all(key in data for key in ['temperature', 'humidity', 'moisture']):
            print(f"[db_client] 警告：查询到的数据不完整: {data}")
            return {}
                
    except Exception as e:
        print(f"[db_client] 查询数据库失败: {e}")
        return {}
    finally:
        client.close()
    
    return data

def query_history_data(hours=24, limit=100):
    """
    查询历史传感器数据。
    参数:
        hours: 查询多少小时内的数据（默认24小时）
        limit: 返回多少条数据（默认100条）
    返回: 列表格式的历史数据
    """
    config = DATA_CONFIG["influxdb"]
    client = get_influx_client()
    query_api = client.query_api()
    
    # 查询最近N小时的数据
    query = f'''
    from(bucket: "{config['bucket']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement == "environment")
      |> limit(n: {limit})
      |> sort(columns: ["_time"], desc: false)
    '''
    
    history = []
    try:
        result = query_api.query(query, org=config["org"])
        
        # 按时间分组组织数据
        temp_data = {}
        for table in result:
            for record in table.records:
                time_str = record.get_time().strftime("%Y-%m-%d %H:%M:%S")
                field_name = record.get_field()
                field_value = record.get_value()
                
                # 初始化时间点的数据
                if time_str not in temp_data:
                    temp_data[time_str] = {
                        "time": time_str,
                        "temperature": None,
                        "humidity": None,
                        "moisture": None
                    }
                
                # 更新对应字段的值
                if field_name == "temperature":
                    temp_data[time_str]["temperature"] = field_value
                elif field_name == "humidity":
                    temp_data[time_str]["humidity"] = field_value
                elif field_name == "moisture":
                    temp_data[time_str]["moisture"] = field_value
        
        # 转换为列表并过滤掉不完整的数据
        for time_key in sorted(temp_data.keys()):
            data_point = temp_data[time_key]
            # 只包含完整数据点
            if all(data_point[key] is not None for key in ["temperature", "humidity", "moisture"]):
                history.append(data_point)
        
        # 如果数据库没有数据，返回空列表
        if not history:
            print(f"[db_client] 数据库中没有最近{hours}小时的历史数据")
                
    except Exception as e:
        print(f"[db_client] 查询历史数据失败: {e}")
    finally:
        client.close()
    
    return history

# 在 db_client.py 末尾添加

def get_last_seen():
    """获取最近一次收到硬件数据的时间"""
    config = DATA_CONFIG["influxdb"]
    client = get_influx_client()
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{config['bucket']}")
      |> range(start: -24h)
      |> filter(fn: (r) => r._measurement == "environment")
      |> last()
      |> keep(columns: ["_time"])
    '''
    
    try:
        result = query_api.query(query)
        for table in result:
            for record in table.records:
                return record.get_time()
    except:
        pass
    finally:
        client.close()
    return None