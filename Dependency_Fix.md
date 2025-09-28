# 解决依赖包版本冲突问题

## 问题描述
在安装依赖包时遇到以下错误：
```
ERROR: Could not find a version that satisfies the requirement Jinja2>=3.0 (from flask) (from versions: none)
ERROR: No matching distribution found for Jinja2>=3.0
```

## 解决方案

### 方法一：使用兼容版本的requirements文件（推荐）
我已经创建了一个使用更宽松版本约束的文件：

```bash
cd /home/user/vibecoding/workspace/sql
pip install -r requirements_compatible.txt
```

### 方法二：升级pip并使用最新版本
```bash
# 升级pip
pip install --upgrade pip

# 清除缓存
pip cache purge

# 重新安装
pip install Flask Flask-CORS Flask-SQLAlchemy PyJWT Werkzeug pytest pytest-flask
```

### 方法三：手动安装特定版本
```bash
# 安装兼容的Flask版本
pip install Flask==2.0.1

# 安装其他依赖
pip install Flask-CORS==3.0.10 Flask-SQLAlchemy==2.5.1 PyJWT==2.1.0 Werkzeug==2.0.1
pip install pytest==6.2.5 pytest-flask==1.0.0
```

### 方法四：使用虚拟环境（推荐）
```bash
# 创建新的虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements_compatible.txt
```

### 方法五：指定国内PyPI源
如果是网络问题或源的问题，可以使用国内源：

```bash
# 使用阿里云源
pip install -r requirements_compatible.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或使用清华大学源
pip install -r requirements_compatible.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 方法六：手动安装所有依赖
```bash
# 直接安装所有需要的包
pip install Flask Flask-CORS Flask-SQLAlchemy PyJWT Werkzeug pytest pytest-flask
```

## 验证安装
安装完成后，可以验证是否成功：

```bash
# 检查已安装的包
pip list | grep -E "Flask|Jinja2|Werkzeug|SQLAlchemy|PyJWT"

# 运行项目测试
cd /home/user/vibecoding/workspace/sql
python run.py
```

## 常见问题排查

1. **检查Python版本**：
   ```bash
   python --version
   # 确保是Python 3.7或更高版本
   ```

2. **检查pip版本**：
   ```bash
   pip --version
   # 如果版本过旧，请升级pip
   ```

3. **检查网络连接**：
   ```bash
   # 测试PyPI连接
   ping pypi.org
   ```

4. **检查代理设置**：
   ```bash
   # 如果使用代理，请确保配置正确
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

如果以上方法都无法解决问题，请提供完整的错误日志，我将为您提供更具体的解决方案。
