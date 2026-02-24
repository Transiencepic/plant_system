// ========================================
// 植物监控系统 - 精简配置文件
// 根据实际硬件(DHT11温度+土壤湿度+摄像头)调整
// ========================================
const PlantMonitorConfig = {
    // ========== 传感器阈值配置 ==========
    thresholds: {
        // DHT11温度传感器范围（根据植物类型调整）
        temperature: {
            min: 15,        // 最低安全温度(°C) - 热带植物
            max: 35,        // 最高安全温度(°C) - DHT11最高测50°C
            optimal: [16, 28], // 大多数室内植物适宜温度
            unit: '°C'
        },
        // 土壤湿度传感器（模拟值，需要校准）
        soil_moisture: {
            // 注意：这是模拟电压值(0-1023)，不是百分比！
            dry: 700,       // 高于此值表示干燥（需要浇水）
            wet: 300,       // 低于此值表示过湿
            optimal: [400, 600], // 适宜范围
            unit: 'RAW'     // 原始模拟值
        },
        // DHT11湿度传感器
        humidity: {
            min: 30,        // 最低空气湿度(%)
            max: 85,        // 最高空气湿度(%)
            optimal: [40, 70], // 室内植物适宜湿度
            unit: '%'
        }
    },

    // ========== 颜色配置 ==========
    colors: {
        healthy: '#4CAF50',     // 健康 - 绿色
        thirsty: '#2196F3',     // 缺水 - 蓝色
        dry: '#FF9800',         // 干燥 - 橙色
        overwatered: '#03A9F4', // 过湿 - 浅蓝
        hot: '#F44336',         // 过热 - 红色
        cold: '#00BCD4',        // 过冷 - 青色
        warning: '#FF9800',     // 警告
        danger: '#F44336'       // 危险
    },

    // ========== 时间间隔配置（毫秒） ==========
    intervals: {
        sensorUpdate: 10000,     // 传感器数据更新：10秒（模仿开源项目）
        chartUpdate: 30000,      // 图表更新：30秒
        cameraCapture: 3600000,  // 摄像头拍照：1小时（开源项目设置）
        aiAnalysisUpdate: 300000 // AI分析更新：5分钟
    },

    // ========== API端点配置 ==========
    apiEndpoints: {
    sensorData: '/api/data',              // 根据API文档，真实接口是/api/data
    captureImage: '/api/camera/take',     // 根据API文档，拍照接口
    diseaseDetect: '/api/disease/detect',    // 改成病害检测接口
    moistureHistory: '/api/history/real', // 根据API文档
    temperatureHistory: '/api/history/real'
    },

    // ========== 植物类型预设 ==========
    // 可以扩展支持不同植物
    plantPresets: {
    default: {
        name: '通用室内植物',
        temperature: { min: 18, max: 28 },
        soilMoisture: { dry: 700, wet: 300 },
        humidity: { min: 40, max: 70 }
    },
    succulent: {
        name: '多肉植物',
        temperature: { min: 15, max: 35 },
        soilMoisture: { dry: 800, wet: 400 },
        humidity: { min: 30, max: 50 }
    },
    tropical: {
        name: '热带植物',
        temperature: { min: 20, max: 32 },
        soilMoisture: { dry: 600, wet: 250 },
        humidity: { min: 60, max: 85 }
    }
},

    // ========== 当前设置 ==========
    currentSettings: {
        plantType: 'default',      // 当前植物类型
        enableAI: true,            // 启用AI分析
        enableAutoCapture: true,   // 自动拍照
        notificationLevel: 'all'   // 通知级别：all/warning/off
    }
};

// ========================================
// 辅助函数 - 针对土壤湿度传感器的特殊处理
// ========================================
// DHT11温度状态判断
PlantMonitorConfig.getTemperatureStatus = function(value) {
    const t = this.thresholds.temperature;
    if (value < t.min) return { status: 'cold', level: 'danger' };
    if (value > t.max) return { status: 'hot', level: 'danger' };
    if (value >= t.optimal[0] && value <= t.optimal[1]) {
        return { status: 'healthy', level: 'good' };
    }
    return { status: 'warning', level: 'warning' };
};
// 土壤湿度状态判断（模拟值转义）
PlantMonitorConfig.getMoistureStatus = function(rawValue) {
    const m = this.thresholds.soil_moisture;
    if (rawValue > m.dry) return { status: 'dry', level: 'danger' };
    if (rawValue < m.wet) return { status: 'overwatered', level: 'danger' };
    if (rawValue >= m.optimal[0] && rawValue <= m.optimal[1]) {
        return { status: 'healthy', level: 'good' };
    }
    return { status: 'thirsty', level: 'warning' };
};
// 转换为百分比显示（用于UI，非真实值）
PlantMonitorConfig.moistureToPercent = function(rawValue) {
    const m = this.thresholds.soil_moisture;
    // 将模拟值映射到0-100%显示
    const percent = 100 - ((rawValue - m.wet) / (m.dry - m.wet)) * 100;
    return Math.max(0, Math.min(100, Math.round(percent)));
};
// 获取状态的颜色（data-manager.js需要）
PlantMonitorConfig.getStatusForValue = function(sensorType, value) {
    if (sensorType === 'temperature') {
        const status = this.getTemperatureStatus(parseFloat(value));
        return status.level; // 返回 'good'/'warning'/'danger'
    }
    if (sensorType === 'humidity') {
        const val = parseInt(value);
        if (val < this.thresholds.humidity.min || val > this.thresholds.humidity.max) {
            return 'danger';
        }
        if (val >= this.thresholds.humidity.optimal[0] && val <= this.thresholds.humidity.optimal[1]) {
            return 'good';
        }
        return 'warning';
    }
    return 'normal';
};
// 根据状态等级获取颜色（data-manager.js需要）
PlantMonitorConfig.getColorForStatus = function(status) {
    // 映射状态等级到颜色
    const colorMap = {
        'good': this.colors.healthy,
        'warning': this.colors.warning,
        'danger': this.colors.danger,
        'normal': this.colors.normal
    };
    return colorMap[status] || this.colors.normal;
};
// 获取摄像头图片URL（模仿开源项目格式）
PlantMonitorConfig.getCameraImageUrl = function() {
    const timestamp = new Date().getTime();
    return `/api/capture?t=${timestamp}`; // 防止缓存
};

// ========================================
// 暴露给全局使用
// ========================================
window.config = PlantMonitorConfig;

console.log('🌱 智能植物监控系统配置已加载 - 适配DHT11+土壤湿度+摄像头');
