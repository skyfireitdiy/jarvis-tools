# -*- coding: utf-8 -*-
import os
import subprocess
from typing import Dict, Any
from jarvis.jarvis_utils.output import PrettyOutput, OutputType

class convert_video:
    """
    视频格式转换工具
    """
    name = "convert_video"
    description = "使用ffmpeg将视频文件从一种格式转换为另一种格式。"
    parameters = {
        "type": "object",
        "properties": {
            "input_file": {
                "type": "string",
                "description": "源视频文件的路径。"
            },
            "output_file": {
                "type": "string",
                "description": "输出视频文件的路径。如果未提供，将自动生成。"
            }
        },
        "required": ["input_file"]
    }

    @staticmethod
    def check() -> bool:
        """检查ffmpeg是否已安装"""
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            PrettyOutput.print("错误：ffmpeg未安装或不在系统PATH中。", OutputType.ERROR)
            return False

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频转换"""
        input_file = args.get("input_file")
        output_file = args.get("output_file")

        if not os.path.exists(input_file):
            PrettyOutput.print(f"输入文件不存在: {input_file}", OutputType.ERROR)
            return {"success": False, "stdout": "", "stderr": f"输入文件不存在: {input_file}"}

        if not output_file:
            base, _ = os.path.splitext(input_file)
            output_file = f"{base}.mp4"
            PrettyOutput.print(f"未指定输出文件，将使用默认名称: {output_file}", OutputType.INFO)

        command = ["ffmpeg", "-i", input_file, output_file]

        try:
            PrettyOutput.print(f"正在执行转换命令: {' '.join(command)}", OutputType.INFO)
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            success_message = f"视频已成功转换为 {output_file}"
            PrettyOutput.print(success_message, OutputType.SUCCESS)
            return {
                "success": True,
                "stdout": success_message + "\n" + process.stdout,
                "stderr": process.stderr
            }
        except subprocess.CalledProcessError as e:
            error_message = f"视频转换失败: {e.stderr}"
            PrettyOutput.print(error_message, OutputType.ERROR)
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": error_message
            }
        except Exception as e:
            error_message = f"发生未知错误: {str(e)}"
            PrettyOutput.print(error_message, OutputType.ERROR)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_message
            }
