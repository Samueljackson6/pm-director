# RuoYi Office Vben 部署情况报告

> 生成时间：2026-07-01 11:05
> 生成人：pm-director

---

## 📋 一、部署概况

### 1.1 部署目标

部署 RuoYi Office Vben 项目管理系统，用于项目管理、合同管理、财务管理等业务。

### 1.2 部署方式

- **模式**：单体模式（boot profile）
- **架构**：Spring Boot + Vue3 + MySQL + Redis
- **环境**：局域网服务器（Ubuntu 24.04）

### 1.3 部署结果

**✅ 部署成功**，但存在登录后路由问题需要修复。

---

## 📊 二、当前服务状态

### 2.1 服务清单

| 服务 | 状态 | 地址 | 进程ID |
|------|------|------|--------|
| 后端服务 | ✅ 运行中 | http://192.168.0.236:48080 | 3352613 |
| 前端服务 | ✅ 运行中 | http://192.168.0.236:5666 | 3352673+ |
| MySQL | ✅ 健康 | localhost:3306 | Docker容器 |
| Redis | ✅ 健康 | localhost:6379 | Docker容器 |

### 2.2 访问信息

**前端登录地址**：
```
http://192.168.0.236:5666/auth/login
```

**登录凭据**：
- 用户名：`admin`
- 密码：`admin123`

**API文档**：
- Swagger：http://192.168.0.236:48080/swagger-ui.html
- 健康检查：http://192.168.0.236:48080/actuator/health

---

## 🔧 三、部署过程详细记录

### 3.1 环境准备

**已完成**：
- ✅ Docker 29.1.3
- ✅ OpenJDK 17.0.19
- ✅ Maven 3.8.7
- ✅ Node.js + pnpm

### 3.2 数据库部署

**MySQL容器**：
```bash
docker run -d \
  --name ruoyi-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=ruoyi-office \
  mysql:8.0
```

**Redis容器**：
```bash
docker run -d \
  --name ruoyi-redis \
  -p 6379:6379 \
  redis:5.0
```

**数据库状态**：
- 数据库名：ruoyi-office
- 用户：root
- 密码：123456
- 状态：Up 14 hours (healthy)

### 3.3 后端编译

**代码位置**：
```
/home/samuel/ruoyi-office/
/home/samuel/ruoyi-office-vben/
```

**编译命令**：
```bash
cd /home/samuel/ruoyi-office
mvn clean package -DskipTests -Dmaven.test.skip=true -Pboot -T 1C
```

**编译结果**：
- ✅ BUILD SUCCESS
- JAR文件：191MB
- 位置：`/home/samuel/ruoyi-office/yudao-server/target/yudao-server.jar`

**修复的代码问题**：
1. **CrmContractStatusListener.java**
   - 问题：`event.getStatus()` 方法不存在
   - 修复：改为 `event.getProcessInstanceInfo().getStatus()`
   - 文件：`/home/samuel/ruoyi-office/yudao-module-crm/yudao-module-crm-server/src/main/java/cn/iocoder/yudao/module/crm/service/contract/listener/CrmContractStatusListener.java`

2. **CrmReceivableStatusListener.java**
   - 问题：同上
   - 修复：同上
   - 文件：`/home/samuel/ruoyi-office/yudao-module-crm/yudao-module-crm-server/src/main/java/cn/iocoder/yudao/module/crm/service/receivable/listener/CrmReceivableStatusListener.java`

### 3.4 后端启动

**启动命令**：
```bash
cd /home/samuel/ruoyi-office/yudao-server/target
nohup java -jar yudao-server.jar --spring.profiles.active=local > /tmp/ruoyi-backend.log 2>&1 &
```

**启动配置**：
- Profile：local
- 端口：48080
- 日志：`/tmp/ruoyi-backend.log`

**启动时间**：约25秒

**配置文件**：
- `/home/samuel/ruoyi-office/yudao-server/src/main/resources/application-local.yaml`
- MySQL连接：`jdbc:mysql://127.0.0.1:3306/ruoyi-office`
- Redis连接：`localhost:6379`

### 3.5 前端部署

**依赖安装**：
```bash
cd /home/samuel/ruoyi-office-vben
pnpm install
```

**启动命令**：
```bash
cd /home/samuel/ruoyi-office-vben/apps/web-antd
nohup pnpm dev > /tmp/ruoyi-frontend.log 2>&1 &
```

**启动配置**：
- 端口：5666
- 日志：`/tmp/ruoyi-frontend.log`

**关键配置文件**：

1. **环境变量**：`/home/samuel/ruoyi-office-vben/apps/web-antd/.env.development`
```properties
VITE_BASE_URL=http://192.168.0.236:48080/
VITE_GLOB_API_URL=/admin-api
```

2. **默认首页**：`/home/samuel/ruoyi-office-vben/apps/web-antd/src/preferences.ts`
```typescript
defaultHomePath: '/',  // 已修改，原来是 '/workspace'
```

---

## ⚠️ 四、当前存在的问题

### 4.1 主要问题：登录后跳转404

**现象**：
- 登录成功，提示"欢迎回来:芋道源码"
- 但跳转到404页面，显示"哎呀！未找到页面"
- 访问地址：http://192.168.0.236:5666/workspace

**原因分析**：
1. 前端配置默认首页为 `/workspace`
2. 数据库菜单表（system_menu）中没有 `/workspace` 路径的菜单项
3. 路由守卫无法找到对应的路由组件

**已尝试的解决方案**：
- ✅ 修改默认首页配置为 `/`（根路径）
- ⚠️ 需要清除浏览器缓存后重新登录测试

### 4.2 Docker权限问题

**现象**：
```bash
permission denied while trying to connect to the docker API
```

**解决方案**：
```bash
# 临时方案
newgrp docker

# 永久方案
sudo usermod -aG docker $USER
# 然后重新登录系统
```

**当前状态**：需要使用 `newgrp docker` 激活权限

---

## 📝 五、配置文件清单

### 5.1 后端配置

**主配置文件**：
```
/home/samuel/ruoyi-office/yudao-server/src/main/resources/application.yaml
/home/samuel/ruoyi-office/yudao-server/src/main/resources/application-local.yaml
```

**数据库配置**：
```yaml
spring:
  datasource:
    dynamic:
      datasource:
        master:
          url: jdbc:mysql://127.0.0.1:3306/ruoyi-office?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&nullCatalogMeansCurrent=true&rewriteBatchedStatements=true
          username: root
          password: 123456
```

**Redis配置**：
```yaml
spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      database: 0
```

### 5.2 前端配置

**环境变量**：
```
/home/samuel/ruoyi-office-vben/apps/web-antd/.env
/home/samuel/ruoyi-office-vben/apps/web-antd/.env.development
```

**API地址配置**（已修改）：
```properties
VITE_BASE_URL=http://192.168.0.236:48080/
```

**路由配置**：
```
/home/samuel/ruoyi-office-vben/apps/web-antd/src/router/routes/core.ts
/home/samuel/ruoyi-office-vben/apps/web-antd/src/preferences.ts
```

### 5.3 数据库配置

**连接信息**：
- 主机：localhost:3306
- 数据库：ruoyi-office
- 用户：root
- 密码：123456

**关键表**：
- `system_users` - 用户表
- `system_menu` - 菜单权限表
- `system_dept` - 部门表（已添加 org_type 字段）

---

## 🔄 六、服务管理命令

### 6.1 启动服务

**后端服务**：
```bash
cd /home/samuel/ruoyi-office/yudao-server/target
nohup java -jar yudao-server.jar --spring.profiles.active=local > /tmp/ruoyi-backend.log 2>&1 &
```

**前端服务**：
```bash
cd /home/samuel/ruoyi-office-vben/apps/web-antd
nohup pnpm dev > /tmp/ruoyi-frontend.log 2>&1 &
```

**数据库容器**：
```bash
newgrp docker << 'EOF'
docker start ruoyi-mysql ruoyi-redis
EOF
```

### 6.2 停止服务

**后端服务**：
```bash
ps aux | grep yudao-server.jar | grep -v grep | awk '{print $2}' | xargs -r kill -9
```

**前端服务**：
```bash
pkill -9 -f "pnpm dev"
pkill -9 -f "vite"
```

### 6.3 查看日志

**后端日志**：
```bash
tail -f /tmp/ruoyi-backend.log
```

**前端日志**：
```bash
tail -f /tmp/ruoyi-frontend.log
```

### 6.4 检查服务状态

**进程检查**：
```bash
ps aux | grep -E "yudao-server.jar|vite" | grep -v grep
```

**端口检查**：
```bash
netstat -tlnp | grep -E "48080|5666|3306|6379"
```

**健康检查**：
```bash
curl http://192.168.0.236:48080/actuator/health
curl -I http://192.168.0.236:5666/
```

---

## 📋 七、维护清单

### 7.1 日常维护

**检查项**：
1. 后端服务是否运行
2. 前端服务是否运行
3. MySQL容器是否健康
4. Redis容器是否健康
5. 磁盘空间是否充足
6. 日志文件大小

**维护频率**：每日

### 7.2 数据备份

**需要备份的内容**：
1. MySQL数据库（ruoyi-office）
2. 后端配置文件
3. 前端配置文件
4. 上传的文件（如有）

**备份命令示例**：
```bash
# 数据库备份
newgrp docker << 'EOF'
docker exec ruoyi-mysql mysqldump -uroot -p123456 ruoyi-office > /backup/ruoyi-office-$(date +%Y%m%d).sql
EOF

# 配置备份
tar -czf /backup/ruoyi-config-$(date +%Y%m%d).tar.gz \
  /home/samuel/ruoyi-office/yudao-server/src/main/resources/*.yaml \
  /home/samuel/ruoyi-office-vben/apps/web-antd/.env*
```

### 7.3 日志管理

**日志位置**：
- 后端：`/tmp/ruoyi-backend.log`
- 前端：`/tmp/ruoyi-frontend.log`

**日志轮转建议**：
```bash
# 每周归档一次
mv /tmp/ruoyi-backend.log /tmp/ruoyi-backend-$(date +%Y%m%d).log
mv /tmp/ruoyi-frontend.log /tmp/ruoyi-frontend-$(date +%Y%m%d).log
```

---

## 🚀 八、下一步计划

### 8.1 紧急任务（优先级：高）

1. **修复登录跳转问题**
   - 清除浏览器缓存
   - 重新测试登录流程
   - 如果仍然404，检查数据库菜单配置

2. **数据迁移**
   - 从SQLite迁移224条项目数据
   - 迁移脚本：`/home/samuel/.openclaw/workspace/pm-director/database/project_management.db`
   - 目标表：contracts, finance_records, stages, payments, deliverables

### 8.2 短期任务（优先级：中）

1. **业务定制**
   - 合同管理模块定制
   - 财务管理模块定制
   - 项目管理模块定制

2. **数据同步**
   - 飞书表格数据同步
   - 历史数据导入
   - 定期更新机制

3. **监控部署**
   - 服务监控
   - 日志监控
   - 性能监控

### 8.3 长期任务（优先级：低）

1. **安全加固**
   - 修改默认密码
   - 配置HTTPS
   - 设置防火墙规则

2. **性能优化**
   - JVM参数调优
   - 数据库索引优化
   - 缓存策略优化

3. **文档完善**
   - 用户使用手册
   - 管理员手册
   - API文档

---

## 🔗 九、相关文档

### 9.1 项目文档

- 部署完成报告：`/home/samuel/.openclaw/workspace/pm-director/docs/RuoYi-Office-Vben部署完成报告-20260701.md`
- 本报告：`/home/samuel/.openclaw/workspace/pm-director/docs/RuoYi-Office-Vben部署情况报告-20260701-1105.md`

### 9.2 官方文档

- 官方网站：https://ruoyioffice.com
- 快速开始：http://ruoyioffice.com/quick-start/
- 视频教程：https://ruoyioffice.com/02Yf6M7Qn
- GitHub：https://gitee.com/yqzy1688/ruoyi-office.git

### 9.3 关键文件路径

```
# 项目代码
/home/samuel/ruoyi-office/                    # 后端代码
/home/samuel/ruoyi-office-vben/               # 前端代码

# 配置文件
/home/samuel/ruoyi-office/yudao-server/src/main/resources/application-local.yaml
/home/samuel/ruoyi-office-vben/apps/web-antd/.env.development
/home/samuel/ruoyi-office-vben/apps/web-antd/src/preferences.ts

# 日志文件
/tmp/ruoyi-backend.log                        # 后端日志
/tmp/ruoyi-frontend.log                       # 前端日志

# JAR文件
/home/samuel/ruoyi-office/yudao-server/target/yudao-server.jar
```

---

## 📞 十、联系信息

**部署人**：pm-director
**部署时间**：2026-07-01
**服务器**：Ubuntu 24.04 (192.168.0.236)

**需要oc-ops协助**：
1. 修复登录后路由跳转问题
2. 配置服务自启动
3. 设置日志轮转
4. 数据备份策略
5. 安全加固建议

---

**报告生成时间**：2026-07-01 11:05
**报告版本**：v1.0
