// ========================================
// 植物监控系统 - 模拟API服务器
// 用于前端开发，模拟真实后端API
// ========================================

class MockAPI {
    //构造函数&初始化
    constructor() {
        // 模拟数据库
        this.database = {
            sensor_data: [],
            images: [],
            ai_analysis: []
        };
        
        // 初始化模拟数据
        this.initMockData();
        
        console.log('🌐 模拟API服务器已启动');
    }
    initMockData() {
        // 生成过去24小时的模拟数据
        const now = new Date();
        for (let i = 24; i >= 0; i--) {
            const time = new Date(now - i * 3600000);
            this.database.sensor_data.push({
                timestamp: time.toISOString(),
                temperature: (20 + Math.sin(i * Math.PI / 12) * 5 + Math.random() * 2).toFixed(1),
                humidity: (50 + Math.random() * 20).toFixed(0),
                soil_moisture: Math.floor(300 + Math.random() * 400),
                light_level: Math.floor(Math.random() * 100)
            });
        }
        
        // 模拟AI分析记录
        this.database.ai_analysis = [
            {
                id: 1,
                timestamp: now.toISOString(),
                status: 'healthy',
                confidence: 0.92,
                details: {
                    plant_health: '良好',
                    leaf_color: '正常',
                    growth_stage: '生长期',
                    issues: [],
                    recommendations: ['继续保持当前养护']
                }
            }
        ];
        
        // 模拟图像记录
        this.database.images = [
            {
                id: 1,
                filename: 'plant_001.jpg',
                timestamp: now.toISOString(),
                url: 'https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=植物图像',
                analysis: {
                    detected: true,
                    health_score: 85,
                    anomalies: []
                }
            }
        ];
    }
    
    // ========== API端点模拟 ==========
    async getSensorData(params = {}) {
        await this.delay(200);
        
        const range = params.range || 'latest';
        let responseData;
        
        if (range === 'latest') {
            // 返回最新数据
            responseData = this.database.sensor_data[this.database.sensor_data.length - 1];
        } else {
            // 返回指定范围的数据
            const hours = {
                hour: 1,
                day: 24,
                week: 168
            }[range] || 24;
            
            const cutoff = new Date(Date.now() - hours * 3600000);
            responseData = this.database.sensor_data.filter(
                data => new Date(data.timestamp) > cutoff
            );
        }
        
        return {
            success: true,
            data: responseData,
            timestamp: new Date().toISOString()
        };
    }
    async captureImage() {
        await this.delay(800); // 模拟拍照延迟
        
        const timestamp = new Date();
        const imageId = this.database.images.length + 1;
        
        const newImage = {
            id: imageId,
            filename: `plant_${timestamp.getTime()}.jpg`,
            timestamp: timestamp.toISOString(),
            url: `https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=拍照+${timestamp.getHours()}:${timestamp.getMinutes()}`,
            analysis: {
                detected: Math.random() > 0.1,
                health_score: Math.floor(Math.random() * 30 + 70),
                anomalies: Math.random() > 0.7 ? ['叶片轻微发黄'] : []
            }
        };
        
        this.database.images.unshift(newImage);
        
        return {
            success: true,
            message: '照片拍摄成功',
            image: newImage
        };
    }
    async getAIAnalysis() {
    await this.delay(500);
    
    // 模拟病害检测响应 - 完全按照API文档格式
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
    
    const random = diseases[Math.floor(Math.random() * diseases.length)];
    
    return {
        success: true,
        message: '病害检测完成',
        disease_name: random.disease_name,
        confidence: random.confidence,
        treatment: random.treatment,
        prevention: random.prevention,
        image: `plant_${Date.now()}.jpg`,
        timestamp: new Date().toLocaleString()
    };
    }
    async getHistoryData(type, range = 'day') {
        await this.delay(300);
        
        const hours = {
            hour: 1,
            day: 24,
            week: 168
        }[range] || 24;
        
        const cutoff = new Date(Date.now() - hours * 3600000);
        const filteredData = this.database.sensor_data.filter(
            data => new Date(data.timestamp) > cutoff
        );
        
        return {
            success: true,
            type: type,
            range: range,
            data: filteredData.map(item => ({
                time: new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                value: item[type]
            })),
            statistics: {
                average: this.calcAverage(filteredData.map(d => parseFloat(d[type]))),
                min: Math.min(...filteredData.map(d => parseFloat(d[type]))),
                max: Math.max(...filteredData.map(d => parseFloat(d[type]))),
                latest: filteredData[filteredData.length - 1][type]
            }
        };
    }
    
    // ========== 工具方法 ==========
    calcAverage(arr) {
        const sum = arr.reduce((a, b) => a + b, 0);
        return (sum / arr.length).toFixed(2);
    }
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    } 
    createResponse(data, error = null) {
        return {
            success: !error,
            data: data,
            error: error,
            server_time: new Date().toISOString(),
            version: '1.0.0-mock'
        };
    }// 模拟真实API响应格式
}

// ========================================
// 模拟Express风格的路由
// ========================================
window.mockAPI = {
    server: new MockAPI(),
    
    async get(endpoint, params = {}) {
        console.log(`[MockAPI] GET ${endpoint}`, params);
        
        try {
            let response;
            
            switch(endpoint) {
                case '/api/sensor-data':
                    response = await this.server.getSensorData(params);
                    break;
                    
                case '/api/capture':
                    response = await this.server.captureImage();
                    break;
                    
                case '/api/ai-analysis':
                    response = await this.server.getAIAnalysis();
                    break;
                    
                case '/api/temperature-history':
                    response = await this.server.getHistoryData('temperature', params.range);
                    break;
                    
                case '/api/moisture-history':
                    response = await this.server.getHistoryData('soil_moisture', params.range);
                    break;
                    
                case '/health':
                    response = {
                        success: true,
                        status: 'healthy',
                        uptime: Date.now(),
                        version: 'mock-1.0.0'
                    };
                    break;
                    
                default:
                    response = {
                        success: false,
                        error: `Endpoint ${endpoint} not found`
                    };
            }
            
            return this.server.createResponse(response.data, response.error);
            
        } catch (error) {
            console.error(`[MockAPI] Error in ${endpoint}:`, error);
            return this.server.createResponse(null, error.message);
        }
    }
};

// 拦截fetch请求（如果data-manager使用模拟模式）
const originalFetch = window.fetch;
window.fetch = async function(url, options = {}) {
    const mockMode = window.dataManager && window.dataManager.useMockAPI;
    const isOurAPI = url.includes('/api/');
    
    if (mockMode && isOurAPI) {
        console.log(`[MockAPI] 拦截请求: ${url}`);
        
        // 解析URL
        const urlObj = new URL(url, window.location.origin);
        const endpoint = urlObj.pathname;
        const params = Object.fromEntries(urlObj.searchParams.entries());
        
        // 调用模拟API
        const response = await mockAPI.get(endpoint, params);
        
        // 返回模拟响应
        return Promise.resolve({
            ok: response.success,
            status: response.success ? 200 : 404,
            json: async () => response,
            text: async () => JSON.stringify(response)
        });
    }
    
    // 否则使用原始fetch
    return originalFetch.call(this, url, options);
};

console.log('🌐 模拟API加载完成（已拦截fetch请求）');