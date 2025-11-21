#!/usr/bin/env python3
"""
依赖检查器 - 智能依赖管理
=======================

检查和管理系统依赖，提供自动安装功能
"""

import sys
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class DependencyInfo:
    """依赖信息"""
    
    def __init__(self, name: str, import_name: str = None, version: str = None):
        self.name = name  # pip包名
        self.import_name = import_name or name  # import时使用的名称
        self.version = version
        self.installed = False
        self.installed_version = None


class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self):
        self.required_deps = [
            DependencyInfo('markdown', 'markdown', '>=3.5.1'),
            DependencyInfo('pyppeteer', 'pyppeteer', '>=1.0.2'),
            DependencyInfo('Pygments', 'pygments', '>=2.14.0'),
        ]
        
        self.optional_deps = [
            DependencyInfo('asyncio', 'asyncio'),  # 内置模块
        ]
    
    def check_python_version(self) -> Tuple[bool, str]:
        """检查Python版本"""
        current_version = sys.version_info
        min_version = (3, 7)
        
        is_valid = current_version >= min_version
        version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
        
        return is_valid, version_str
    
    def check_dependency(self, dep: DependencyInfo) -> bool:
        """检查单个依赖"""
        try:
            module = importlib.import_module(dep.import_name)
            dep.installed = True
            
            # 尝试获取版本信息
            if hasattr(module, '__version__'):
                dep.installed_version = module.__version__
            
            return True
            
        except ImportError:
            dep.installed = False
            return False
    
    def check_all_dependencies(self) -> Dict[str, List[DependencyInfo]]:
        """检查所有依赖"""
        results = {
            'required': [],
            'optional': [],
            'missing': [],
            'installed': []
        }
        
        # 检查必需依赖
        for dep in self.required_deps:
            if self.check_dependency(dep):
                results['installed'].append(dep)
            else:
                results['missing'].append(dep)
            results['required'].append(dep)
        
        # 检查可选依赖
        for dep in self.optional_deps:
            self.check_dependency(dep)
            results['optional'].append(dep)
        
        return results
    
    def install_dependencies(
        self, 
        deps: List[DependencyInfo] = None,
        requirements_file: str = None,
        verbose: bool = True
    ) -> Tuple[bool, str]:
        """安装依赖"""
        
        if requirements_file and Path(requirements_file).exists():
            return self._install_from_requirements(requirements_file, verbose)
        
        if deps is None:
            deps = [dep for dep in self.required_deps if not dep.installed]
        
        if not deps:
            return True, "所有依赖已安装"
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"]
            
            for dep in deps:
                if dep.version:
                    cmd.append(f"{dep.name}{dep.version}")
                else:
                    cmd.append(dep.name)
            
            if verbose:
                print(f"🔧 安装依赖: {' '.join(dep.name for dep in deps)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=not verbose,
                text=True,
                check=True
            )
            
            # 重新检查已安装的依赖
            for dep in deps:
                self.check_dependency(dep)
            
            return True, "依赖安装成功"
            
        except subprocess.CalledProcessError as e:
            error_msg = f"依赖安装失败: {e}"
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f"\n{e.stderr}"
            return False, error_msg
    
    def _install_from_requirements(self, requirements_file: str, verbose: bool) -> Tuple[bool, str]:
        """从requirements.txt安装依赖"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
            
            if verbose:
                print(f"🔧 从 {requirements_file} 安装依赖")
            
            subprocess.run(cmd, capture_output=not verbose, text=True, check=True)
            
            return True, "依赖安装成功"
            
        except subprocess.CalledProcessError as e:
            return False, f"依赖安装失败: {e}"
    
    def get_environment_info(self) -> Dict[str, str]:
        """获取环境信息"""
        python_valid, python_version = self.check_python_version()
        
        return {
            'python_version': python_version,
            'python_valid': python_valid,
            'python_executable': sys.executable,
            'platform': sys.platform,
            'working_directory': str(Path.cwd())
        }
    
    def generate_report(self) -> str:
        """生成依赖检查报告"""
        env_info = self.get_environment_info()
        dep_results = self.check_all_dependencies()
        
        report = []
        report.append("🔍 系统环境检查报告")
        report.append("=" * 40)
        
        # Python版本
        status = "✅" if env_info['python_valid'] else "❌"
        report.append(f"{status} Python版本: {env_info['python_version']}")
        
        # 工作目录
        report.append(f"📁 工作目录: {env_info['working_directory']}")
        
        # 必需依赖
        report.append("\n📦 必需依赖:")
        for dep in dep_results['required']:
            status = "✅" if dep.installed else "❌"
            version_info = f" ({dep.installed_version})" if dep.installed_version else ""
            report.append(f"  {status} {dep.name}{version_info}")
        
        # 可选依赖
        if dep_results['optional']:
            report.append("\n🔧 可选依赖:")
            for dep in dep_results['optional']:
                status = "✅" if dep.installed else "⚠️"
                version_info = f" ({dep.installed_version})" if dep.installed_version else ""
                report.append(f"  {status} {dep.name}{version_info}")
        
        # 缺失依赖
        if dep_results['missing']:
            report.append("\n❌ 缺失依赖:")
            for dep in dep_results['missing']:
                report.append(f"  • {dep.name}")
        
        return "\n".join(report)