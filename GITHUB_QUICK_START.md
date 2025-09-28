# GitHub同步快速入门指南

## 5分钟上手GitHub同步

### 第一步：安装Git

**Windows**:
- 下载: https://git-scm.com/download/win
- 运行安装程序，按默认设置安装

**macOS**:
```bash
brew install install git
```

**Linux**:
```bash
sudo apt install git  # Ubuntu/Debian
# 或
sudo yum install git  # CentOS/RHEL
```

### 第二步：创建GitHub账号

1. 访问: https://github.com/join
2. 注册账号
3. 验证邮箱

### 第三步：创建GitHub仓库

1. 登录GitHub
2. 点击右上角角"+"图标 → "New repository"
3. 填写仓库名称（如: sql-manager）
4. **不要**勾选"Initialize this repository with a README"
5. 点击"Create repository"
6. 复制仓库仓库URL（复制）

### 第四步：初始化同步

在项目目录中运行：

```bash
cd /home/user/vibecoding/workspace/sql
python git_sync.py
```

按照提示完成以下步骤：

1. **配置Git信息**（首次运行时）
   - 输入GitHub用户名
   - 输入GitHub邮箱

2. **初始化仓库**（如果提示）
   - 输入 `y` 确认初始化

3. **添加远程仓库**
   - 粘贴您复制的GitHub仓库URL

4. **完成首次同步**
   - 工具会自动提交并推送代码

### 第五步：日常同步

#### 方法1：一键同步（推荐）

```bash
python git_sync_simple.py
```

这个脚本会自动：
- 拉取最新代码
- 提交本地更改
- 推送到GitHub

#### 方法2：通过启动脚本

```bash
python start.py
```

选择选项5："同步到GitHub"

#### 方法3：通过更新脚本

```bash
python update.py
```

选择选项6："同步到GitHub"

### 常用操作

#### 推送新代码到GitHub

```bash
python git_sync_simple.py
```

#### 从GitHubHub获取最新代码

```bash
python git_sync.py
# 选择选项2: 从GitHub拉取最新代码
```

#### 查看同步状态

```bash
python git_sync.py
# 选择选项4: 查看Git状态
```

### 常见问题

#### Q: 提示"未安装git"怎么办？
A: 请按照第一步安装Git，然后重新运行脚本。

#### Q: 如何获取GitHub仓库URL？
A: 在GitHub仓库页面，点击"Code"按钮，复制显示的URL。

#### Q: 同步失败显示"Permission denied"？
A: 检查您的GitHub仓库URL是否正确，确保您有权限访问该仓库。

#### Q: 数据库文件会被同步吗？
A: 默认情况下，数据库文件（*.db）不会被同步，以保护您的数据安全。

### 同步成功标志

当您看到以下信息时，表示同步成功：

```
✅ 推送成功！
🎉 项目已成功同步到GitHub
```

### 最佳实践

1. **定期同步**：建议每次开发前和开发后都进行同步
2. **提交有意义的信息**：描述您做了什么更改
3. **先拉后推**：推送前先拉取最新代码，避免冲突
4. **分支管理**：重要功能开发可以创建新分支

### 联系支持

如果遇到任何问题，请查看详细文档：
- 完整指南: README_GITHUB.md
- 安装指南: GITHUB_INSTALL_GUIDE.md

祝您使用愉快！
