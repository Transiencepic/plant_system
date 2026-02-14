# Plant Monitoring System API 文档

## 项目概述

### 项目简介
本项目是一个基于树莓派、Arduino等硬件的智能植物自动养护系统。系统通过传感器监测植物生长环境，用户可通过远程方式查看植物环境数据，并控制浇水操作。

### 项目目标
为植物爱好者、上班族及家庭用户提供便捷的室内植物养护解决方案，帮助用户轻松管理植物生长环境。

## 接口约定

### ⚠️ 重要：ngrok免费版访客警告

由于使用ngrok免费版，所有请求**必须携带以下请求头**，否则会被拦截：

```javascript
headers: {
  'ngrok-skip-browser-warning': 'true'
}
```

### 基础信息
- **基础URL**: `http://localhost:5000`
- **API前缀**: `/api`
- **数据格式**: JSON
- **跨域支持**: 默认允许

### 请求规范
1. **GET请求**：直接通过URL访问，无请求体
2. **POST请求**：
   - 请求头：`Content-Type: application/json`
   - 请求体：JSON格式的数据

### 响应格式
#### 成功响应
各接口响应格式不同，详见具体接口。

#### 错误响应
```json
{
  "error": "错误描述信息",
  "message": "详细的错误说明"
}
```
### HTTP状态码说明
|状态码	|含义|使用场景|
|---------|---------|---------|
|200|成功|请求成功处理|
|400|客户端错误|请求参数无效、超出限制等|
|404|接口不存在|
|500|服务器错误|服务器内部处理异常|


### 具体API接口文档

#### 系统首页
- **接口说明**：访问系统首页，查看API列表和系统基本信息
- **请求方法**：GET
- **请求URL**：`/`
- **请求头**：无特殊要求
- **请求参数**：无

#### 1.获取系统状态
- **接口说明**：获取智能植物养护系统的当前运行状态
- **请求方法**：GET
- **请求URL**：`/api/status`
- **请求头**：无特殊要求
- **请求参数**：无


#### 成功响应示例
```json
{
  "system": "智能植物养护系统",
  "status": "running",
  "mode": "manual",
  "uptime": "2024-01-01 10:00:00",
  "hardware": "waiting",
  "version": "1.0.0",
  "water_today": 0,
  "last_watered": null
}
```
#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|system|string|系统名称|
|status|string|系统运行状态（running/stopped）|
|mode|string|当前模式（manual/auto）|
|uptime|string|系统启动时间|
|hardware|string|硬件连接状态|
|version|string|系统版本|
|water_today|number|今日已浇水时长（秒）|
|last_watered|string/null|上次浇水时|

#### 2.获取传感器数据
- **接口说明**：获取当前植物环境传感器数据（温度、湿度、土壤湿度、光照等）
- **请求方法**：GET
- **请求URL**：`/api/data`
- **请求头**：无特殊要求
- **请求参数**：无
- **数据来源**: 支持模拟数据和硬件数据两种模式

#### 成功响应示例
```json
{
  "success": true,
  "timestamp": "2024-01-01 10:30:00",
  "data": {
    "temperature": 24.5,
    "humidity": 58.3,
    "soil_moisture": 420,
    "light_level": 780,
    "last_update": "2024-01-01 10:30:00",
    "last_simulated": "2024-01-01T10:30:00.123456",
    "source": "simulated"
  },
  "source": "simulated",
  "mode": "manual",
  "note": "模拟数据"
}
```

#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean|请求是否成功|
|timestamp|string|数据获取时间|
|data|object|传感器数据对象|
|data.temperature|number|温度值（单位：°C，范围：20-30）|
|data.humidity|number|湿度值（单位：%，范围：40-70）|
|data.soil_moisture|number|土壤湿度值（值越小越湿，范围：200-800）|
|data.light_level|number|光照强度（单位：lux，范围：500-1000）|
|data.last_update|string|数据最后更新时间|
|data.last_simulated|string|最后模拟时间（仅模拟数据时有）|
|data.source|string|数据来源，值为"simulated"（模拟数据）或"hardware"（硬件数据）。如果未明确设置，默认值为"simulated"|
|source|string|数据来源类型|
|mode|string|系统当前模式（manual/auto）|
|note|string|数据备注说明|

#### 数据模拟规则
1.**温度**：基于当前时间模拟，白天较高，夜晚较低
2.**湿度**：在40-70%范围内随机变化
3.**土壤湿度**：随时间缓慢下降（模拟水分蒸发），浇水后上升
4.**光照**：在500-1000 lux范围内随机变化

#### 注意事项
- 当`data.source`为`"simulated"`时，数据为程序生成的模拟数据
- 当`data.source`为`"hardware"`时，数据来自真实硬件传感器
- 土壤湿度值：数值越小表示土壤越湿润，数值越大表示土壤越干燥

#### 3.控制浇水
- **接口说明**:手动控制植物浇水，仅在手动模式下有效
- **请求方法**：POST
- **请求URL**：`/api/water`
- **请求头**：`Content-Type: application/json`
- **请求体**：
```json
{
  "seconds": 5
}
```
#### 请求参数说明
|参数名|类型|必填|默认值|说明|
|---------|---------|---------|---------|---------|
|seconds|number|否|5|浇水时长（秒）,最大30|

#### 成功响应示例（硬件执行成功）
```json
{
  "action": "watering",
  "duration": 5,
  "time": "2026-02-12 15:45:00",
  "water_today": 10,
  "new_moisture": 328,
  "hardware_success": true,
  "hardware_message": "浇水指令发送成功。设备响应：OK",
  "note": "（硬件执行成功）",
  "message": "成功浇水 5 秒",
  "remaining_today": 20
}
```
#### 成功响应示例（硬件执行失败）
```json
{
  "action": "watering",
  "duration": 5,
  "time": "2026-02-12 15:45:00",
  "water_today": 10,
  "new_moisture": 428,
  "hardware_success": false,
  "hardware_message": "连接硬件设备超时",
  "note": "（硬件执行失败：连接硬件设备超时）",
  "message": "成功浇水 5 秒",
  "remaining_today": 20
}
```

#### 错误响应示例
情况1：**系统已停止**
```json
{
  "error": "系统已停止"
}
```
状态码：400

情况2：**当前为自动模式**
```json
{
  "error": "当前为自动模式，请切换到手动模式后再操作"
}
```
状态码：400

情况3：**超过每日浇水限制**
```json
{
  "error": "超过每日浇水限制",
  "message": "今日已浇水 25 秒，最多可浇水 30 秒",
  "remaining": 5
}
```
状态码：400

#### 响应字段说明（成功时）
|字段名|类型|说明|
|---------|---------|---------|
|action|string|执行的动作（固定为"watering"）|
|duration|number|实际浇水时长（秒）|
|time|string|浇水执行时间|
|water_today|number|今日累计浇水时长（秒）|
|new_moisture|number|浇水后的土壤湿度值（值越小越湿）|
|hardware_success|boolean|硬件是否真的执行成功|
|hardware_message|string|硬件返回的详细信息|
|note|string|执行备注（成功/失败原因）|
|message|string|操作成功消息|
|remaining_today|number|今日剩余可浇水量（秒），基于最大30秒计算|

#### 业务规则
1.只有在系统运行状态（`running`为true）下才能浇水
2.只有在手动模式（`mode`为"manual"）下才能手动浇水
3.每日浇水总时长不能超过`PLANT_CONFIG["max_water_per_day"]`配置值
4.浇水后土壤湿度值会降低（模拟土壤变湿）
5.如果未指定`seconds`参数，使用`PLANT_CONFIG["water_duration"]`作为默认值

#### 4.切换系统模式
- **接口说明**:切换系统的控制模式（手动模式/自动模式）
- **请求方法**：POST
- **请求URL**：`/api/mode`
- **请求头**：`Content-Type: application/json`
- **请求体**：
```json
{
  "mode": "auto"
}
```
#### 请求参数说明
|参数名|类型|必填|允许值|说明|
|---------|---------|---------|---------|---------|
|mode|string|是|"manual" 或 "auto"|要切换到的系统模式|

#### 成功响应示例（切换到自动）
```json
{
  "success": true,
  "message": "系统模式已从 manual 切换为 auto",
  "old_mode": "manual",
  "new_mode": "auto",
  "auto_config": {
    "water_threshold": 300,
    "water_duration": 5,
    "check_interval": 300
  }
}
```

#### 成功响应示例（切换到手动）
```json
{
  "success": true,
  "message": "系统模式已从 auto 切换为 manual",
  "old_mode": "auto",
  "new_mode": "manual",
  "auto_config": null
}
```

#### 错误响应示例
情况1：**无效的参数模式**
```json
{
  "error": "无效的模式",
  "message": "模式必须是 'manual' 或 'auto'"
}
```
状态码：400

情况2：**服务器内部错误**
```json
{
  "error": "错误描述信息"
}
```
状态码：500


#### 响应字段说明（成功时）
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean|操作是否成功|
|message|string|操作结果消息|
|old_mode|string|切换前的模式|
|new_mode|string|切换后的模式|
|auto_config|object/null|仅在切换到自动模式时返回自动浇水配置|
|auto_config.water_threshold|number|自动浇水阈值（土壤湿度高于此值时触发浇水）|
|auto_config.water_duration|number|单次浇水时长（秒）|
|auto_config.check_interval|number|检查间隔（秒）|

#### 业务规则
1.只允许切换到 "manual"（手动模式）或 "auto"（自动模式）两种模式
2.切换到自动模式时，会返回当前的自动浇水配置参数
3.切换到手动模式时，`auto_config`字段为`null`
4.模式切换会立即生效，影响系统的浇水控制逻辑

#### 5.接受硬件传感器数据（！此接口为硬件专用，前端无需调用！）
- **接口说明**:接收硬件设备（树莓派/Arduino）发送的传感器数据，并在自动模式下根据数据判断是否需要浇水
- **请求方法**：POST
- **请求URL**：`/api/sensor`
- **请求头**：`Content-Type: application/json`
- **请求体**：
```json
{
  "temperature": 25.5,
  "humidity": 60.2,
  "soil_moisture": 480
}
```
#### 请求参数说明
|参数名|类型|必填|说明|
|---------|---------|---------|---------|
|temperature|number|是|温度值（单位：°C）|
|humidity|number|是|湿度值（单位：%）|
|soil_moisture|number|是|土壤湿度值（值越小越湿）|

#### 成功响应示例
情况1：**仅接收数据，不需要浇水**
```json
{
  "success": true,
  "message": "传感器数据接收成功",
  "timestamp": "2024-01-01 11:00:00",
  "mode": "auto",
  "command": {
    "action": "none",
    "message": "数据接收成功"
  },
  "data_received": {
    "temperature": 25.5,
    "humidity": 60.2,
    "soil_moisture": 480
  }
}
```


情况2：**自动模式下需要浇水**
```json
{
  "success": true,
  "message": "传感器数据接收成功",
  "timestamp": "2024-01-01 11:00:00",
  "mode": "auto",
  "command": {
    "action": "water",
    "duration": 5,
    "reason": "土壤湿度 520 高于阈值 300",
    "message": "需要浇水"
  },
  "data_received": {
    "temperature": 25.5,
    "humidity": 60.2,
    "soil_moisture": 520
  }
}
```

#### 错误响应示例
情况1：**缺少必要字段**
```json
{
  "error": "数据格式错误",
  "message": "缺少必要字段: soil_moisture",
  "required_fields": ["temperature", "humidity", "soil_moisture"]
}
```
状态码：400

#### 响应字段说明（成功时）
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean|数据接收是否成功|
|message|string|操作结果消息|
|timestamp|string|数据接收时间|
|mode|string|系统当前模式（manual/auto）|
|command|object|系统返回的指令|
|command.action|string|指令动作（none/water）|
|command.duration|number|浇水时长（秒，仅当action为water时返回）|
|command.reason|string|浇水原因说明（仅当action为water时返回）|
|command.message|string|指令消息|
|data_received|object|接收到的传感器数据|
|data_received.temperature|number|接收到的温度值|
|data_received.soil_moisture|number|接收到的土壤湿度值|

#### 业务规则
1.必须包含`temperature`、`humidity`、`soil_moisture`三个字段
2.接收到的数据会更新系统的传感器数据，并标记数据来源为`"hardware"`
3.在手动模式（`mode`为"manual"）下，仅接收数据，不返回浇水指令
4.在自动模式（`mode`为"auto"）下，系统会根据接收到的土壤湿度判断是否需要浇水：
* **浇水条件**：如果土壤湿度值大于`PLANT_CONFIG["auto_water_threshold"]`，则返回浇水指令
* **浇水指令**：浇水指令包含建议的浇水时长（`PLANT_CONFIG["water_duration"]`）
* **浇水限制**：同时检查是否超过每日浇水限制

#### 6.1获取真实历史数据
- **接口说明**：从数据库查询真实传感器历史数据，无数据时自动降级为模拟数据。
- **请求方法**：GET
- **请求URL**：`/api/history/real`
- **请求头**：无特殊要求
- **请求参数**：

|参数|类型|必填|默认|说明|
|---------|---------|---------|---------|---------|
|hours|int|否|24|查询小时范围，最大168（7天）|
limits|int|否|100|返回条数，最大1000|

#### 成功响应示例（真实数据库）
```json
{
  "success": true,
  "source": "database",
  "period_hours": 24,
  "data_count": 24,
  "data": [
    {
      "time": "2026-02-12 15:00:00",
      "temperature": 25.0,
      "humidity": 50.0,
      "moisture": 428
    }
  ]
}
```
#### 成功响应示例（模拟降级）
```json
{
  "success": true,
  "source": "simulated",
  "note": "数据库中没有历史数据，返回模拟数据",
  "period_hours": 24,
  "data_count": 12,
  "data": [
    {
      "time": "2026-02-12 15:00:00",
      "temperature": 25.0,
      "humidity": 50.0,
      "moisture": 428
    }
  ]
}
```

#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean|请求是否成功|
|source|string|数据来源：database/simulated/error|
|period_hours|number|查询的时间范围（小时）|
|data_count|number|数据点的数量|
|note|string|备注信息（仅模拟/错误时有）|
|data|array|历史数据数组|
|data[].time|string|时间点（格式：YYYY-MM-DD HH:MM:SS）|
|data[].temperature|number|温度历史值（单位：°C）|
|data[].humidity|number|湿度历史值（单位：%）|
|data[].moisture|number|土壤湿度历史值（值越小越湿）|

#### 6.2获取历史数据(兼容旧版)
- **接口说明**：兼容旧版本，与`/api/history/real`返回完全相同。推荐新代码直接使用`/api/history/real`。
- **请求方法**：GET
- **请求URL**：`/api/history/real`
- **请求参数**：同`/api/history/real`
- **响应格式**：同`/api/history/real`
- **注意**：此接口仅为兼容旧版前端，新开发请直接使用`/api/history/real`。
  


#### 7.获取系统配置
- **接口说明**： 获取当前系统的完整配置信息，包括服务器、数据、硬件和植物养护配置
- **请求方法**：GET
- **请求URL**：`/api/config`
- **请求头**：无特殊要求
- **请求参数**：无

#### 成功响应示例
```json
{
  "system": {
    "name": "智能植物养护系统",
    "version": "1.0.0",
    "author": "周佳乐，许隽玮，郑淇匀",
    "debug": true
  },
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "timeout": 30
  },
  "data": {
    "save_interval": 300,
    "history_days": 7,
    "data_file": "data/sensor_data.json",
    "log_file": "system.log"
  },
  "hardware": {
    "serial_port": "/dev/ttyACM0",
    "baud_rate": 9600,
    "camera_port": 0
  },
  "plant": {
    "auto_water_threshold": 300,
    "water_duration": 5,
    "max_water_per_day": 30,
    "check_interval": 300
  },
  "current_mode": "manual",
  "current_data_file": "data/sensor_data.json"
}
```

#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|system|object|系统运行配置|
|system.author|string|作者信息|
|system.debug|boolean|调试模式开关|
|system.name|string|系统名称|
|server|object|服务器配置|
|server.host|string|服务器监听地址|
|server.port|number|服务器监听端口|
|server.timeout|number|请求超时时间（秒）|
|data|object|数据与日志配置|
|data.save_interval|number|自动保存数据间隔（秒）|
|data.history_days|number|保留历史数据的天数|
|data.data_file|string|传感器数据存储文件路径|
|data.log_file|string|日志文件存储路径|
|hardware|object|硬件配置（仅供参考，实际硬件参数可能不同）|
|hardware.serial_port|string|Arduino连接的串口|
|hardware.baud_rate|number|串口通信波特率|
|hardware.camera_port|number|树莓派摄像头端口|
|plant|object|植物养护配置|
|plant.auto_water_threshold|number|自动浇水阈值（土壤湿度高于此值时触发浇水）|
|plant.water_duration|number|单次浇水时长（秒）|
|plant.max_water_per_day|number|每日最大浇水时长（秒）|
|plant.check_interval|number|自动模式检查间隔（秒）|
|current_mode|string|系统当前运行模式（manual/auto）|
|current_data_file|string|当前使用的数据文件路径|

#### 注意事项
1.配置信息从项目的`config.py`文件中读取，实际值以配置文件为准。示例中的数值为默认配置值
2.`hardware`配置仅供参考，具体硬件连接请以实际电路为准
3.修改配置需要重启服务才能生效（当前版本不支持热更新配置）
4.所有路径均为相对于项目根目录的路径

#### 8.主动拍照
- **接口说明**： 控制树莓派摄像头拍摄一张照片，并返回可直接访问的图片URL。
- **请求方法**：POST
- **请求URL**：`/api/camera/take`
- **请求头**：无特殊要求
- **请求参数**：无

#### 成功响应示例
```json
{
  "success": true,
  "message": "拍照成功",
  "image_url": "https://ratio-kaylie-severally.ngrok-free.dev/images/plant_20260212_164602.jpg",
  "image_path": "data/images/plant_20260212_164602.jpg",
  "filename": "plant_20260212_164602.jpg",
  "timestamp": "2026-02-12 16:46:02"
}
```
前端直接用`image_url`赋值给 <img> 标签即可显示图片。

#### 失败响应示例（摄像头未就绪）
```json
{
  "success": false,
  "error": "连接摄像头失败: Connection refused",
  "note": "树莓派摄像头服务可能未启动",
  "timestamp": "2026-02-12 16:46:02"
}
```
状态码：200（业务失败，不是HTTP错误）

#### 异常响应示例（服务器内部错误）
```json
{
  "success": false,
  "error": "module 'tools.camera_tool' has no attribute 'take_photo'",
  "note": "拍照接口内部错误",
  "timestamp": "2026-02-12 16:46:02"
}
```
状态码：500

#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean	拍照是否成功|
|message|string|成功时的提示信息|
|image_url|string|图片公网访问地址（前端直接用这个）|
|image_path|string|图片在服务器上的本地路径（仅供调试）|
|filename|string|图片文件名|
|timestamp|string|拍照时间|
|note|string|失败时的补充说明|

📌 **当前状态说明：**
- 此接口依赖硬件同学提供的树莓派摄像头服务
- 在硬件地址配置完成前，`take_photo()` 会返回模拟失败
- 前端可根据 `success: false` 和 `note` 字段提示用户

📌 **图片访问说明：**
- 返回的 `image_url` 可直接用于 `<img>` 标签
- 图片访问格式：`https://你的域名/images/文件名.jpg`
- 如返回404，表示图片文件已丢失或被清理

#### 9.智能浇水建议（规则引擎）
- **接口说明**： 基于当前土壤湿度、温度、湿度，通过规则引擎给出是否浇水、浇多久的建议。
- **请求方法**：GET
- **请求URL**：`/api/ai/advice`
- **请求参数**：无

#### 成功响应示例（基于真实数据）
```json
{
  "success": true,
  "timestamp": "2026-02-12 15:30:00",
  "data_source": "database",
  "data_note": "实时传感器数据",
  "sensor_data": {
    "soil_moisture": 428,
    "temperature": 25.0,
    "humidity": 50.0
  },
  "advice": {
    "should_water": true,
    "score": 65,
    "threshold": 60,
    "plant_status": "略干🍂",
    "suggested_duration": 5,
    "reasons": [
      "🌵 土壤略干 (428 > 300)",
      "☀️ 温暖 (25.0°C)",
      "🌤️ 湿度适中 (50.0%)"
    ],
    "ai_version": "1.0 (规则引擎)",
    "note": "基于规则引擎，后期可升级为AI模型"
  },
  "system_info": {
    "mode": "auto",
    "water_today": 10,
    "last_watered": "2026-02-12 15:25:00",
    "max_water_per_day": 30
  }
}
```

#### 成功响应示例（自动模式 + 需要浇水）
```json
{
  "success": true,
  "timestamp": "2026-02-12 15:30:00",
  "data_source": "database",
  "data_note": "实时传感器数据",
  "sensor_data": {
    "soil_moisture": 428,
    "temperature": 25.0,
    "humidity": 50.0
  },
  "advice": {
    "should_water": true,
    "score": 65,
    "threshold": 60,
    "plant_status": "略干🍂",
    "suggested_duration": 5,
    "reasons": [
      "🌵 土壤略干 (428 > 300)",
      "☀️ 温暖 (25.0°C)"
    ],
    "ai_version": "1.0 (规则引擎)",
    "note": "基于规则引擎，后期可升级为AI模型"
  },
  "system_info": {
    "mode": "auto",
    "water_today": 10,
    "last_watered": "2026-02-12 15:25:00",
    "max_water_per_day": 30
  },
  "auto_action": {
    "action": "watering",
    "duration": 5,
    "reason": "AI建议自动浇水"
  }
}
```

#### 响应字段说明
|字段	|类型	|说明|
|---------|---------|---------|
|success|boolean|请求是否成功|
|timestamp|string|建议生成时间|
|data_source|string|数据来源：database（真实）/memory（内存）/simulated（随机）|
|data_note|string|数据来源详细说明|
|sensor_data|object|当前传感器数据|
|sensor_data.soil_moisture|number|土壤湿度（值越小越湿）|
|sensor_data.temperature|number|温度（°C）|
|sensor_data.humidity|number|湿度（%）|
|advice|object|浇水建议详情|
|advice.should_water|boolean|是否建议浇水|
|advice.score|number|浇水紧迫度分数（0-100）|
|advice.threshold|number|建议阈值（≥60分建议浇水）|
|advice.plant_status|string|植物状态（过湿💧/健康🌱/略干🍂/干旱🏜️）|
|advice.suggested_duration|number|建议浇水时长（秒）|
|advice.reasons|array|决策理由列表（带图标）|
|advice.ai_version|string|规则引擎版本|
|advice.note|string|备注说明|
|system_info|object|系统当前状态|
|auto_action|object|仅在自动模式且需要浇水时返回|
|auto_action.action|string|执行的动作（"watering"）|
|auto_action.duration|number|执行浇水时长（秒）|
|auto_action.reason|string|执行原因|

#### 10.植物病害检测
- **接口说明**： 上传植物叶片图片，调用AI模型检测病害类型，返回病害名称、治疗方案和预防措施。
- **请求方法**：POST
- **请求URL**：`/api/disease/detect`
- **请求头**：Content-Type: multipart/form-data
- **请求参数**：无
|参数|类型|必填|说明|
|---------|---------|---------|---------|
|image|file|否|叶片图片，不传则使用最新拍摄照片|

#### 成功响应示例（检测到病害）
```json
{
  "success": true,
  "message": "病害检测完成",
  "disease_name": "番茄早疫病",
  "confidence": "high",
  "treatment": "使用代森锰锌或百菌清，每隔7-10天喷施一次",
  "prevention": "避免叶片潮湿，保持通风，轮作非茄科作物",
  "image": "plant_20260212_164602.jpg",
  "timestamp": "2026-02-12 16:46:02"
}
```

#### 成功响应示例（健康）
```json
{
  "success": true,
  "message": "病害检测完成",
  "disease_name": "健康",
  "confidence": "high",
  "treatment": "无需治疗",
  "prevention": "保持当前养护方式",
  "image": "plant_20260212_164602.jpg",
  "timestamp": "2026-02-12 16:46:02"
}
```

#### 成功响应示例（未识别）
```json
{
  "success": true,
  "message": "病害检测完成",
  "disease_name": "未知病害",
  "confidence": "low",
  "treatment": "暂无治疗方案",
  "prevention": "暂无预防措施",
  "image": "plant_20260212_164602.jpg",
  "timestamp": "2026-02-12 16:46:02"
}
```

####  错误响应示例（无图片）
```json
{
  "success": false,
  "error": "未找到可分析的图片",
  "message": "请先拍照或直接上传一张植物叶片图片。"
}
```
状态码：400

#### 错误响应示例（AI服务未启动）
```json
{
  "success": false,
  "error": "无法连接到病害检测服务，请确保它正在运行: http://127.0.0.1:5001",
  "message": "病害检测服务执行失败"
}
```
状态码：500

#### 响应字段说明
|字段名|类型|说明|
|---------|---------|---------|
|success|boolean|检测是否成功|
|message|string|操作结果消息|
|disease_name|string|病害名称（健康/番茄早疫病/番茄晚疫病/未知病害等）|
|confidence|string|置信度：high（高可信） / low（低可信/未识别）|
|treatment|string|治疗方案|
|prevention|string|预防措施|
|image|string|检测的图片文件名|
|timestamp|string|检测完成时间|
|error|string|失败时的错误描述|

📌 **使用说明：**
1. 优先使用场景：前端拍照 → 自动用最新照片检测（不传 image 参数）
2. 备选场景：用户上传本地图片 → 传 image 文件
3. 检测完成后，临时文件会自动删除，无需前端处理

📌 **当前支持的病害：**
- 番茄早疫病
- 番茄晚疫病
- 健康叶片
- 其他病害统一返回“未知病害”

📌 **置信度说明：**
- `confidence: "high"` → 明确匹配到已知病害
- `confidence: "low"` → 未匹配到已知病害，可能是其他品种或病害
