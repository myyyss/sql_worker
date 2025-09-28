# SQL-manager 项目下载指南

## 方法一：直接压缩包下载（推荐）

1. 访问项目目录：
   ```
   /home/user/vibecoding/workspace/sql
   ```

2. 压缩项目文件夹：
   ```bash
   cd /home/user/vibecoding/workspace
   zip -r sql-manager.zip sql/
   ```

3. 下载压缩包：
   - 压缩包位置：`/home/user/vibecoding/workspace/sql-manager.zip`
   - 通过该文件传输工具（如scp、ftp或文件管理器）将此文件下载到本地计算机

## 方法二：使用Git命令克隆（如果有Git仓库）

如果项目已配置Git仓库：

```bash
# 克隆项目
git clone https://your-repository-url/sql-manager.git

# 进入项目目录
cd sql-manager
```

## 方法三：手动复制文件（如果上述方法不可用）

1. 前端目录结构：
   ```
   sql/
   ├── sql-manager/
   │   ├── index.html
   │   └── assets/
   └── sql-manager-backend/
       ├── app.py
       ├── requirements.txt
       └── sql_manager.db
   ```

2. 手动复制上述目录结构到本地计算机

## 方法四：使用PyCharm直接打开（推荐PyCharm用户）

1. 在PyCharm中：
   - 点击 "File > Open"
   - 导航到 `/home/user/vibecoding/workspace/sql`
   - 点击 "OK" 打开项目

2. 配置Python环境：
   - 点击 "File > Settings > Project: sql > Python Interpreter"
   - 配置虚拟环境并安装依赖

## 方法五：使用启动脚本（简化版）

```bash
# 复制启动脚本
cp /home/user/vibecoding/workspace/sql/run.py ~/

# 运行启动脚本
python ~/run.py
```

## 验证项目完整性

下载完成后，请项目目录结构应包含：

```
sql/
├── sql-manager/          # 前端代码
│   ├── index.html        # 主页面
│   └── assets/           # 静态资源
├── sql-manager-backend/  # Python后端代码
│   ├── app.py            # Flask应用主文件
│   ├── requirements.txt  # 依赖包列表
│   └── sql_manager.db    # SQLite数据库文件
├── run.py                # 启动脚本
└── README_PYCHARM.md     # PyCharm开发指南
```

## 后续步骤

下载项目后，请参考 `README_PYCHARM.md` 文件了解如何在PyCharm中配置和运行项目。

如需任何帮助，请请随时咨询！
