# tools/ai_advisor.py
"""
智能浇水决策工具（规则引擎版）
后期可升级为真正的AI模型
"""

import datetime
from config import PLANT_CONFIG  # 从统一配置中心导入
import datetime

class PlantAdvisor:
    """植物养护建议器（规则引擎版）"""
    
    def __init__(self):
        self.config = PLANT_CONFIG
        self.version = "1.0 (规则引擎)"
    
    def should_water_now(self, soil_moisture, temperature, humidity):
        """
        判断当前是否需要浇水（规则引擎）
        
        返回:
            (should_water: bool, score: int, reasons: list)
        """
        current_time = datetime.datetime.now()
        score = 0
        reasons = []
        
        # ========== 规则1：土壤湿度（主要因素） ==========
        threshold = self.config["auto_water_threshold"]
        
        if soil_moisture > 600:
            score += 80
            reasons.append(f"🚨 土壤严重干旱 ({soil_moisture})")
        elif soil_moisture > 450:
            score += 60
            reasons.append(f"⚠️ 土壤干燥 ({soil_moisture})")
        elif soil_moisture > threshold:
            score += 40
            reasons.append(f"🌵 土壤略干 ({soil_moisture} > {threshold})")
        else:
            score -= 20
            reasons.append(f"💧 土壤湿润 ({soil_moisture} ≤ {threshold})")
        
        # ========== 规则2：温度因素 ==========
        if temperature > 30:
            score += 30
            reasons.append(f"🔥 高温 ({temperature}°C)")
        elif temperature > 25:
            score += 15
            reasons.append(f"☀️ 温暖 ({temperature}°C)")
        elif temperature < 15:
            score -= 10
            reasons.append(f"❄️ 低温 ({temperature}°C)")
        
        # ========== 规则3：湿度因素 ==========
        if humidity < 40:
            score += 20
            reasons.append(f"💨 空气干燥 ({humidity}%)")
        elif humidity < 60:
            score += 10
            reasons.append(f"🌤️ 湿度适中 ({humidity}%)")
        else:
            score -= 5
            reasons.append(f"🌫️ 空气潮湿 ({humidity}%)")
        
        # ========== 规则4：时间因素 ==========
        hour = current_time.hour
        if 22 <= hour <= 23 or 0 <= hour < 6:
            score -= 30
            reasons.append(f"🌙 夜间 ({hour:02d}:00，避免浇水)")
        elif 12 <= hour <= 16:
            score += 10
            reasons.append(f"🌞 最佳浇水时间 ({hour:02d}:00)")
        
        # ========== 最终决策 ==========
        should_water = score >= 60
        
        return should_water, score, reasons
    
    def get_advice(self, soil_moisture, temperature, humidity):
        """
        获取完整的浇水建议
        
        返回:
            dict: 建议详情
        """
        should_water, score, reasons = self.should_water_now(
            soil_moisture, temperature, humidity
        )
        
        # 建议浇水量（基于土壤干燥程度）
        base = self.config["water_duration"]
        if soil_moisture > 600:
            duration = base * 2  # 严重干旱，加倍
        elif soil_moisture > 450:
            duration = int(base * 1.5)  # 干燥，加50%
        else:
            duration = base
        
        # 限制最大浇水量
        max_daily = self.config["max_water_per_day"]
        if duration > max_daily:
            duration = max_daily
            reasons.append(f"📊 调整浇水量至每日上限 {max_daily}秒")
        
        # 植物状态评估
        if soil_moisture < 250:
            status = "过湿💧"
        elif soil_moisture < 400:
            status = "健康🌱"
        elif soil_moisture < 550:
            status = "略干🍂"
        else:
            status = "干旱🏜️"
        
        return {
            "should_water": should_water,
            "score": score,
            "threshold": 60,
            "plant_status": status,
            "suggested_duration": duration,
            "reasons": reasons,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ai_version": self.version,
            "note": "基于规则引擎，后期可升级为AI模型"
        }


# 便捷函数
def get_watering_advice(soil_moisture, temperature, humidity):
    """获取浇水建议（对外接口）"""
    advisor = PlantAdvisor()
    return advisor.get_advice(soil_moisture, temperature, humidity)


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("🌱 智能浇水决策工具测试")
    print("版本：规则引擎 1.0")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        # (土壤湿度, 温度, 湿度, 描述)
        (650, 32, 35, "场景1: 严重干旱 + 高温 + 干燥"),
        (280, 24, 65, "场景2: 土壤湿润 + 适宜环境"),
        (480, 28, 45, "场景3: 干燥 + 温暖 + 中等湿度"),
        (350, 22, 75, "场景4: 略干 + 凉爽 + 潮湿"),
        (750, 18, 80, "场景5: 极端干旱但环境潮湿"),
    ]
    
    for soil, temp, hum, desc in test_cases:
        print(f"\n📊 {desc}")
        print(f"  输入: 土壤={soil}, 温度={temp}°C, 湿度={hum}%")
        
        advice = get_watering_advice(soil, temp, hum)
        
        decision = "✅ 需要浇水" if advice['should_water'] else "❌ 无需浇水"
        print(f"  决策: {decision}")
        print(f"  评分: {advice['score']}/{advice['threshold']}")
        print(f"  状态: {advice['plant_status']}")
        print(f"  建议时长: {advice['suggested_duration']}秒")
        
        print(f"  分析理由:")
        for i, reason in enumerate(advice['reasons'], 1):
            print(f"    {i:2d}. {reason}")
    
    print("\n" + "=" * 50)
    print("🎯 规则引擎特点:")
    print("  • 基于多因素加权评分")
    print("  • 阈值60分以上建议浇水")
    print("  • 考虑时间、温度、湿度等因素")
    print("  • 架构支持未来升级为真正AI")
    print("\n✅ 测试完成！")