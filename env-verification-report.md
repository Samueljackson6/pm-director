# 本地开发测试环境验证报告 — pm-director

**验证人**: 严过关 (QA Engineer)
**验证时间**: 2026-07-07
**环境**: 本沙箱 Docker (docker compose 启动)
**容器**: pm-director-backend (8800) / pm-director-frontend (nginx:alpine, 8900, 挂载宿主机 dist)

---

## 一、容器状态 (PASS)

| 容器 | 状态 | 端口映射 | 运行时长 |
|---|---|---|---|
| pm-director-backend | Up | 0.0.0.0:8800->8800/tcp | Up 2 hours |
| pm-director-frontend | Up | 0.0.0.0:8900->80/tcp | Up 2 hours |

> `docker ps --filter name=pm-director` 两容器均 `Up`。**PASS**

---

## 二、后端 API (端口 8800)

| 检查项 | 预期 | 实际观测 | 结果 |
|---|---|---|---|
| `/api/stats` | 返回 JSON，data 含 contract_count / total_amount 等 | `{"code":0,"data":{"contract_count":50,"total_amount":2364.79,"invoiced":1049.13,"received":707.15,"receipt_rate":67.4,"sub_invoiced":399.96,"sub_paid":287.03,"stages":83,"payments":72,"deliverables":125}}` | **PASS** |
| `/health` | 404（后端无此路由） | HTTP 404 | **PASS** (符合预期) |
| `/api/projects?page=1&size=1` | 200 + 数据数组 | 200, `total:50`, `items:[1条]` | **PASS** |
| `/api/contracts?page=1&size=1` | 200 + 数据数组 | 200, `total:50`, `items:[1条]` | **PASS** |

**说明**: `/api/stats` 返回字段完整（共 11 个 data 字段），可作为后端健康探活基准——**后端健康探活应以 `/api/stats` 返回 200 为准**，而非 `/health`（404 属正常，/health 由 nginx 层提供）。

---

## 三、前端 (nginx 端口 8900)

| 检查项 | 预期 | 实际观测 | 结果 |
|---|---|---|---|
| `GET /` | 301 重定向到 /web/ | 301, `Location: http://localhost:8900/web/` | **PASS** |
| `GET /web/` | 200（SPA 入口 HTML） | 200, `text/html`, **3178 字节完整 HTML** | **PASS** |
| `GET /web/dashboard`（深链回退） | 200（SPA fallback） | 200, **3178 字节完整 HTML**（与 /web/ 同源同 md5） | **PASS** |
| `GET /health` | 200（nginx 健康检查） | 200, body `OK` | **PASS** |
| 产物 `dist/index.html` 存在 | 文件存在 | `/d/Tare-workspace/pm-director/ui-vben/apps/web-antd/dist/index.html`, 3178 字节 | **PASS** |

> **SPA 回退验证**: deep route `/web/dashboard` 经 nginx `try_files $uri $uri/ /web/index.html` 正确回退到入口 HTML（与 `/web/` 的 md5 一致），客户端路由刷新无问题。

---

## 四、一致性风险 (WARN — 非阻断)

| 风险 | 说明 | 建议 |
|---|---|---|
| Stale dist | frontend 使用 `nginx:alpine` + 卷挂载宿主机 `dist`，**不自动构建**。若宿主机未重新 build 即重启容器，容器 serving 的是旧产物。 | 部署/更新前端代码后，先 `pnpm build` 再 restart 前端容器；建议在 CI 增加 build + 产物校验步骤；代码评审时确认 dist 为最新后再挂载。 |

**当前观测**: 线上 served HTML 资源版本号 `?v=5.6.0-a363dae2`，宿主机 `dist/index.html` mtime 2026-07-06 17:59，与容器内内容一致（md5 相同），**当前未观察到陈旧**，但该机制本身存在风险，列为 WARN。

---

## 五、总体结论

- **该环境可正常用于日常开发测试。**
- 检查项统计: **9 项 PASS / 0 项 FAIL / 1 项 WARN（非阻断）**。
- 容器、后端业务接口、前端路由与 SPA 回退、静态产物均工作正常。
- **未发现任何源码 Bug。**

### 智能路由判定: **NoOne / 通过**
- 所有检查通过；`/health` 404 为文档化预期行为，非 Bug。
- stale dist 属部署流程风险（WARN），非源码缺陷，无需转交 Engineer (Alex)。
- 测试/Bash 自身无问题（`-w %{size_download}` 偶现 0 为 curl 度量假象，已用文件落盘 + md5 交叉验证确认内容完整送达）。

---

*方法论备注*: 部分 `curl -w '%{size_download}'` 在管道/`-o /dev/null` 组合下偶发返回 0（exit code 23），为避免误判，关键字节数改用 `curl -o file && wc -c && md5sum` 实测，确认 `/web/`、`/web/index.html`、`/web/dashboard` 均为同一份 3178 字节完整 HTML。
