# SQL语句管理工具

一个现代化的SQL语句管理工具，支持多用户协作，帮助团队高效管理和共享SQL语句。

## 功能特点

### 核心功能
- **SQL编辑器**：支持语法高亮、自动补全和格式化
- **多数据库支持**：兼容SQLite、MySQL、PostgreSQL和SQL Server
- **SQL模板**：提供常用SQL模板，支持自定义模板
- **执行结果可视化**：以表格形式展示查询结果
- **分类和标签**：通过分类和标签组织SQL语句
- **备注功能**：为SQL语句添加详细说明和文档

### 多用户协作功能
- **用户认证**：支持邮箱/密码、Google和GitHub登录
- **共享SQL语句**：所有用户可以查看共享的SQL语句
- **权限控制**：只有创建者可以修改和删除自己的SQL语句
- **评论系统**：对SQL语句进行讨论和反馈
- **分享功能**：生成分享链接分享SQL语句

## 技术栈
- HTML5/CSS3/JavaScript
- Tailwind CSS
- CodeMirror（SQL编辑器）
- Tabulator（数据表格）
- Firebase（用户认证和数据存储）

## 如何使用

### 本地运行
1. 克隆项目到本地
2. 打开 `index.html` 文件

### Firebase配置
要使用多用户协作功能，需要配置Firebase：

1. 创建Firebase项目
2. 在 `index.html` 文件中更新Firebase配置：
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

3. 启用Firebase Authentication（电子邮件/密码、Google、GitHub）
4. 创建Firestore数据库并设置安全规则：
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /sqlSnippets/{document=**} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.createdBy.id;
    }
    
    match /categories/{document=**} {
      allow read: if request.auth != null;
      allow create, update, delete: if request.auth != null;
    }
    
    match /tags/{document=**} {
      allow read: if request.auth != null;
      allow create, update, delete: if request.auth != null;
    }
    
    match /sqlSnippets/{sqlId}/comments/{document=**} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.createdBy.id;
    }
  }
}
```

## 使用指南

### 基本操作
1. **登录/注册**：使用邮箱/密码、Google或GitHub账号登录
2. **创建SQL语句**：点击"新建SQL"按钮创建新的SQL语句
3. **编辑SQL语句**：在编辑器中编写和修改SQL语句
4. **执行SQL语句**：点击"执行SQL"按钮或使用快捷键Ctrl+Enter执行SQL
5. **保存SQL语句**：点击"保存SQL"按钮或使用快捷键Ctrl+S保存SQL语句

### 协作功能
1. **查看他人SQL语句**：在左侧列表中浏览所有共享的SQL语句
2. **评论SQL语句**：切换到"评论"标签页，添加和查看评论
3. **分享SQL语句**：点击"分享"按钮生成分享链接
4. **通过链接打开SQL语句**：访问分享链接直接打开特定的SQL语句

## 快捷键
- **Ctrl+S**：保存SQL语句
- **Ctrl+Enter**：执行SQL语句
- **Ctrl+N**：新建SQL语句
- **Ctrl+O**：打开SQL语句

## 注意事项
- 所有SQL语句默认是公开的，所有登录用户都可以查看
- 只有SQL语句的创建者可以修改和删除该语句
- 评论功能允许所有用户参与讨论
- 分享链接可以被任何人访问，但需要登录才能查看完整内容

## 未来计划
- 添加更多数据库支持
- 实现SQL语句的版本控制
- 添加更高级的权限管理
- 支持团队和项目管理
- 增加SQL语句的导入/导出功能
