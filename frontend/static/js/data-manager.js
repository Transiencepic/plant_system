// 植物监控系统 - 数据管理器
// 统一管理所有数据的获取和切换

class DataManager {
    // 构造函数 & 初始化 
    constructor() {
        // API配置
        this.useMockAPI = false;  // 开始用模拟数据，后端准备好后改为false
        this.API_BASE = 'https://ratio-kaylie-severally.ngrok-free.dev';  
        // 数据缓存
        this.cache = {
            sensorData: null,
            aiAnalysis: null,
            lastUpdate: null
        };
        // 状态
        this.currentMode = 'manual';  //默认手动模式
        this.isConnected = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        console.log('🌱 数据管理器已初始化（真实模式）');
    }
    
    //获取传感器数据（温度、湿度、土壤湿度）
    async fetchSensorData() {
        try {
            if (this.useMockAPI) {
                return await this.fetchMockSensorData();
            } else {
                return await this.fetchRealSensorData();
            }
        } catch (error) {
            console.error('获取传感器数据失败:', error);
            throw error;
        }
    }
    async fetchRealSensorData() {
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/data`);
    if (!response.ok) throw new Error(`API错误: ${response.status}`);
    
    const result = await response.json();  // result 是外层对象
    const data = result.data;  // ✅ 真正的数据在 result.data 里！
    
    this.cache.sensorData = {
        temperature: data.temperature,
        humidity: data.humidity,
        soil_moisture: data.soil_moisture,
        light_level: data.light_level,
        timestamp: result.timestamp,
        source: result.source
    };
    
    return this.cache.sensorData;
}
    async fetchMockSensorData() {
    // 模拟网络延迟
    await this.delay(300);
    
    // 生成逼真的传感器数据
    const now = new Date();
    const hour = now.getHours();
    
    // 模拟昼夜温度变化
    const baseTemp = 22;
    const dailyVariation = Math.sin(hour * Math.PI / 12) * 4;
    
    // 返回符合新格式的数据
    return {
        temperature: (baseTemp + dailyVariation + (Math.random() - 0.5) * 2).toFixed(1),
        humidity: Math.floor(Math.random() * 15 + 55), // 55-70%
        soil_moisture: Math.floor(Math.random() * 300 + 350), // 350-650
        light_level: Math.floor(Math.random() * 500 + 500), // 添加光照数据
        timestamp: now.toISOString(),
        source: 'mock'
    };
    }

    //控制植物浇水 
    async waterPlant(seconds = 5) {
        try {
            if (this.useMockAPI) {
                return await this.mockWaterPlant(seconds);
            } else {
                return await this.realWaterPlant(seconds);
            }
        } catch (error) {
            console.error('浇水失败:', error);
            throw error;
        }
    }
    async realWaterPlant(seconds = 5) {
        const response = await this.fetchWithNgrok(`${this.API_BASE}/api/water`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ seconds: seconds })
        });
        
        const result = await response.json();
        
        // 检查是否有错误
        if (result.error) {
            throw new Error(result.error);
        }
        
        return result;
    }
    async mockWaterPlant(seconds = 5) {
        // 模拟网络延迟
        await this.delay(800);
        
        // 模拟浇水响应
        const now = new Date();
        
        return {
            action: "watering",
            duration: seconds,
            time: now.toLocaleString(),
            water_today: Math.floor(Math.random() * 10 + seconds), // 模拟今日累计浇水
            new_moisture: Math.floor(Math.random() * 100 + 300), // 模拟新的土壤湿度
            message: `成功浇水 ${seconds} 秒`,
            remaining_today: Math.floor(Math.random() * 20 + 10) // 模拟剩余可浇水量
        };
    }
    /**
    * 基于规则的浇水决策（前端决定是否浇水）
    * @param {Object} sensorData - 传感器数据
    * @returns {Object} 浇水决策结果
    */
    decideWateringByRules(sensorData) {
    const soilMoisture = sensorData.soil_moisture;
    
    // 阈值配置
    const dryThreshold = 700;     // 干燥阈值
    const wetThreshold = 300;     // 过湿阈值
    const optimalMin = 400;       // 适宜下限
    const optimalMax = 600;       // 适宜上限
    
    let shouldWater = false;
    let reason = '';
    let priority = 'low';
    let status = '';
    
    if (soilMoisture > dryThreshold) {
        shouldWater = true;
        reason = '🌵 土壤干燥，急需浇水';
        priority = 'high';
        status = 'dry';
    } else if (soilMoisture > optimalMax) {
        shouldWater = true;
        reason = '💧 土壤偏干，建议适量浇水';
        priority = 'medium';
        status = 'thirsty';
    } else if (soilMoisture >= optimalMin && soilMoisture <= optimalMax) {
        shouldWater = false;
        reason = '🌱 土壤湿度适宜，暂不需要浇水';
        priority = 'low';
        status = 'healthy';
    } else if (soilMoisture < wetThreshold) {
        shouldWater = false;
        reason = '💦 土壤过湿，停止浇水';
        priority = 'high';
        status = 'overwatered';
    } else {
        shouldWater = false;
        reason = '🌿 土壤微湿，暂不需要浇水';
        priority = 'low';
        status = 'moist';
    }
    
    const moisturePercent = config.moistureToPercent(soilMoisture);
    
    return {
        should_water: shouldWater,
        reason: reason,
        priority: priority,
        status: status,
        soil_moisture_raw: soilMoisture,
        soil_moisture_percent: moisturePercent,
        suggested_duration: this.calculateWaterDuration(soilMoisture),
        timestamp: new Date().toISOString(),
        decision_source: 'rule-based'
    };
}
    /**
    * 根据土壤湿度计算浇水时长
    * @param {number} soilMoisture - 土壤湿度原始值
    * @returns {number} 浇水秒数
    */
    calculateWaterDuration(soilMoisture) {
    const dryThreshold = config.thresholds.soil_moisture.dry;
    
    // 越干燥浇水越久
    if (soilMoisture > dryThreshold + 200) {
        return 8; // 非常干燥
    } else if (soilMoisture > dryThreshold) {
        return 6; // 干燥
    } else if (soilMoisture > (dryThreshold + 300) / 2) {
        return 4; // 偏干
    }
    return 3; // 轻微干燥
    }
    
    /**
    * 切换系统模式（手动/自动）
    * @param {string} mode - 'manual' 或 'auto'
    */
    async switchSystemMode(mode) {
    try {
        if (this.useMockAPI) {
            return await this.mockSwitchMode(mode);
        } else {
            return await this.realSwitchMode(mode);
        }
    } catch (error) {
        console.error('切换模式失败:', error);
        throw error;
    }
    }
    async realSwitchMode(mode) {
    // 验证模式参数
    if (mode !== 'manual' && mode !== 'auto') {
        throw new Error('模式必须是 "manual" 或 "auto"');
    }
    
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/mode`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: mode })
    });
    
    const result = await response.json();
    
    // 检查是否有错误
    if (result.error) {
        throw new Error(result.error);
    }
    
    return result;
    }
    async mockSwitchMode(mode) {
    await this.delay(500);
    
    if (mode !== 'manual' && mode !== 'auto') {
        throw new Error('模式必须是 "manual" 或 "auto"');
    }
    
    // 模拟当前模式
    const oldMode = this.currentMode || 'manual';
    this.currentMode = mode;  // 保存当前模式
    
    return {
        success: true,
        message: `系统模式已从 ${oldMode} 切换为 ${mode}`,
        old_mode: oldMode,
        new_mode: mode,
        auto_config: mode === 'auto' ? {
            water_threshold: 300,
            water_duration: 5,
            check_interval: 300
        } : null,
        timestamp: new Date().toLocaleString()
    };
    }

    //拍照功能
    async takePhoto() {
        try {
            if (this.useMockAPI) {
                return await this.mockTakePhoto();
            } else {
                return await this.realTakePhoto();
            }
        } catch (error) {
            console.error('拍照失败:', error);
            return await this.mockTakePhoto();
        }
    }
    async realTakePhoto() {
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/camera/take`, {  // ✅ 新URL
        method: 'POST',  // ✅ 改为POST
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) throw new Error(`拍照API错误: ${response.status}`);
    
    const result = await response.json();
    
    return {
        success: result.success,
        message: result.message,
        filename: result.image_path,  // ✅ 注意字段名是 image_path
        timestamp: result.timestamp,
        source: 'real'
    };
    }
    async mockTakePhoto() {
    await this.delay(1000);
    
    return {
        success: true,
        message: '拍照成功',
        filename: `data/images/plant_${Date.now()}.jpg`,  // ✅ 匹配真实API格式
        timestamp: new Date().toLocaleString(),
        source: 'mock'
    };
    }
    async takePhotoWithTimeout(timeoutMs = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    
    try {
        const response = await this.fetchWithNgrok(`${this.API_BASE}/api/camera/take`, {
            method: 'POST',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`拍照失败: ${response.status}`);
        }
        
        return await response.json();
        
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('拍照超时，请重试');
        }
        throw error;
    }
    }// 在 DataManager 类中添加

    /**
     * 获取图表历史数据
     * @param {string} range - 'hour'/'day'/'week'
     */
    async fetchChartData(range = 'day') {
        try {
            if (this.useMockAPI) {
                return await this.fetchMockChartData(range);
            } else {
                return await this.fetchRealChartData(range);
            }
        } catch (error) {
            console.error('获取图表数据失败:', error);
            return await this.fetchMockChartData(range);
        }
    }
    async fetchRealChartData(range = 'day') {
    // 注意：API文档中历史数据接口是 GET /api/history
    // 没有range参数，直接返回最近12小时数据
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/history/real?hours=24`);
    if (!response.ok) throw new Error(`历史数据API错误: ${response.status}`);
    
    const result = await response.json();
    
    // 转换格式：从后端格式转为我们图表需要的格式
    if (result.data && Array.isArray(result.data)) {
        return {
            // 把完整时间转成 "13:00" 格式
            labels: result.data.map(item => {
                const timeStr = item.time.split(' ')[1].substring(0, 5);
                return timeStr;
            }),
            temperature: result.data.map(item => item.temperature),
            humidity: result.data.map(item => item.humidity),
            soil_moisture: result.data.map(item => item.moisture),  // 注意字段名是 moisture
            light: result.data.map(item => item.light || 0)
        };
    }
    
    throw new Error('历史数据格式错误');
    }
    async fetchMockChartData(range = 'day') {
    await this.delay(200);
    
    // 模拟返回与真实API相同的格式
    const now = new Date();
    const dataPoints = 12; // 模拟12个数据点
    
    const labels = [];
    const temperature = [];
    const humidity = [];
    const soil_moisture = [];
    const light = [];
    
    for (let i = dataPoints - 1; i >= 0; i--) {
        const time = new Date(now - i * 3600000);
        labels.push(time.getHours().toString().padStart(2, '0') + ':00');
        
        temperature.push((20 + Math.sin(i * Math.PI / 6) * 5 + Math.random() * 2).toFixed(1));
        humidity.push(Math.floor(50 + Math.random() * 20));
        soil_moisture.push(Math.floor(300 + Math.random() * 400));
        light.push(Math.floor(Math.random() * 500 + 500));
    }
    
    return {
        labels,
        temperature,
        humidity,
        soil_moisture,
        light
    };
    }

    //获取AI分析结果
    async fetchRealAIAnalysis() {
    try {
        const formData = new FormData();  // 创建空的 FormData
        // 不传 image 参数，后端会使用最新拍摄的照片
        
        const response = await this.fetchWithNgrok(`${this.API_BASE}/api/disease/detect`, {
            method: 'POST',
            body: formData,  // ✅ 发送 FormData
            // 不要设置 Content-Type 头！
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('病害检测API错误响应:', errorText);
            throw new Error(`病害检测API错误: ${response.status}`);
        }
        
        const data = await response.json();
        this.cache.aiAnalysis = data;
        
        return data;
        
    } catch (error) {
        console.error('调用病害检测API失败:', error);
        throw error;
    }
    }
    async fetchMockAIAnalysis() {
    await this.delay(800);  // 模拟网络延迟
    
    // 模拟病害检测响应（完全匹配API文档格式）
    const diseases = [
        {
            disease_name: '健康',
            confidence: 'high',
            treatment: '无需治疗',
            prevention: '保持当前养护方式'
        },
        {
            disease_name: '番茄早疫病',
            confidence: 'high',
            treatment: '使用代森锰锌或百菌清，每隔7-10天喷施一次',
            prevention: '避免叶片潮湿，保持通风，轮作非茄科作物'
        },
        {
            disease_name: '番茄晚疫病',
            confidence: 'high',
            treatment: '使用霜脲氰或烯酰吗啉，每7天喷施一次',
            prevention: '控制湿度，避免叶片积水'
        },
        {
            disease_name: '未知病害',
            confidence: 'low',
            treatment: '暂无治疗方案',
            prevention: '暂无预防措施'
        }
    ];
    
    const randomDisease = diseases[Math.floor(Math.random() * diseases.length)];
    
    return {
        success: true,
        message: '病害检测完成',
        disease_name: randomDisease.disease_name,
        confidence: randomDisease.confidence,
        treatment: randomDisease.treatment,
        prevention: randomDisease.prevention,
        image: `plant_${Date.now()}.jpg`,
        timestamp: new Date().toLocaleString()
    };
    }

    // 配置方法
    async fetchSystemConfig() {
    try {
        if (this.useMockAPI) {
            return await this.fetchMockConfig();
        } else {
            return await this.fetchRealConfig();
        }
    } catch (error) {
        console.error('获取配置失败:', error);
        return await this.fetchMockConfig();
    }
    }
    async fetchRealConfig() {
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/config`);
    if (!response.ok) throw new Error(`配置API错误: ${response.status}`);
    
    return await response.json();
    }
    async fetchMockConfig() {
    await this.delay(300);
    
    return {
        system: {
            name: "智能植物养护系统",
            version: "1.0.0",
            author: "周佳乐，许隽玮，郑淇匀",
            debug: true
        },
        server: {
            host: "0.0.0.0",
            port: 5000,
            timeout: 30
        },
        data: {
            save_interval: 300,
            history_days: 7,
            data_file: "data/sensor_data.json",
            log_file: "system.log"
        },
        hardware: {
            serial_port: "/dev/ttyACM0",
            baud_rate: 9600,
            camera_port: 0
        },
        plant: {
            auto_water_threshold: 300,
            water_duration: 5,
            max_water_per_day: 30,
            check_interval: 300
        },
        current_mode: "manual",
        current_data_file: "data/sensor_data.json"
    };
    }

    // 状态方法
    async fetchSystemStatus() {
    try {
        if (this.useMockAPI) {
            return await this.fetchMockStatus();
        } else {
            return await this.fetchRealStatus();
        }
    } catch (error) {
        console.error('获取系统状态失败:', error);
        return await this.fetchMockStatus();
    }
    }
    async fetchRealStatus() {
    const response = await this.fetchWithNgrok(`${this.API_BASE}/api/status`);
    if (!response.ok) throw new Error(`状态API错误: ${response.status}`);
    
    return await response.json();
    }
    async fetchMockStatus() {
    await this.delay(200);
    
    return {
        system: "智能植物养护系统",
        status: "running",
        mode: "manual",
        uptime: new Date().toLocaleString(),
        hardware: "waiting",
        version: "1.0.0",
        water_today: 0,
        last_watered: null
    };
    }
    
    //浇水建议模块
    async getWateringAdvice() {
    try {
        // 先获取最新传感器数据
        const sensorData = await this.fetchSensorData();
        
        // 基于规则决策
        const decision = this.decideWateringByRules(sensorData);
        
        return {
            success: true,
            timestamp: new Date().toLocaleString(),
            sensor_data: sensorData,
            advice: decision,
            ai_analysis: null // 这里不包含AI分析，AI只做病害
        };
    } catch (error) {
        console.error('获取浇水建议失败:', error);
        // 返回默认决策
        return {
            success: false,
            advice: {
                should_water: false,
                reason: '无法获取传感器数据',
                priority: 'low'
            }
        };
    }
    }
    //工具方法   
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    toggleAPIMode(useMock) {
        this.useMockAPI = useMock;
        console.log(`切换到 ${useMock ? '模拟' : '真实'} API模式`);
        return this.useMockAPI;
    }
    async testConnection() {
        try {
            if (this.useMockAPI) {
                return { connected: true, mode: 'mock', latency: 50 };
            }
            
            const startTime = Date.now();
            
            // 使用AbortController实现超时
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            
            const response = await this.fetchWithNgrok(`${this.API_BASE}/health`, { 
                method: 'HEAD',
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            const latency = Date.now() - startTime;
            
            this.isConnected = response.ok;
            return { 
                connected: response.ok, 
                mode: 'real', 
                latency,
                status: response.status 
            };
            
        } catch (error) {
            this.isConnected = false;
            return { 
                connected: false, 
                mode: this.useMockAPI ? 'mock' : 'real',
                error: error.message 
            };
        }
    }//测试API连接
    formatSensorData(data) {
        if (!data) return null;
        
        return {
            temperature: {
                value: data.temperature,
                unit: '°C',
                status: config.getTemperatureStatus(parseFloat(data.temperature))
            },
            humidity: {
                value: data.humidity,
                unit: '%',
                status: config.getStatusForValue('humidity', parseInt(data.humidity))
            },
            soil_moisture: {
                // 注意：原始值是模拟值，转换为百分比显示
                raw: data.soil_moisture,
                value: config.moistureToPercent(data.soil_moisture),
                unit: '%',
                status: config.getMoistureStatus(data.soil_moisture)
            },
            timestamp: data.timestamp,
            source: data.source || 'unknown'
        };
    }// 格式化数据用于显示
    validateSensorData(data) {
        const required = ['temperature', 'humidity', 'soil_moisture'];
        return required.every(key => 
            key in data && data[key] !== null && data[key] !== undefined
        );
    } // 数据验证
    async fetchWithNgrok(url, options = {}) {
    const headers = {
        'ngrok-skip-browser-warning': 'true',
        ...options.headers
    };
    return fetch(url, { ...options, headers });
    }
}

console.log('🌱 数据管理器加载完成');
window.dataManager = new DataManager();