# 智能植物养护系统 

## 项目说明
这是一个为智能植物养护项目提供数据存储、API接口和设备控制的核心后端服务。基于 Flask + InfluxDB + Ngrok 构建。

## 快速开始

### 前提条件
*   Python 3.9+
*   ［待硬件就绪］树莓派（拍照、浇水控制）

### 1.安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动后端所有服务（按顺序）
1.启动数据库
2.启动后端API
3.启动公网隧道（供队友访问）

### 3. 访问服务
- 首页：http://localhost:5000
- API文档：http://localhost:5000/

### 4.硬件清单

|组件|型号/规格|数量|用途|
|------|-----------|------|------|
| 树莓派 | 3B/4B | 1 | 主控，运行通信服务 |
| Arduino | Uno/Nano | 1 | 连接传感器和执行器 |
| 温湿度传感器 | DHT11 | 1 | 测量空气温湿度 |
| 土壤湿度传感器 | 模拟量 | 1 | 测量土壤湿度 |
| 水泵 | 5V/12V | 1 | 浇水执行器 |
| 继电器模块 | 5V | 1 | 控制水泵开关 |
| 摄像头 | USB或CSI | 1 | 拍摄植物照片 |

详细接线图请参考 `hardware/README.md`

## 📁项目结构

plant_system/

├── backend/ # 后端核心代码

│ ├── app.py # Flask主应用，所有API路由定义

│ ├── config.py # 系统配置文件

│ ├── db_client.py # InfluxDB数据库客户端

│ ├── requirements.txt # Python依赖包列表

│ └── tools/ # 核心工具函数目录

│ ├── ai_advisor.py # AI建议生成模块

│ ├── camera_tool.py # 摄像头控制模块

│ ├── disease_detector.py # 病害检测模块（调用AI模型）

│ └── watering.py # 浇水控制模块

├── frontend/ # 前端代码

│ ├── index.html # 主页面

│ └── static/ # 静态资源

│ ├── css/ # 样式文件

│ │ └── style.css

│ └── js/ # JavaScript文件

│ ├── config.js # 前端配置文件（API端点配置）

│ ├── data-manager.js # 数据管理逻辑

│ ├── mock-api.js # 模拟API（仅开发用）

│ └── ui-components.js # UI组件

├── hardware/                           # 硬件控制代码

│   ├── arduino/                         # Arduino代码

│   │   └── plant_monitor.ino              # 传感器读取 + 水泵控制

│   ├── raspberry_pi/                      # 树莓派代码

│   │   └── main.py                          # 串口通信 + 拍照 + 与后端通信

│   ├── README.md                          # 硬件文档

├── ai_model/ # AI模型文件（需自行下载）

├── docs/ # 文档

│ ├── README.md # 本文档

│ └── API_DOCUMENTATION.md # 详细的API接口文档

├── data/ # 本地模拟数据存储目录

│ └── images/ # 测试图片存放位置

├── .env # 环境变量（请勿上传）

└── .gitignore # Git忽略文件配置


## AI模型说明
本项目的植物病害检测功能基于开源深度学习模型实现：
- **原项目地址**：https://github.com/manthan89-py/Plant-Disease-Detection
- **模型文件**：需要下载 `plant\_disease\_model\_1\_latest.pt` 等文件
- **下载后放置位置**：项目根目录的 `ai\_model/` 文件夹下
- **依赖库**：PyTorch、Torchvision等（已在 `requirements.txt` 中列出）
> ⚠️ 注意：由于模型文件较大（超过200MB），未包含在GitHub仓库中，请自行下载。

## 配置说明
主要配置集中在 config.py 和 .env 文件中，请根据实际环境修改：
* config.py：调整服务器端口、数据文件路径、硬件设备URL等。
* .env：存放安全敏感信息，如 INFLUXDB_TOKEN, OPENAI_API_KEY 等。**切勿将此文件提交到公开仓库。**

## API 接口
完整的API接口说明请参见：API_DOCUMENTATION.md。
主要接口包括：
* GET /api/status - 获取系统状态
* GET /api/data - 获取最新传感器数据（自动判别硬件/模拟数据）
* GET/api/history/real - 真实历史数据
* GET/api/history - 历史数据
* GET/api/config - 系统配置
* GET/api/ai/advice - 智能浇水建议
* POST /api/sensor - ［硬件调用］接收传感器数据
* POST /api/water - 手动控制浇水
* POST /api/mode - 切换系统模式（手动/自动）
* POST /api/camera/take - 控制拍照（树莓派）

## 团队成员
- 后端：周佳乐
- 前端：郑淇匀
- 硬件：许隽玮

## 更新日志
- 2026-01-31：创建项目，实现基础API
- 2026-02-06：搭建数据库，开通公网，完善flask框架，增加工具函数watering
- 2026-02-10：接AI
- 2026-02-14：整理文件，初步上传GitHub
- 2026-02-24：上传前端代码，更新README.md
- 2026-02-25：添加硬件代码（Arduino + 树莓派）
