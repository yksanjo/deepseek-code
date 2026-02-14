# DeepSeek Code Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek](https://img.shields.io/badge/Powered%20by-DeepSeek--V3-green.svg)](https://www.deepseek.com/)

**AI coding assistant with REST API server** - Deploy DeepSeek Code as a service.

**AI 编程助手 REST API 服务器** - 将 DeepSeek Code 部署为服务。

<p align="center">
  <img src="https://img.shields.io/badge/REST-API-blue" alt="REST API">
  <img src="https://img.shields.io/badge/FastAPI-red" alt="FastAPI">
  <img src="https://img.shields.io/badge/Multi--tenant-orange" alt="Multi-tenant">
</p>

```
  ____                 ____            _       _
 |  _ \  ___  ___ _ __/ ___|  ___  ___| | __ | |
 | | | |/ _ \/ _ \ '_ \___ \ / _ \/ _ \ |/ /| |
 | |_| |  __/  __/ |_) |__) |  __/  __/   < |_|
 |____/ \___|\___| .__/____/ \___|\___|_|\_\|_|
    ____          |_|  _                      _
   / ___|___   __| | __| |__   __ _
  | |   / _ \ / _` | '_ \ '_ \ / _` |
  | |__| (_) | (_| | |_) | | | | (_| |
   \____\___/ \__,_|\__/\__/_|\__,_|
```

---

## Why DeepSeek Code Server? | 为什么选择 DeepSeek Code Server?

<details>
<summary>🇨🇳 中文</summary>

- **REST API**: 通过 HTTP API 提供 AI 编程助手能力
- **多租户**: 支持多个用户/项目隔离
- **可扩展**: 支持水平扩展和负载均衡
- **Webhooks**: 支持回调通知
- **认证**: 内置 API 密钥认证

### 主要功能

| 功能 | 描述 |
|------|------|
| **REST API** | 完整的 CRUD 操作 |
| **WebSocket** | 实时流式响应 |
| **多租户** | 项目/用户隔离 |
| **API 密钥** | 认证和访问控制 |
| **Webhooks** | 任务完成回调 |
| **历史记录** | 会话持久化 |

</details>

<details open>
<summary>🇺🇸 English</summary>

- **REST API**: Expose AI coding assistant via HTTP endpoints
- **Multi-tenant**: Support multiple users/projects with isolation
- **Scalable**: Horizontal scaling with load balancers
- **Webhooks**: Task completion callbacks
- **Authentication**: Built-in API key auth

## Features

| Feature | Description |
|---------|-------------|
| **REST API** | Full CRUD operations |
| **WebSocket** | Real-time streaming responses |
| **Multi-tenancy** | Project/user isolation |
| **API Keys** | Authentication & access control |
| **Webhooks** | Task completion callbacks |
| **History** | Session persistence |

</details>

## Installation

```bash
# Clone and install
git clone https://github.com/yksanjo/deepseek-code-server.git
cd deepseek-code-server
pip install -e .
```

### Setup API Key

```bash
export DEEPSEEK_API_KEY=your_key_here
```

## Quick Start

### Start Server

```bash
# Start the API server
deepseek-code-server

# Or with custom port
deepseek-code-server --host 0.0.0.0 --port 8080
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "my-project"}'

# Send message
curl -X POST http://localhost:8000/api/sessions/{session_id}/messages \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "Fix the bug in main.py"}'

# Get session history
curl http://localhost:8000/api/sessions/{session_id} \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sessions/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content); // Streamed response
};
```

## API Reference

### Authentication

All API requests require an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" ...
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/sessions` | Create session |
| GET | `/api/sessions` | List sessions |
| GET | `/api/sessions/{id}` | Get session |
| DELETE | `/api/sessions/{id}` | Delete session |
| POST | `/api/sessions/{id}/messages` | Send message |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| GET | `/api/keys` | List API keys |
| POST | `/api/keys` | Create API key |

### Request/Response Examples

#### Create Session

```json
// Request
POST /api/sessions
{
  "project_id": "my-project",
  "model": "deepseek-chat",
  "options": {
    "trust_mode": false,
    "max_turns": 50
  }
}

// Response
{
  "id": "sess_abc123",
  "project_id": "my-project",
  "created_at": "2025-01-01T00:00:00Z",
  "status": "active"
}
```

#### Send Message

```json
// Request
POST /api/sessions/sess_abc123/messages
{
  "content": "Add docstrings to utils.py"
}

// Response (with streaming)
{
  "type": "message",
  "content": "I'll help you add docstrings...",
  "tool_calls": [...],
  "done": false
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | Required |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DATABASE_URL` | SQLite/PostgreSQL URL | `sqlite:///./data.db` |
| `API_KEY_SECRET` | Secret for API key signing | Random |
| `WEBHOOK_SECRET` | Secret for webhook signing | Random |

### Config File

```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

deepseek:
  api_key: ${DEEPSEEK_API_KEY}
  model: deepseek-chat
  max_retries: 3

database:
  url: sqlite:///./data.db

auth:
  api_key_enabled: true
  webhook_enabled: true
```

## Architecture

```
deepseek_code_server/
├── server.py              # FastAPI application
├── api/
│   ├── routes/
│   │   ├── sessions.py   # Session CRUD
│   │   ├── projects.py   # Project management
│   │   └── keys.py       # API key management
│   └── middleware/
│       └── auth.py       # Authentication
├── models/
│   ├── session.py        # Session model
│   ├── project.py        # Project model
│   └── key.py           # API key model
├── services/
│   ├── agent.py          # Agent service
│   └── webhook.py        # Webhook service
└── main.py               # Entry point
```

## Webhooks

Configure webhooks to receive notifications:

```bash
export WEBHOOK_URL=https://your-server.com/webhook
export WEBHOOK_SECRET=your_secret
```

Webhook payload:

```json
{
  "event": "session.completed",
  "session_id": "sess_abc123",
  "project_id": "my-project",
  "timestamp": "2025-01-01T00:00:00Z",
  "data": {
    "messages": [...],
    "tool_results": [...]
  }
}
```

## Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["deepseek-code-server"]
```

```bash
docker build -t deepseek-code-server .
docker run -p 8000:8000 -e DEEPSEEK_API_KEY=xxx deepseek-code-server
```

## Use Cases

- **CI/CD Integration**: AI code review in pipelines
- **Team-wide AI Assistant**: Shared coding assistant
- **IDE Plugins**: Custom IDE extensions
- **Documentation**: Auto-generate docs
- **Code Migration**: Legacy code modernization

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Star this repo if you find it useful!</b>
</p>
