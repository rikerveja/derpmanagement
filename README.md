mysql数据存储


以下是 **DERP 服务器租赁与管理系统** 的完整需求汇总：

---

### **1. 用户管理**

- **注册与登录**：
  - 用户通过邮箱注册，支持邮箱验证。
  - 用户可通过序列号绑定租赁套餐，生成 ACL 配置和服务器权限。
  - 用户登录分为管理员和普通用户登录，权限不同。
  
- **用户界面**：
  - 查看当前租赁信息：租赁时长、到期时间、剩余流量。
  - 支持主动续费：根据套餐延长租赁时间。
  - 提供 ACL 配置下载，绑定三台 DERP 服务器。
  
- **用户到期处理**：
  - 到期后自动释放服务器资源。
  - 提供用户历史记录查询，保留已注销用户的使用记录。
  
- **序列号激活**：
  - 用户可输入管理员生成的序列号激活租赁服务。
  - 每个序列号绑定一个用户，仅可使用一次。

- **用户注销功能**：
  - 注销前销毁 ACL 文件、包含的服务器对应 Docker 容器（通过 SSH 登录释放）。
  - 检查用户财务结算是否完整（包括续费）。
  - 到期未续费或管理员操作不续费时，保留用户权限，但关停其 DERP 服务。
  - 超过 30 天未续费的用户将自动注销。
  - 用户注册时，邮箱每隔 10 分钟只能发送 5 封邮件。

---

### **2. ACL 管理**

- **ACL 生成**：
  - 动态生成用户 ACL 配置，包含三台服务器（高可用）。
  - 配置绑定用户注册设备，限制使用范围。
  
- **ACL 更新**：
  - 设置 32 天自动失效机制，到期时重新生成 ACL。
  - 支持管理员手动更新 ACL 配置。
  
- **ACL 日志记录**：
  - 每次生成 ACL 时记录用户 IP 地址、地理位置、生成时间和配置版本。
  - 管理员可查询 ACL 生成历史日志。
  
- **ACL 校验**：
  - 下载 ACL 文件需校验序列号是否已付费（已使用序列号）。
  - 不同用户之间无法查看 ACL 配置文件。
  - 下载时记录用户名、IP、机器校验码、浏览器信息等数据，允许管理员、超级管理员和分销账号查看 ACL 文件下载情况。

---

### **3. 服务器管理**

- **服务器列表**：
  - 显示服务器的 IP 地址、地区、用户数、流量消耗、速率。
  - 按地区统计服务器的用户数和负载状态。

- **服务器资源管理**：
  - 支持自动关闭超流量的服务器 Docker 容器。
  - 提供健康检测与时延检测，记录历史趋势图。

- **服务器删除与用户通知**：
  - 管理员可删除异常或负载高的服务器，并通知相关用户更新 ACL。

- **服务器扩展信息**：
  - 每台服务器对应的阿里云账号（手机号）。
  - 显示 IP 所在国内地址、公网 IP 地址、用户数（DERP 服务器主要是 Docker 容器数量）、总体流量及月度剩余流量。

---

### **4. Docker 容器管理**

- **容器隔离**：
  - 每个用户分配独立 Docker 容器和端口，避免端口冲突。

- **容器生命周期管理**：
  - 到期后自动释放用户的容器。
  - 新续费时延长容器使用时间或重新分配。

- **流量统计**：
  - 按容器记录用户流量，包括实时速率和总流量。

---

### **5. 财务管理**

- **套餐定价与序列号管理**：
  - 管理员设置租赁套餐（3天、5天、30天、180天、360天）。
  - 自动生成复杂序列号，供用户激活租赁。

- **财务统计**：
  - 显示当月收益、历史总收益。
  - 统计用户预付款余额和套餐购买数量。

- **订单管理**：
  - 查看用户订单历史，支持完成、续费和取消状态标记。

- **分销系统财务管理**：
  - 管理员查看分销员账号的财务信息，包括分销员的分销金额。

---

### **6. 分销管理**

- **分销员类别**：
  - 分销员分为：黄金分销员（10%）、白金分销员（15%）、铂金分销员（20%）三类，按营业额比例分成。

- **序列号生成与分销**：
  - 分销员可以生成序列号，用以开辟服务器资源和权限。
  - 分销员申请生成序列号，管理员审核后发送。
  - 分销员购买序列号时，按分销员类别打折。

- **支付与结算**：
  - 分销员可以在网站上支付购买序列号，或等待超级管理员确认收款后发送。

---

### **7. 系统安全性**

- **设备绑定**：
  - ACL 配置仅允许用户注册设备访问。

- **流量异常监控**：
  - 检测用户流量异常情况（速率过高或超限）。

- **权限与日志**：
  - 管理员界面支持多级权限分配。
  - 提供系统操作日志，追踪管理员和用户的关键操作。

---

### **8. 收费模块**

- **支付方式**：
  - 提供支付宝和微信两大收款账号信息。

---

### **9. 续费功能**

- **管理员续费**：
  - 允许管理员帮助用户续费至指定日期。
  
- **续费通知**：
  - 预设 7 天、3 天和 1 天续费通知。
  
- **自动注销**：
  - 超过 30 天未续费的用户将自动注销。

---

### **10. 序列号管理**

- **序列号生成与过期**：
  - 新生成的序列号 30 天后自动过期。
  - 序列号管理板块：记录用户使用情况、状态查看、服务器关联匹配、与 Docker 容器的关联等。
  - 序列号与分销系统相融合，提升功能与管理效率。

---

### **11. 技术栈**

- **前端**：
  - React（用户与管理员界面，动态展示用户与服务器状态）。

- **数据库**：
  - MySQL（数据存储）。

- **后端**：
  - Flask 或 FastAPI（实现核心逻辑）。
  - 使用 Celery 和 Redis 处理异步任务（如容器释放、ACL 到期等）。

- **消息通知**：
  - 使用 SMTP 发送邮件通知（如续费提醒、ACL 更新）。

---

### **12. 部署与实施步骤**

1. **开发阶段**：
   - 开发核心功能：用户注册登录、序列号激活、ACL 配置生成与更新。
   - Docker 容器管理和服务器负载监控。
   - 财务统计和管理员操作界面。
   
2. **初始部署**：
   - 使用一台轻量云服务器部署系统，安装 Docker 和所需依赖。
   - 初始化 MySQL 数据库，创建表结构。

3. **生产部署**：
   - 引入负载均衡（如 Nginx）和 Redis 缓存提升性能。

4. **监控与报警**：
   - 部署 Prometheus 和 Grafana 配置流量和系统异常报警。

---

### **总结**

- 系统设计为模块化，确保各个功能独立、可扩展。
- 自动化与安全性得到高度重视，如自动续费、ACL 配置的严格权限控制、多因素认证等。
- 续费功能与日志系统、支付系统与分销系统高度整合，以提高管理效率与用户体验。

---
### 阶段性工作汇总

---

#### **1. 项目背景**
- **项目名称**: DERP Management
- **项目目标**:
  - 提供用户、服务器、容器和 ACL 管理功能。
  - 支持分销、监控、告警和高可用。
  - 支持基于序列号的租赁管理。
  - 提供基于 Flask 的后端和可扩展的 API 接口。

---

#### **2. 当前进展**
##### **2.1 数据库相关**
- **数据库初始化状态**: 数据库 `app.db` 已初始化，迁移脚本成功生成并应用。
- **已检测到的表**:
  ```plaintext
  acl_logs
  monitoring_logs
  serial_numbers
  server_logs
  servers
  system_alerts
  system_logs
  user_containers
  user_history
  user_logs
  user_server_association
  users
  ```

##### **2.2 API 路由**
- 已整合多个蓝图（Blueprints），包括：
  - 用户模块 (`user_routes`)
  - 服务器模块 (`server_routes`)
  - 容器管理模块 (`container_routes`)
  - ACL 管理模块 (`acl_routes`)
  - 财务模块 (`finance_routes`)
  - 高可用模块 (`ha_routes`)
  - 日志管理模块 (`logs_routes`)
  - 通知模块 (`notifications_routes`)
  - 分销管理模块 (`admin_routes`)
  - 流量模块 (`traffic_routes`)
  - 告警模块 (`alerts_routes`)
  - 监控模块 (`monitoring_routes`)
  - 序列号模块 (`serial_routes`)
  - 安全与设备绑定模块 (`security_routes`)

##### **2.3 配置相关**
- 配置文件 `app/config.py` 完整加载 `.env` 文件。
- 数据库使用 SQLite，支持未来切换为其他数据库（如 PostgreSQL）。
- 邮件、Redis 和 Celery 均已配置。

---

### 数据库表设计

以下是项目中数据库表的详细设计：

| 表名                 | 字段                                   | 类型             | 描述                                                     |
|----------------------|---------------------------------------|------------------|----------------------------------------------------------|
| `users`              | `id`                                 | Integer (PK)     | 用户 ID                                                  |
|                      | `username`                           | String (unique)  | 用户名                                                   |
|                      | `email`                              | String (unique)  | 邮箱地址                                                 |
|                      | `password`                           | String           | 密码                                                     |
|                      | `role`                               | String           | 用户角色（如 `user`, `admin`）                           |
|                      | `rental_expiry`                      | DateTime         | 租赁到期时间                                             |
|                      | `created_at`                         | DateTime         | 用户创建时间                                             |
| `serial_numbers`     | `id`                                 | Integer (PK)     | 序列号 ID                                                |
|                      | `code`                               | String (unique)  | 序列号代码                                               |
|                      | `duration_days`                      | Integer          | 有效天数                                                 |
|                      | `status`                             | String           | 序列号状态（`unused`, `used`, `expired`）                |
|                      | `user_id`                            | Integer (FK)     | 用户 ID（外键）                                          |
|                      | `created_at`                         | DateTime         | 序列号创建时间                                           |
|                      | `used_at`                            | DateTime         | 序列号使用时间                                           |
| `servers`            | `id`                                 | Integer (PK)     | 服务器 ID                                                |
|                      | `ip`                                 | String           | IP 地址                                                  |
|                      | `region`                             | String           | 服务器所在地区                                           |
|                      | `load`                               | Float            | 当前负载                                                 |
|                      | `status`                             | String           | 服务器状态（`healthy`, `unhealthy`）                     |
|                      | `created_at`                         | DateTime         | 创建时间                                                 |
|                      | `updated_at`                         | DateTime         | 更新时间                                                 |
| `acl_logs`           | `id`                                 | Integer (PK)     | 日志 ID                                                  |
|                      | `user_id`                            | Integer (FK)     | 用户 ID（外键）                                          |
|                      | `ip_address`                         | String           | 用户 IP 地址                                             |
|                      | `location`                           | String           | 地理位置                                                 |
|                      | `acl_version`                        | String           | ACL 版本号                                               |
|                      | `created_at`                         | DateTime         | 创建时间                                                 |
| `monitoring_logs`    | `id`                                 | Integer (PK)     | 日志 ID                                                  |
|                      | `server_id`                          | Integer (FK)     | 服务器 ID（外键）                                        |
|                      | `metric`                             | String           | 监控指标                                                 |
|                      | `value`                              | Float            | 监控值                                                   |
|                      | `timestamp`                          | DateTime         | 时间戳                                                   |
| `system_alerts`      | `id`                                 | Integer (PK)     | 告警 ID                                                  |
|                      | `alert_type`                         | String           | 告警类型                                                 |
|                      | `severity`                           | String           | 严重程度（`info`, `warning`, `critical`）                |
|                      | `message`                            | String           | 告警信息                                                 |
|                      | `resolved`                           | Boolean          | 是否已解决                                               |

---

### API 接口说明

以下是项目中主要 API 的详细说明：

| 模块                  | 路由                                     | 方法   | 描述                                   | 请求参数                                   | 返回值示例                                      |
|-----------------------|------------------------------------------|--------|----------------------------------------|-------------------------------------------|-----------------------------------------------|
| 用户模块              | `/api/user/register`                    | POST   | 用户注册                               | `{ "username": "test", "email": "...", ...}` | `{ "success": true, "user_id": 1 }`           |
|                       | `/api/user/login`                       | POST   | 用户登录                               | `{ "email": "...", "password": "..." }`    | `{ "success": true, "token": "..." }`         |
| 序列号管理模块        | `/api/serial/generate`                  | POST   | 管理员生成序列号                       | `{ "duration_days": 30 }`                  | `{ "success": true, "serial_numbers": ["..."] }` |
| 服务器管理模块        | `/api/server/add`                       | POST   | 添加服务器                             | `{ "ip": "...", "region": "..." }`         | `{ "success": true, "server_id": 1 }`         |
| 容器管理模块          | `/api/container/allocate`               | POST   | 分配容器                               | `{ "user_id": 1, "server_id": 1, ... }`    | `{ "success": true, "container_id": 1 }`      |
| ACL 管理模块          | `/api/acl/generate`                     | POST   | 生成 ACL 配置                          | `{ "user_id": 1, "server_ids": [1, 2] }`   | `{ "success": true, "acl": { ... } }`         |
| 高可用模块            | `/api/ha/failover`                      | POST   | 故障切换                               | 无                                         | `{ "success": true, "message": "..." }`       |
| 日志管理模块          | `/api/logs/system`                      | GET    | 查询系统日志                           | 无                                         | `{ "success": true, "logs": [ ... ] }`        |
| 财务模块              | `/api/finance/statistics`               | GET    | 获取财务统计数据                       | 无                                         | `{ "success": true, "total_revenue": 1000 }`  |
| 监控模块              | `/api/monitoring/load_analysis`         | GET    | 分析服务器负载                         | 无                                         | `{ "success": true, "load_analysis": [...] }` |
| 通知模块              | `/api/notifications/send`               | POST   | 发送通知                               | `{ "user_id": 1, "subject": "...", ... }`  | `{ "success": true, "message": "Sent" }`      |

---

### 使用规范

1. **数据库初始化**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

2. **运行服务**:
   ```bash
   flask run
   ```

3. **API 调用**:
   使用工具（如 Postman 或 curl）调用各 API 端点，确保功能正确。

---

### 后续建议
1. **单元测试**:
   - 为主要模块和 API 增加测试，确保逻辑的正确性。
2. **性能优化**:
   - 优化服务器负载和数据库查询。
3. **文档完善**:
   - 自动生成 Swagger 文档以便于使用。

如果需要，我可以协助实现单元测试或文档生成！
