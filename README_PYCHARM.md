# SQL管理工具 - PyCharm开发指南

## 项目概述

这是一个功能强大的SQL管理工具，支持多用户协作、SQL语句执行和结果可视化。本指南将帮助您在PyCharm中继续开发此项目。

## 项目结构

```
sql/
├── sql-manager/          # 前端代码
│   ├── index.html        # 主页面
│   ├── assets/           # 静态资源
│   └── ...
├── sql-manager-backend/  # Python后端代码
│   ├── app.py            # Flask应用主文件
│   ├── requirements.txt  # 依赖包列表
│   └── sql_manager.db    # SQLite数据库文件
├── run.py                # 启动脚本
└── README_PYCHARM.md     # PyCharm开发指南
```

## 在PyCharm中打开项目

1. 打开PyCharm
2. 点击 "Open" 或 "File > Open"
3. 选择项目根目录 `/home/user/vibecoding/workspace/sql`
4. 点击 "OK" 打开项目

## 配置Python环境

1. 点击 "File > Settings > Project: sql > Python Interpreter"
2. 点击齿轮图标，选择 "Add"
3. 选择 "Virtualenv Environment"
4. 选择 "New Virtualenv" 或 "Existing environment"
5. 点击 "OK" 保存配置

## 安装依赖

1. 打开PyCharm的Terminal
2. 运行以下命令：
   ```bash
   cd sql-manager-backend
   pip install -r requirements.txt
   ```

## 运行项目

### 方法1：使用启动脚本

1. 在PyCharm中打开 `run.py` 文件
2. 点击文件右上角的绿色播放按钮，或右键点击文件选择 "Run 'run'"

### 方法2：直接运行Flask应用

1. 在PyCharm中打开 `sql-manager-backend/app.py` 文件
2. 点击文件右上角的绿色播放按钮，或右键点击文件选择 "Run 'app'"

## 访问应用

项目启动后，在浏览器中访问：`http://127.0.0.1:5000

## 默认用户

系统已预置置了一个测试用户：
- 邮箱：test@example.com
- 密码：password123

## 开发指南

### 前端开发

前端代码位于 `sql-manager` 目录中：
- `index.html`：主页面，包含所有HTML、CSS和JavaScript代码
- `assets/`：包含图标、图片等静态资源

### 后端开发

后端代码位于 `sql-manager-backend` 目录中：
- `app.py`：Flask应用主文件，包含所有API端点和业务逻辑
- `sql_manager.db`：SQLite数据库文件，存储所有数据

### 数据库模型

主要数据库模型包括：
- User：用户信息
- SqlSnippet：SQL语句片段
- Category：SQL语句分类
- Tag：SQL语句标签
- Comment：评论

### API端点

主要API端点包括：
- `/api/register`：用户注册
- `/api/login`：用户登录
- `/api/sql-snippets`：SQL语句管理（CRUD操作）
- `/api/categories`：分类管理
- `/api/tags`：标签管理
- `/api/execute-sql`：执行SQL语句

## 调试技巧

### 调试后端

1. 在PyCharm中打开 `app.py`
2. 在需要调试断点的行号点击左侧空白区域，设置断点
3. 点击 "Debug 'app'" 按钮（绿色虫子图标）
4. 使用应用触发断点，查看变量值调用栈

### 调试前端

1. 在Chrome浏览器中打开应用
2. 按 F12 打开开发者工具
3. 切换到 "Sources" 标签页
4. 在左侧导航找到找到并打开 `index.html`
5. 在需要调试的JavaScript代码处设置断点

## 常见问题

### 端口被占用

如果启动时提示端口5000被占用，可以修改 `app.py` 文件中的端口号：

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # 修改port参数
```

### 数据库问题

如果遇到数据库相关问题，可以删除 `sql_manager.db` 文件，系统会自动重新创建一个新的数据库文件。

### 依赖包安装问题

如果安装依赖包时遇到问题，可以尝试升级pip：

```bash
pip install --upgrade pip
```

## 后续开发建议

1. **添加更多数据库支持**：目前只支持模拟执行SQL，未来可以添加真实数据库连接功能
2. **增强SQL编辑器**：添加语法高亮、自动补全、格式化等功能
3. **添加版本控制**：为SQL语句添加版本历史记录功能
4. **实现更高级的权限管理**：支持私有SQL语句、分享给特定用户等功能
5. **添加更多数据可视化**：支持图表、导出等功能

## 联系方式

如有任何问题，请联系项目负责人。
