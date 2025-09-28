import subprocess
import sys
import os
import re

def get_current_pip_version():
    """获取当前pip版本"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        # 从输出中提取版本号
        match = re.search(r'pip\s+(\d+\.\d+\.?\d*)', output)
        if match:
            return match.group(1)
        return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None

def parse_version(version_str):
    """解析版本字符串为元组"""
    try:
        return tuple(map(int, version_str.split('.')))
    except ValueError:
        return (0, 0, 0)

def is_version_less_than(current, target):
    """检查当前版本是否小于目标版本"""
    current_tuple = parse_version(current)
    target_tuple = parse_version(target)
    
    # 确保两个版本元组长度相同
    max_len = max(len(current_tuple), len(target_tuple))
    current_tuple += (0,) * (max_len - len(current_tuple))
    target_tuple += (0,) * (max_len - len(target_tuple))
    
    return current_tuple < target_tuple

def check_and_upgrade_pip():
    """检查并升级pip"""
    try:
        current_version = get_current_pip_version()
        
        if current_version and is_version_less_than(current_version, "25.2"):
            print("=" * 50)
            print(f"检测到pip版本较旧 (当前: {current_version})")
            print("建议升级到最新版本以避免兼容性问题")
            print("=" * 50)
            
            # 询问用户是否升级
            try:
                choice = input("是否升级pip? (y/n, 默认n): ").lower()
                if choice == 'y':
                    print("正在升级pip...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
                    ])
                    print("pip升级成功！")
                    print("请重新运行启动脚本")
                    sys.exit(0)
                else:
                    print("已选择不升级pip，继续启动应用...")
            except KeyboardInterrupt:
                print("\n已取消pip升级")
            except subprocess.CalledProcessError:
                print("pip升级失败，继续启动应用...")
    except Exception:
        # 任何错误都继续启动应用
        pass

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    
    # 先尝试使用SQLite版本的requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_sqlite.txt"])
        print("依赖包安装成功！")
        return
    except subprocess.CalledProcessError:
        print("使用requirements_sqlite.txt安装失败，尝试使用requirements_compatible.txt...")
    
    # 如果失败，尝试使用requirements_compatible.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_compatible.txt"])
        print("依赖包包安装包安装成功！")
        return
    except subprocess.CalledProcessError:
        print("使用requirements_compatible.txt安装失败，尝试使用requirementsments_new.txt...")
    
    # 如果都失败，尝试使用原始的requirements.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装成功！")
        return
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包安装失败: {e}")
        print("请手动手动安装依赖包:")
        print("pip install Flask==2.0.3 Flask-CORS==3.0.10 Flask-SQLAlchemy==2.5.3 PyJWT==2.3.0 Werkzeug==2.0.3 SQLAlchemy==1.4.46")
        sys.exit(1)

def run_application():
    """运行应用程序"""
    print("启动应用程序...")
    
    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), "sql-manager-backend")
    os.chdir(backend_dir)
    
    # 运行app.py
    try:
        subprocess.check_call([sys.executable, "app.py"])
    except subprocess.CalledProcessError as e:
        print(f"应用程序启动失败: {e}")
        print("请检查错误信息并尝试手动运行:")
        print("cd sql-manager-backend")
        print("python app.py")
        sys.exit(1)

def main():
    print("=== SQL管理工具 (SQLite版本) ===")
    
    # 检查并升级pip
    check_and_upgrade_pip()
    
    print("1. 安装依赖包")
    print("2. 运行应用程序")
    print("3. 安装依赖并运行")
    
    choice = input("请选择操作 (1/2/3): ").strip()
    
    if choice == "1":
        install_requirements()
    elif choice == "2":
        run_application()
    elif choice == "3":
        install_requirements()
        run_application()
    else:
        print("无效选择")
        sys.exit(1)

if __name__ == "__main__":
    main()
