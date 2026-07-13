# 企查查 MCP 生产环境部署指南

## 一、部署前准备

### 1.1 环境要求
- Node.js 18+ 或 Python 3.8+
- 网络能访问 `https://agent.qcc.com`
- MCP 客户端支持（Claude Desktop、Cursor、或其他 AI IDE）

### 1.2 凭证准备
- 企查查 API Token（已获取）
- 积分余额检查（初始 500 积分）

---

## 二、配置步骤

### 2.1 Claude Desktop 配置

编辑配置文件：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下内容：

\`\`\`json
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-risk": {
      "url": "https://agent.qcc.com/mcp/risk/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-ipr": {
      "url": "https://agent.qcc.com/mcp/ipr/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-operation": {
      "url": "https://agent.qcc.com/mcp/operation/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-executive": {
      "url": "https://agent.qcc.com/mcp/executive/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-history": {
      "url": "https://agent.qcc.com/mcp/history/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-legal-regulation": {
      "url": "https://agent.qcc.com/mcp/regulation/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-legal-case": {
      "url": "https://agent.qcc.com/mcp/case/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    },
    "qcc-document": {
      "url": "https://agent.qcc.com/mcp/document/stream",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
\`\`\`

### 2.2 Cursor IDE 配置

编辑 `~/.cursor/mcp_settings.json`，添加相同配置。

### 2.3 环境变量管理（推荐）

使用环境变量管理 Token：

\`\`\`bash
# 设置环境变量
export QCC_API_TOKEN="YOUR_TOKEN_HERE"

# 在配置文件中使用
{
  "headers": {
    "Authorization": "Bearer ${QCC_API_TOKEN}"
  }
}
\`\`\`

---

## 三、网络安全配置

### 3.1 防火墙规则
确保服务器能访问：
- `agent.qcc.com` (HTTPS, 443端口)

### 3.2 代理配置（如需要）

\`\`\`bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
\`\`\`

---

## 四、监控与日志

### 4.1 API 调用日志

建议记录以下信息：
- 调用时间
- 查询企业名称/信用代码
- 查询类型（工商/风险/知识产权等）
- 响应时间
- 积分消耗

### 4.2 积分监控

定期检查积分余额：
\`\`\`bash
# 建议每周检查一次积分余额
curl -X POST https://agent.qcc.com/mcp/company/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
\`\`\`

---

## 五、故障排查

### 5.1 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| 401 Unauthorized | Token 无效或过期 | 检查 Token 是否正确 |
| 403 Forbidden | 权限不足 | 联系企查查开通相应权限 |
| 429 Too Many Requests | 请求频率过高 | 降低调用频率 |
| 地域限制 | 查询对象不在中国大陆 | 确认查询企业范围 |

### 5.2 测试连通性

使用提供的测试脚本：
\`\`\`bash
node test-qcc-mcp.js
\`\`\`

---

## 六、生产环境最佳实践

### 6.1 缓存策略
- 企业工商信息：缓存 24 小时
- 风险信息：缓存 4 小时
- 知识产权信息：缓存 12 小时

### 6.2 限流策略
- 单个企业查询：间隔 ≥ 1 秒
- 批量查询：使用队列，控制并发 ≤ 5

### 6.3 数据存储
- 查询结果建议存储到数据库
- 定期同步更新关键企业信息

---

## 七、联系方式

- 企查查智能体平台：https://agent.qcc.com
- 技术支持：联系企查查客服
- MCP 协议文档：https://modelcontextprotocol.io

---

**部署清单**：
- [ ] 配置文件已更新
- [ ] Token 已正确设置
- [ ] 网络连通性测试通过
- [ ] 功能测试通过
- [ ] 监控日志已配置
- [ ] 积分余额充足

**部署完成后运行**：
\`\`\`bash
node test-qcc-mcp.js
\`\`\`
