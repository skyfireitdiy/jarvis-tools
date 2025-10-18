# -*- coding: utf-8 -*-
import requests
from typing import Dict, Any
from jarvis.jarvis_utils.output import PrettyOutput, OutputType
import json

class get_weather_forecast:
    """
    获取指定城市的天气预报信息
    """
    name = "get_weather_forecast"
    description = "获取指定城市未来三天的天气预报"
    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "需要查询天气的城市名称, 例如: 北京"
            }
        },
        "required": ["city"]
    }

    @staticmethod
    def check() -> bool:
        # 检查requests库是否存在
        try:
            import requests
            return True
        except ImportError:
            PrettyOutput.print("缺少 'requests' 库，请先安装: pip install requests", OutputType.ERROR)
            return False

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        city = args.get("city")
        if not city:
            return {
                "success": False,
                "stdout": "",
                "stderr": "缺少城市名称参数"
            }

        url = f"https://wttr.in/{city}?format=j1"
        PrettyOutput.print(f"正在从 {url} 获取天气信息...", OutputType.INFO)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 如果请求失败则抛出HTTPError

            weather_data = response.json()

            # 提取并格式化输出
            current_condition = weather_data.get('current_condition', [{}])[0]
            forecast = weather_data.get('weather', [])
            
            output = f"城市: {weather_data.get('nearest_area', [{}])[0].get('value')}\n"
            output += "--- 当前天气 ---\n"
            output += f"  温度: {current_condition.get('temp_C')}°C\n"
            output += f"  体感温度: {current_condition.get('FeelsLikeC')}°C\n"
            output += f"  天气: {current_condition.get('weatherDesc', [{}])[0].get('value')}\n"
            output += f"  风速: {current_condition.get('windspeedKmph')} km/h\n"
            output += f"  湿度: {current_condition.get('humidity')}%\n"
            
            output += "\n--- 未来三天预报 ---\n"
            for day in forecast:
                output += f"日期: {day.get('date')}\n"
                output += f"  最高温: {day.get('maxtempC')}°C, 最低温: {day.get('mintempC')}°C\n"
                output += f"  日出: {day.get('astronomy', [{}])[0].get('sunrise')}, 日落: {day.get('astronomy', [{}])[0].get('sunset')}\n"
                # 选择中午12点的数据作为当天天气的代表
                hourly_forecast_for_midday = day.get('hourly', [{}])[4]
                output += f"  天气: {hourly_forecast_for_midday.get('weatherDesc', [{}])[0].get('value')}\n"
                output += "-------------------\n"

            PrettyOutput.print("天气信息获取成功", OutputType.SUCCESS)
            return {
                "success": True,
                "stdout": output,
                "stderr": ""
            }

        except requests.exceptions.RequestException as e:
            error_message = f"获取天气信息失败: {str(e)}"
            PrettyOutput.print(error_message, OutputType.ERROR)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_message
            }
        except Exception as e:
            error_message = f"处理天气数据时发生未知错误: {str(e)}"
            PrettyOutput.print(error_message, OutputType.ERROR)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_message
            }
