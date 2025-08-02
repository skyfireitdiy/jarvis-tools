# -*- coding: utf-8 -*-
import requests
from typing import Dict, Any

from jarvis.jarvis_utils.output import PrettyOutput, OutputType

class get_weather:
    name = "get_weather"
    description = """获取指定城市的天气预报。

    适用场景:
    1. 查询当前天气。
    2. 查询今天的天气预报。
    3. 查询明天的天气预报。

    使用示例:
    - 查询北京明天的天气: get_weather(city="Beijing")
    - 查询上海今天的天气: get_weather(city="Shanghai", forecast_type="today")
    - 查询广州当前的天气: get_weather(city="Guangzhou", forecast_type="current")
    """

    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "需要查询天气的城市名称 (支持中文或英文)"
            },
            "forecast_type": {
                "type": "string",
                "description": "预报类型",
                "enum": ["current", "today", "tomorrow"],
                "default": "tomorrow"
            }
        },
        "required": ["city"]
    }

    @staticmethod
    def check() -> bool:
        """检查requests库是否可用"""
        try:
            import requests
            return True
        except ImportError:
            PrettyOutput.print("缺少 'requests' 库，请先安装: pip install requests", OutputType.ERROR)
            return False

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        city = args.get("city")
        forecast_type = args.get("forecast_type", "tomorrow")

        PrettyOutput.print(f"正在为城市 '{city}' 获取 '{forecast_type}' 的天气预报...", OutputType.INFO)

        try:
            # 使用 wttr.in 的 JSON API
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 如果请求失败则抛出异常
            
            weather_data = response.json()

            # 提取并格式化所需信息
            if forecast_type == "current":
                data = weather_data.get("current_condition")
                if not data:
                    raise ValueError("无法获取当前天气数据")
                
                current = data[0]
                location = weather_data['nearest_area'][0]
                city_name = f"{location['areaName'][0]['value']}, {location['country'][0]['value']}"
                
                output_str = (
                    f"城市: {city_name}\n"
                    f"天气: {current['weatherDesc'][0]['value']}\n"
                    f"温度: {current['temp_C']}°C (体感: {current['FeelsLikeC']}°C)\n"
                    f"风速: {current['windspeedKmph']} km/h\n"
                    f"湿度: {current['humidity']}%"
                )

            else: # 'today' or 'tomorrow'
                day_index = 0 if forecast_type == "today" else 1
                if len(weather_data.get("weather", [])) <= day_index:
                     raise ValueError(f"无法获取 {forecast_type} 的天气数据")
                
                forecast = weather_data["weather"][day_index]
                location = weather_data['nearest_area'][0]
                city_name = f"{location['areaName'][0]['value']}, {location['country'][0]['value']}"

                hourly_reports = []
                for hourly in forecast['hourly']:
                    time_in_hour = int(hourly['time']) // 100
                    report = (
                        f"  - {time_in_hour:02d}:00: "
                        f"{hourly['weatherDesc'][0]['value']:<15}, "
                        f"温度: {hourly['tempC']:>3}°C, "
                        f"风速: {hourly['windspeedKmph']:>2} km/h"
                    )
                    hourly_reports.append(report)

                output_str = (
                    f"城市: {city_name}\n"
                    f"日期: {forecast['date']}\n"
                    f"天气概况: 最高 {forecast['maxtempC']}°C, 最低 {forecast['mintempC']}°C\n"
                    f"日出: {forecast['astronomy'][0]['sunrise']}\n"
                    f"日落: {forecast['astronomy'][0]['sunset']}\n"
                    f"小时预报:\n" + "\n".join(hourly_reports)
                )

            PrettyOutput.print("成功获取天气信息", OutputType.SUCCESS)
            return {
                "success": True,
                "stdout": output_str,
                "stderr": ""
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {e}"
            PrettyOutput.print(error_msg, OutputType.ERROR)
            return {"success": False, "stdout": "", "stderr": error_msg}
        except (ValueError, KeyError, IndexError) as e:
            error_msg = f"解析天气数据失败: {e}. 请检查城市名称是否正确。"
            PrettyOutput.print(error_msg, OutputType.ERROR)
            return {"success": False, "stdout": "", "stderr": error_msg}
        except Exception as e:
            error_msg = f"发生未知错误: {e}"
            PrettyOutput.print(error_msg, OutputType.ERROR)
            return {"success": False, "stdout": "", "stderr": error_msg}
