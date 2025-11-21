# API 文档示例

## 概述

这是一个技术文档示例，展示 GitHub 主题的效果。

## 安装

```bash
npm install example-api
```

## 快速开始

```javascript
const API = require('example-api');

const client = new API({
    apiKey: 'your-api-key',
    endpoint: 'https://api.example.com'
});

// 获取用户信息
const user = await client.getUser('user-id');
console.log(user);
```

## API 参考

### Authentication

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/logout` | 用户登出 |
| GET | `/auth/refresh` | 刷新令牌 |

### Users

#### GET /users/:id

获取用户信息

**参数:**
- `id` (string): 用户ID

**响应:**
```json
{
    "id": "user-123",
    "name": "John Doe",
    "email": "john@example.com"
}
```

## 转换命令

```bash
./scripts/convert.sh technical-doc.md github
```
