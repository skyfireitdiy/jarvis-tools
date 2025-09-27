# -*- coding: utf-8 -*-
from typing import Dict, Any
import os
import subprocess
from jarvis.jarvis_utils.output import PrettyOutput, OutputType

class nvim_diagnostic:
    name = "nvim_diagnostic"
    description = "诊断和修复nvim启动问题的工具，支持插件管理器检查、配置文件验证和常见故障修复"
    
    parameters = {
        "type": "object",
        "properties": {
            "fix_issues": {
                "type": "boolean",
                "description": "是否自动修复发现的问题",
                "default": False
            },
            "check_plugins": {
                "type": "boolean", 
                "description": "是否检查插件管理器状态",
                "default": True
            },
            "verbose": {
                "type": "boolean",
                "description": "是否显示详细检查信息",
                "default": False
            }
        },
        "required": []
    }
    
    @staticmethod
    def check() -> bool:
        """检查是否安装了nvim"""
        try:
            subprocess.run(["nvim", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行nvim诊断"""
        try:
            PrettyOutput.print("开始nvim诊断...", OutputType.INFO)
            
            issues_found = []
            fixes_applied = []
            
            # 1. 检查vim-plug
            plug_path = os.path.expanduser("~/.local/share/nvim/site/autoload/plug.vim")
            if not os.path.exists(plug_path):
                issues_found.append("vim-plug插件管理器缺失")
                
                if args.get("fix_issues", False):
                    PrettyOutput.print("正在安装vim-plug...", OutputType.INFO)
                    try:
                        os.makedirs(os.path.dirname(plug_path), exist_ok=True)
                        
                        # 尝试多种方式下载
                        import urllib.request
                        urls = [
                            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
                            "https://hub.fastgit.org/junegunn/vim-plug/raw/master/plug.vim"
                        ]
                        
                        success = False
                        for url in urls:
                            try:
                                urllib.request.urlretrieve(url, plug_path)
                                success = True
                                break
                            except:
                                continue
                        
                        if success:
                            fixes_applied.append("已安装vim-plug插件管理器")
                            PrettyOutput.print("vim-plug安装成功", OutputType.SUCCESS)
                        else:
                            PrettyOutput.print("无法下载vim-plug，请检查网络连接", OutputType.ERROR)
                    except Exception as e:
                        PrettyOutput.print(f"安装vim-plug失败: {str(e)}", OutputType.ERROR)
            else:
                PrettyOutput.print("vim-plug状态正常", OutputType.SUCCESS)
            
            # 2. 检查配置文件
            config_path = os.path.expanduser("~/.config/nvim/init.vim")
            if not os.path.exists(config_path):
                issues_found.append("主配置文件init.vim不存在")
            else:
                if args.get("verbose", False):
                    PrettyOutput.print(f"找到配置文件: {config_path}", OutputType.INFO)
            
            # 3. 测试nvim启动
            PrettyOutput.print("测试nvim启动...", OutputType.INFO)
            try:
                result = subprocess.run([
                    "nvim", "--headless", 
                    "-c", "echo 'test'", 
                    "-c", "qa!"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    PrettyOutput.print("nvim可以正常启动", OutputType.SUCCESS)
                else:
                    issues_found.append("nvim启动失败")
                    if args.get("verbose", False):
                        PrettyOutput.print(f"错误输出: {result.stderr}", OutputType.ERROR)
            except subprocess.TimeoutExpired:
                issues_found.append("nvim启动超时")
            except Exception as e:
                issues_found.append(f"nvim测试失败: {str(e)}")
            
            # 4. 检查插件目录
            plugged_dir = os.path.expanduser("~/.local/share/nvim/plugged")
            if not os.path.exists(plugged_dir):
                if args.get("verbose", False):
                    PrettyOutput.print("插件目录尚未创建", OutputType.INFO)
            else:
                plugin_count = len([d for d in os.listdir(plugged_dir) if os.path.isdir(os.path.join(plugged_dir, d))])
                PrettyOutput.print(f"已安装 {plugin_count} 个插件", OutputType.INFO)
            
            # 输出总结
            if issues_found:
                PrettyOutput.print(f"发现 {len(issues_found)} 个问题", OutputType.WARNING)
                for issue in issues_found:
                    PrettyOutput.print(f"  - {issue}", OutputType.WARNING)
            else:
                PrettyOutput.print("未发现问题，nvim配置正常", OutputType.SUCCESS)
            
            if fixes_applied:
                PrettyOutput.print(f"已应用 {len(fixes_applied)} 个修复", OutputType.SUCCESS)
                for fix in fixes_applied:
                    PrettyOutput.print(f"  - {fix}", OutputType.SUCCESS)
            
            stdout_msg = f"诊断完成。发现问题: {len(issues_found)}个, 修复应用: {len(fixes_applied)}个"
            if args.get("verbose", False) and issues_found:
                stdout_msg += "\n问题详情:\n" + "\n".join(f"- {issue}" for issue in issues_found)
            
            return {
                "success": len(issues_found) == 0 or (args.get("fix_issues", False) and len(issues_found) == len(fixes_applied)),
                "stdout": stdout_msg,
                "stderr": "",
                "issues_found": issues_found,
                "fixes_applied": fixes_applied
            }
            
        except Exception as e:
            PrettyOutput.print(f"诊断过程出错: {str(e)}", OutputType.ERROR)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"诊断失败: {str(e)}"
            }
