// ========================================
// 植物监控系统 - UI组件库
// 提供可重用的UI组件
// ========================================

class UIComponents {
    constructor() {
        console.log('🎨 UI组件库已加载');
    }

    // ========== 传感器卡片组件 ==========  
    /**
     * 创建传感器卡片
     * @param {string} title - 卡片标题
     * @param {string} icon - 图标
     * @param {string} value - 数值
     * @param {string} unit - 单位
     * @param {string} status - 状态文本
     * @param {string} statusColor - 状态颜色
     * @returns {HTMLElement} 卡片元素
     */
    createSensorCard({ title, icon, value, unit, status, statusColor = '#4CAF50' }) {
        const card = document.createElement('div');
        card.className = 'sensor-card';
        card.innerHTML = `
            <div class="sensor-header">
                <h3>${icon} ${title}</h3>
                <span class="sensor-time">刚刚更新</span>
            </div>
            <div class="sensor-data">
                <span class="data-value">${value}</span>
                <span class="data-unit">${unit}</span>
            </div>
            <div class="sensor-status">
                <span class="status-badge" style="background: ${statusColor}22; color: ${statusColor};">
                    ${status}
                </span>
            </div>
            <div class="sensor-footer">
                <span class="trend-icon">↗️</span>
                <small>与上一小时对比</small>
            </div>
        `;
        
        // 添加点击事件
        card.addEventListener('click', () => {
            console.log(`${title} 卡片被点击，值: ${value}${unit}`);
        });
        
        return card;
    }

    // ========== 状态指示灯组件 ==========
    /**
     * 创建状态指示灯
     * @param {string} status - 状态: 'good'/'warning'/'danger'
     * @param {string} label - 标签文本
     * @returns {HTMLElement}
     */
    createStatusIndicator(status, label = '状态') {
        const indicator = document.createElement('div');
        indicator.className = 'status-indicator';
        
        const statusMap = {
            good: { color: '#4CAF50', icon: '●' },
            warning: { color: '#FF9800', icon: '⚠️' },
            danger: { color: '#F44336', icon: '❗' },
            normal: { color: '#2196F3', icon: '○' }
        };
        
        const statusInfo = statusMap[status] || statusMap.normal;
        
        indicator.innerHTML = `
            <div class="status-light" style="background: ${statusInfo.color}"></div>
            <span class="status-label">${label}</span>
            <span class="status-icon">${statusInfo.icon}</span>
        `;
        
        return indicator;
    }

    // ========== 通知组件 ==========
    /**
     * 显示通知消息
     * @param {string} message - 消息内容
     * @param {string} type - 类型: 'info'/'success'/'warning'/'error'
     * @param {number} duration - 显示时间(毫秒)，0表示不自动关闭
     */
    showNotification(message, type = 'info', duration = 3000) {
        // 移除现有通知
        const existing = document.querySelector('.ui-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = `ui-notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => notification.classList.add('show'), 10);
        
        // 自动关闭
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
        
        return notification;
    }
    getNotificationIcon(type) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        return icons[type] || icons.info;
    }

    // ========== 加载动画组件 ==========
    /**
     * 显示加载动画
     * @param {string} text - 加载文本
     * @returns {HTMLElement} 加载器元素
     */
    showLoader(text = '加载中...') {
        this.hideLoader(); // 先移除现有的
        
        const loader = document.createElement('div');
        loader.className = 'ui-loader';
        loader.innerHTML = `
            <div class="loader-spinner"></div>
            <div class="loader-text">${text}</div>
        `;
        
        document.body.appendChild(loader);
        return loader;
    }
    hideLoader() {
        const loader = document.querySelector('.ui-loader');
        if (loader) loader.remove();
    }

    // ========== 模态框组件 ==========
    /**
     * 显示模态框
     * @param {string} title - 标题
     * @param {string} content - 内容HTML
     * @param {Object} buttons - 按钮配置
     * @returns {HTMLElement} 模态框元素
     */
    showModal(title, content, buttons = {}) {
        this.hideModal(); // 先移除现有的
        
        const modal = document.createElement('div');
        modal.className = 'ui-modal';
        
        const buttonsHTML = Object.entries(buttons).map(([text, action]) => 
            `<button onclick="${action}">${text}</button>`
        ).join('');
        
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="window.ui.hideModal()">×</button>
                </div>
                <div class="modal-body">${content}</div>
                ${buttonsHTML ? `<div class="modal-footer">${buttonsHTML}</div>` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // ESC键关闭
        const escHandler = (e) => {
            if (e.key === 'Escape') this.hideModal();
        };
        modal._escHandler = escHandler;
        document.addEventListener('keydown', escHandler);
        
        return modal;
    }
    hideModal() {
        const modal = document.querySelector('.ui-modal');
        if (modal) {
            document.removeEventListener('keydown', modal._escHandler);
            modal.remove();
        }
    }

    // ========== 图表控制组件 ==========  
    /**
     * 创建图表时间范围选择器
     * @param {string} currentRange - 当前选择范围
     * @param {Function} onChange - 改变回调
     * @returns {HTMLElement}
     */
    createChartRangeSelector(currentRange = 'day', onChange) {
        const selector = document.createElement('div');
        selector.className = 'chart-range-selector';
        
        const ranges = [
            { id: 'hour', label: '1小时', icon: '🕐' },
            { id: 'day', label: '24小时', icon: '📅' },
            { id: 'week', label: '一周', icon: '📆' }
        ];
        
        selector.innerHTML = ranges.map(range => `
            <button 
                class="range-btn ${range.id === currentRange ? 'active' : ''}"
                onclick="this.parentElement.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active')); 
                         this.classList.add('active'); 
                         ${onChange ? `(${onChange.toString()})('${range.id}')` : ''}"
            >
                ${range.icon} ${range.label}
            </button>
        `).join('');
        
        return selector;
    }

    // ========== 植物图像卡片组件 ==========
    /**
     * 更新植物图像显示
     * @param {string} imageUrl - 图片URL
     * @param {string} caption - 图片说明
     */
    updatePlantImage(imageUrl, caption = '最新拍摄') {
        const imageSection = document.querySelector('.sensor-card:nth-child(3)');
        if (!imageSection) return;
        
        const timestamp = new Date().toLocaleTimeString();
        imageSection.innerHTML = `
            <h2 class="sensor-title">📸 植物图像</h2>
            <div class="plant-image-container">
                <div class="image-wrapper">
                    <img src="${imageUrl}" alt="植物图像" 
                         onerror="this.src='https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=图像加载失败'">
                    <div class="image-caption">
                        <span>${caption}</span>
                        <small>${timestamp}</small>
                    </div>
                </div>
                <button onclick="takePhoto()" class="photo-btn">
                    📷 拍摄新照片
                </button>
                <div class="image-controls">
                    <button onclick="this.parentElement.querySelector('img').classList.toggle('zoom')">
                    🔍 放大
                    </button>
                    <button onclick="shareImage('${imageUrl}')">
                    ↗️ 分享
                    </button>
                </div>
            </div>
        `;
    }
}

// ========================================
// 创建全局实例
// ========================================
window.ui = new UIComponents();

console.log('🎨 UI组件库加载完成');