# -*- coding: utf-8 -*-
from typing import Dict, Any
from jarvis.jarvis_utils.output import PrettyOutput, OutputType
import os
import subprocess
import tempfile
import shutil

class install_nerd_font:
    name = "install_nerd_font"
    description = "自动下载并安装Nerd字体到用户字体目录"
    parameters = {
        "type": "object",
        "properties": {
            "font_name": {
                "type": "string",
                "description": "要安装的Nerd字体名称，如：FiraCode、JetBrainsMono、Hack等",
                "default": "FiraCode"
            },
            "version": {
                "type": "string", 
                "description": "Nerd字体版本号，默认为最新稳定版v3.0.2",
                "default": "v3.0.2"
            }
        },
        "required": ["font_name"]
    }
    
    @staticmethod
    def check() -> bool:
        """检查系统是否支持字体安装"""
        try:
            # 检查是否有wget或curl
            result = subprocess.run(['which', 'wget'], capture_output=True, text=True)
            if result.returncode != 0:
                result = subprocess.run(['which', 'curl'], capture_output=True, text=True)
                if result.returncode != 0:
                    return False
            
            # 检查fc-cache命令是否存在
            result = subprocess.run(['which', 'fc-cache'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行字体安装"""
        try:
            font_name = args.get("font_name", "FiraCode")
            version = args.get("version", "v3.0.2")
            
            PrettyOutput.print(f"开始安装 {font_name} Nerd Font...", OutputType.INFO)
            
            # 构建下载URL
            base_url = f"https://github.com/ryanoasis/nerd-fonts/releases/download/{version}"
            font_url = f"{base_url}/{font_name}.zip"
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, f"{font_name}.zip")
                
                # 下载字体文件
                PrettyOutput.print(f"正在下载 {font_name} Nerd Font...", OutputType.INFO)
                download_cmd = ['wget', '-q', font_url, '-O', zip_path]
                result = subprocess.run(download_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # 尝试使用curl作为备选
                    download_cmd = ['curl', '-L', '-s', font_url, '-o', zip_path]
                    result = subprocess.run(download_cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        PrettyOutput.print(f"下载失败，请检查字体名称和版本是否正确", OutputType.ERROR)
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"下载失败: {result.stderr}"
                        }
                
                # 解压字体文件
                PrettyOutput.print("正在解压字体文件...", OutputType.INFO)
                unzip_cmd = ['unzip', '-q', zip_path, '-d', temp_dir]
                result = subprocess.run(unzip_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    PrettyOutput.print("解压失败", OutputType.ERROR)
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": f"解压失败: {result.stderr}"
                    }
                
                # 创建用户字体目录
                font_dir = os.path.expanduser("~/.local/share/fonts")
                os.makedirs(font_dir, exist_ok=True)
                
                # 复制字体文件
                PrettyOutput.print("正在安装字体...", OutputType.INFO)
                font_files = [f for f in os.listdir(temp_dir) if f.endswith(('.ttf', '.otf'))]
                
                for font_file in font_files:
                    src_path = os.path.join(temp_dir, font_file)
                    dst_path = os.path.join(font_dir, font_file)
                    shutil.copy2(src_path, dst_path)
                
                # 更新字体缓存
                PrettyOutput.print("正在更新字体缓存...", OutputType.INFO)
                cache_cmd = ['fc-cache', '-fv', font_dir]
                result = subprocess.run(cache_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    PrettyOutput.print("字体缓存更新失败", OutputType.WARNING)
            
            # 验证安装
            verify_cmd = ['fc-list', '|', 'grep', '-i', font_name.lower()]
            result = subprocess.run(' '.join(verify_cmd), shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                PrettyOutput.print(f"{font_name} Nerd Font 安装成功！", OutputType.SUCCESS)
                return {
                    "success": True,
                    "stdout": f"{font_name} Nerd Font 安装成功",
                    "stderr": ""
                }
            else:
                PrettyOutput.print("字体安装完成，但验证失败", OutputType.WARNING)
                return {
                    "success": True,
                    "stdout": f"{font_name} Nerd Font 安装完成",
                    "stderr": "验证失败，但安装过程完成"
                }
                
        except Exception as e:
            PrettyOutput.print(f"安装失败: {str(e)}", OutputType.ERROR)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"安装失败: {str(e)}"
            }
