import os
import sys
import subprocess
import platform

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        # 使用pip安装依赖
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", 
            "requirements_simple.txt", "--user"
        ])
        print("依赖包安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        sys.exit(1)

def check_requirements():
    """检查是否已安装所有依赖"""
    required_packages = [
        'Flask==1.1.4',
        'Flask-CORS==3.0.10',
        'Flask-SQLAlchemy==2.5.1',
        'PyJWT==2.0.1',
        'Werkzeug==1.0.1',
        'SQLAlchemy==1.3.24'
    ]
    
    missing_packages = []
    for package in required_packages:
        package_name = package.split('==')[0]
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def start_server():
    """启动服务器"""
    print("正在启动SQL管理工具...")
    
    # 切换到后端目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'sql-manager-backend')
    os.chdir(backend_dir)
    
    # 启动Flask应用
    try:
        subprocess.call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")

def main():
    print("=" * 50)
    print("SQL管理工具 - 简易版本启动器")
    print("=" * 50)
    
    # 检查依赖
    missing_packages = check_requirements()
    if missing_packages:
        print(f"检测到缺失的依赖包: {', '.join(missing_packages)}")
        choice = input("是否安装这些依赖包? (y/n): ").lower()
        if choice == 'y':
            install_requirements()
        else:
            print("依赖包缺失，无法启动应用")
            sys.exit(1)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
