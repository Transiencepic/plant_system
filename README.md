\# 🌱 智能植物养护系统 - 后端服务



\## 项目说明

这是一个为智能植物养护项目提供数据存储、API接口和设备控制的核心后端服务。基于 Flask + InfluxDB + Ngrok 构建。



\## 快速开始



\### 前提条件

\*   Python 3.9+

\*   ［待硬件就绪］树莓派（拍照、浇水控制）



\### 安装依赖

```bash

pip install -r requirements.txt
```


\### 2. 启动所有服务（按顺序）

1\.启动数据库

2\.启动后端API

3\.启动公网隧道（供队友访问）



\### 3. 访问服务

\- 首页：http://localhost:5000

\- API文档：http://localhost:5000/



\## 📁项目结构

plant\_system/

├── app.py                 # Flask应用主文件，所有API路由定义

├── config.py              # 系统唯一配置文件（服务器、数据库、硬件地址等）

├── requirements.txt       # Python依赖包列表

├── .env                   # 敏感环境变量（数据库令牌、API密钥等，请勿上传）

├── README.md              # 本文档

├── API\_DOCUMENTATION.md             # 详细的API接口文档

├── data/                  # 本地模拟数据存储目录

│   ├── images

├── db\_client.py       # InfluxDB数据库客户端（读写传感器数据）

├── tools/                 # 核心工具函数目录

│   ├── ai_advisor.py

│   ├── disease_detector.py

│   └── watering.py        # 浇水控制模块（调用硬件设备）

└── \[待添加]...            



\## ⚙️ 配置说明

主要配置集中在 config.py 和 .env 文件中，请根据实际环境修改：

* config.py：调整服务器端口、数据文件路径、硬件设备URL等。
* .env：存放安全敏感信息，如 INFLUXDB\_TOKEN, OPENAI\_API\_KEY 等。\*\*切勿将此文件提交到公开仓库。\*\*



\## 📡 API 接口

完整的API接口说明请参见：API\_DOCUMENTATION.md。

主要接口包括：

* GET /api/status - 获取系统状态
* GET /api/data - 获取最新传感器数据（自动判别硬件/模拟数据）
* GET/api/history/real - 真实历史数据
* GET/api/history - 历史数据
* GET/api/config - 系统配置
* GET/api/ai/advice - 🌱 智能浇水建议
* POST /api/sensor - ［硬件调用］接收传感器数据
* POST /api/water - 手动控制浇水
* POST /api/mode - 切换系统模式（手动/自动）
* POST /api/camera/take - 控制拍照（树莓派）



\## 👥团队成员

\- 后端：周佳乐

\- 硬件：许隽玮

\- 前端：郑淇匀



\## 更新日志

\- 2026-01-31：创建项目，实现基础API

\- 2026-02-06：搭建数据库，开通公网，完善flask框架，增加工具函数watering

\- 2026-02-10：接AI
