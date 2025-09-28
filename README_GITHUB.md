# SQL管理工具 - GitHub同步指南

## 概述

本指南提供了如何将SQL管理工具项目同步到GitHub仓库的详细说明。通过GitHub同步，您可以轻松地备份项目、与团队协作以及在不同设备之间同步代码。

## 准备工作

### 1. 安装Git

首先，您需要安装Git版本控制系统：

- **Windows**: 下载并安装 [Git for Windows](https://git-scm.com/download/win)
- **macOS**: 使用Homebrew安装 `brew install git` 或从 [官网](https://git-scm.com/download/mac) 下载
- **Linux**: 使用包管理器安装，如 `sudo apt install git` (Ubuntu/Debian)

### 2. 创建GitHub账号

如果您还没有GitHub账号，请注册一个：
[https://github.com/join](https://github.com/join)

### 3. 创建GitHub仓库

1. 登录您的GitHub账号
2. 点击右上角的"+"图标，选择"New repository"
3. 填写仓库名称（例如: sql-manager）
4. 添加描述（可选）
5. 选择"Public"或"Private"
6. **不要**勾选"Initialize this repository with a README"
7. 点击"Create repository"
8. 复制仓库URL（HTTPS或SSH）

## 使用方法

### 方法1：使用更新脚本（推荐）

运行我们的综合更新脚本，选择GitHub同步选项：

```bash
cd /home/user/vibecoding/workspace/sql
python update.py
```

在菜单中选择选项6："同步到GitHub"

### 方法2：直接运行GitHub同步工具

```bash
cd /home/user/vibecoding/workspace/sql
python git_sync.py
```

## 同步流程

### 首次同步

当您第一次运行同步工具时，会经历以下步骤：

1. **检查Git配置**：工具会检查您的Git用户信息是否配置
2. **初始化仓库**（如果需要）：如果当前目录不是Git仓库，会提示您初始化
3. **创建.gitignore文件**：自动创建包含常见忽略规则的.gitignore文件
4. **添加远程仓库**：输入您的GitHub仓库URL
5. **提交代码**：第一次提交所有项目文件
6. **推送到GitHub**：将代码推送到您的GitHub仓库

### 后续同步

之后每次运行同步工具时，您可以：

1. **推送到GitHub**：将本地更改更新到GitHub
2. **从GitHub拉取**：获取GitHub上的最新更改
3. **管理远程仓库**：添加或更改远程仓库配置
4. **查看状态**：检查Git工作区状态

## 常见操作

### 推送本地更改到GitHub

```bash
python git_sync.py
```

选择选项1："推送到GitHub（更新代码）"

工具会自动：
- 检查是否有未提交的更改
- 提示您输入提交信息
- 将更改推送到GitHub

### 从GitHub获取最新代码

```bash
python git_sync.py
```

选择选项2："从GitHub拉取最新代码"

### 更改远程仓库URL

如果您需要更改GitHub仓库：

```bash
python git_sync.py
```

选择选项3："添加/更改远程GitHub仓库"

## 注意事项

### 数据安全

- **数据库文件**：默认情况下，数据库文件（*.db）会被.gitignore忽略，不会上传到GitHub
- **敏感信息**：确保不要将包含密码、密钥等敏感信息的文件上传到GitHub
- **配置文件**：包含环境变量的配置文件也应该被忽略

### 分支管理

- 默认使用`main`分支
- 如果您需要使用其他分支，可以在Git命令行中操作：
  ```bash
  git checkout -b feature-branch
  git push -u origin feature-branch
  ```

### 冲突解决

如果本地更改与GitHub上的更改冲突：

1. 工具会提示您有冲突
2. 您需要手动解决冲突文件中的冲突标记
3. 解决后提交更改：
   ```bash
   git add .
   git commit -m "Resolved conflicts"
   git push
   ```

## 错误处理

### 常见错误及解决方案

#### 1. Git未安装

**错误信息**：`未安装git，无法自动更新代码`

**解决方案**：
- 安装Git（参见准备工作部分）
- 重新运行同步工具

#### 2. 远程仓库权限问题

**错误信息**：`Permission denied (publickey)` 或 `Authentication failed`

**解决方案**：
- **HTTPS**: 确保您的GitHub用户名和密码正确
- **SSH**: 确保您的SSH密钥已添加到GitHub账号

#### 3. 远程仓库不存在

**错误信息**：`fatal: repository 'https://github.com/...' not found`

**解决方案**：
- 检查仓库URL是否正确
- 确保仓库已在GitHub上创建
- 检查您是否有权限访问该仓库

#### 4. 本地更改与远程冲突

**错误信息**：`Automatic merge failed; fix conflicts and then commit the result`

**解决方案**：
- 手动编辑冲突文件，解决冲突标记（<<<<<<<, =======, >>>>>>>）
- 提交解决后的更改

## 自动同步建议

为了保持项目最新，建议定期同步：

1. **开发前**：先从GitHub拉取最新代码
   ```bash
   python git_sync.py
   # 选择选项2
   ```

2. **完成开发后**：将更改推送到GitHub
   ```bash
   python git_sync.py
   # 选择选项1
   ```

## 高级功能

### 使用SSH连接（推荐）

为了避免每次输入密码，建议使用SSH连接：

1. 生成SSH密钥：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. 将公钥添加到GitHub：
   - 复制公钥内容：`cat ~/.ssh/id_ed25519.pub`
   - 在GitHub上，进入Settings > SSH and GPG keys > New SSH key
   - 粘贴公钥内容

3. 使用SSH URL克隆仓库：
   ```bash
   git remote set-url origin git@github.com:yourusername/yourrepo.git
   ```

### 配置.gitconfig

为了获得更好的Git体验，可以配置一些别名：

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
```

## 联系支持

如果您在使用GitHub同步工具时遇到任何问题，请提供以下信息：

- 操作系统版本
- Git版本
- 完整的错误信息
- 已尝试的解决方案

祝您使用愉快！
