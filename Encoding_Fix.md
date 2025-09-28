# 解决 UnicodeDecodeError 编码错误问题

## 问题描述
在安装依赖包时遇到以下错误：
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x85 in position 16: illegal multibyte sequence
decoding with 'cp936' codec failed
```

## 解决方案

### 方法一：使用新的requirements文件（推荐）
我已经创建了一个新的UTF-8编码的requirements文件：

```bash
cd /home/user/vibecoding/workspace/sql
pip install -r requirements_new.txt
```

### 方法二：指定编码格式安装
```bash
# 方法1：使用UTF-8编码读取文件
pip install -r <(iconv -f gbk -t utf-8 requirements.txt)

# 方法2：使用Python指定编码读取
python -m pip install -r <(python -c "import sys; print(sys.stdin.read().encode('utf-8').decode('utf-8'))" < requirements.txt)
```

### 方法三：手动安装依赖包
如果上述方法都不行，可以手动手动手动安装：

```bash
# 安装运行依赖
pip install Flask==2.0.1 Flask-CORS==3.0.10 Flask-SQLAlchemy==2.5.1 PyJWT==2.1.0 Werkzeug==2.0.1

# 可选：安装开发工具
pip install pytest==6.2.5 pytest-flask==1.0.0
```

### 方法四：修改pip配置
```bash
# 创建或编辑pip配置文件
mkdir -p ~/.pip
echo -e "[global]\nencoding = utf-8" > ~/.pip/pip.conf

# 然后重新安装
pip install -r requirements.txt
```

### 方法五：使用虚拟环境（彻底解决方案）
```bash
# 创建新的虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 设置环境变量
export PYTHONIOENCODING=utf-8

# 安装依赖
pip install -r requirements_new.txt
```

## 验证安装
安装完成后，可以验证是否成功：

```bash
# 检查已安装的包
pip list | grep -E "Flask|PyJWT|Werkzeug"

# 运行项目测试
cd /home/user/vibecoding/workspace/sql
python run.py
```

如果以上方法都无法解决问题，请提供完整的错误日志，我将为您提供更具体的解决方案。
