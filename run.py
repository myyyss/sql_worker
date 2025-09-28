import subprocess
import sys
import os
from pathlib import Path

def main():
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误：需要Python 3.7或更高版本")
        sys.exit(1)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 后端目录
    backend_dir = project_root / "sql-manager-backend"
    
    # 检查后端目录是否存在
    if not backend_dir.exists():
        print(f"错误：后端目录不存在: {backend_dir}")
        sys.exit(1)
    
    # 检查requirements.txt是否存在
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print(f"错误：requirements.txt不存在: {requirements_file}")
        sys.exit(1)
    
    # 安装依赖
    print("正在依赖...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", 
        str(requirements_file)
    ], check=True)
    
    # 切换到后端目录
    os.chdir(str(backend_dir))
    
    # 运行Flask应用
    print("启动SQL管理工具...")
    print("访问 http://127.0.0.1:5000 查看应用")
    print("按 Ctrl+C 停止服务器")
    
    subprocess.run([
        sys.executable, "app.py"
    ], check=True)

if __name__ == "__main__":
    main()
