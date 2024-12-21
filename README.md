以下是 **DERP 服务器租赁与管理系统** 的完整需求文档，包括所有模块、功能、数据结构和接口需求的细节：

---

## **DERP 服务器租赁与管理系统 需求文档**

### **1. 用户管理模块**

#### **1.1 用户管理功能**
- **用户注册与登录**：支持用户通过邮箱注册，进行邮箱验证后注册成功；用户可以登录查看租赁信息、序列号绑定和租赁到期时间；支持管理员角色区分。
- **续费管理**：用户租赁到期后，管理员可帮助用户续费，并指定续费结束日期，系统会更新用户的租赁到期时间并发送续费成功通知邮件。
- **用户到期处理**：到期后自动释放服务器资源，并保留已注销用户的使用记录，提供历史记录查询。

#### **1.2 数据需求**
- **用户表**：包含用户名、邮箱、密码、角色、租赁到期时间等。
- **租赁表**：记录每个用户的租赁状态（已过期、有效等）。

#### **1.3 接口需求**
- **用户注册与登录接口**
- **续费管理接口**：管理员可以帮助用户续费。
- **续费通知接口**：在用户到期前7天、3天、1天发送提醒。

---

### **2. 序列号管理模块**

#### **2.1 序列号管理功能**
- **序列号生成与管理**：管理员生成序列号，设置有效期（天数）和状态（未使用、已使用、过期）。用户激活序列号后，绑定到租赁服务。
- **序列号过期管理**：明确记录每个序列号的过期时间，当到期后自动更新状态为 `expired`。
- **序列号与用户租赁时间关联**：用户绑定序列号时，系统根据序列号的有效期调整用户的租赁到期时间。续费时，续费的有效期将累加到当前租赁时间，而不是覆盖原有的到期时间。

#### **2.2 数据需求**
- **序列号表**：包括序列号代码、有效天数、状态、绑定的用户 ID、创建时间、使用时间、过期时间等字段。

#### **2.3 接口需求**
- **序列号生成接口**
- **序列号激活接口**：用户激活序列号。
- **序列号状态查询接口**：查询某个序列号的使用状态。

---

### **3. 服务器管理模块**

#### **3.1 服务器管理功能**
- **服务器信息管理**：管理员查看服务器的基本信息，如 IP 地址、地区、负载、流量等，并支持新增、删除、更新服务器信息。
- **服务器资源管理**：管理员可以查看服务器的流量使用情况，支持服务器流量限制，超流量时自动关闭容器。
- **服务器健康监控**：管理员查看服务器健康状态，并接收负载、流量等的实时监控数据。

#### **3.2 数据需求**
- **服务器表**：包括 IP 地址、地区、负载、流量、状态、硬件配置等字段。

#### **3.3 接口需求**
- **服务器信息管理接口**
- **服务器健康监控接口**
- **流量管理接口**：查看服务器流量、限制流量等。

---

### **4. 容器管理模块**

#### **4.1 容器管理功能**
- **容器分配与管理**：每个用户分配独立的 Docker 容器，容器需绑定到用户和服务器，支持动态端口分配。
- **容器流量统计**：按容器记录用户流量，包括上传流量和下载流量，且可设置流量上限。

#### **4.2 数据需求**
- **用户容器表**：包括容器 ID、用户 ID、服务器 ID、端口、流量统计等字段。

#### **4.3 接口需求**
- **容器分配接口**
- **容器流量统计接口**

---

### **5. ACL 管理模块**

#### **5.1 ACL 配置管理**
- **ACL 配置生成与管理**：管理员为每个用户生成 ACL 配置，配置用户访问服务器的权限。支持手动和自动更新 ACL 配置。

#### **5.2 数据需求**
- **ACL 配置表**：包括用户 ID、绑定服务器、权限、版本号等字段。

#### **5.3 接口需求**
- **ACL 配置生成接口**
- **ACL 校验接口**：在用户请求时校验 ACL 权限。

---

### **6. 监控与告警模块**

#### **6.1 监控功能**
- **服务器监控**：系统实时监控服务器的 CPU 使用率、内存、流量、负载等。
- **告警机制**：当监控指标超过预设阈值时，自动触发告警并发送通知。

#### **6.2 数据需求**
- **监控日志表**：记录每个服务器的监控指标和对应的值。
- **告警表**：包括告警类型、严重性、告警信息、是否解决等字段。

#### **6.3 接口需求**
- **监控日志接口**
- **告警发送接口**：触发并发送告警。

---

### **7. 财务管理模块**

#### **7.1 套餐管理功能**
- **套餐管理**：管理员设置不同租赁套餐（如 3 天、5 天、30 天等），并生成对应的序列号。
- **财务统计**：系统自动统计收益、套餐销售数量、用户支付等信息。

#### **7.2 数据需求**
- **财务表**：记录收入、套餐销售数量、用户支付情况等信息。

#### **7.3 接口需求**
- **财务统计接口**
- **财务报表接口**

---

### **8. 高可用模块**

#### **8.1 故障切换功能**
- **故障切换**：系统支持故障自动切换，确保服务不中断。

#### **8.2 接口需求**
- **故障切换接口**：用于处理系统出现故障时的切换操作。

---

### **9. 流量管理模块**

#### **9.1 流量监控功能**
- **流量监控**：实时监控每个服务器和容器的流量使用情况。
- **流量限制**：支持根据套餐和用户配置限制每个容器的最大流量。

#### **9.2 数据需求**
- **流量表**：记录每个用户容器的上传和下载流量。

#### **9.3 接口需求**
- **实时流量接口**
- **流量统计接口**
- **超流量检测接口**

---

### **10. 安全与设备绑定模块**

#### **10.1 设备绑定管理**
- **设备绑定与解绑**：用户通过 **序列号激活后，绑定的服务器资源** 与用户的 **序列号、容器以及 ACL 配置挂钩**，而不是设备本身的绑定。
- **设备验证**：通过 **序列号与服务器资源的绑定** 进行验证。

#### **10.2 数据需求**
- **设备绑定表**：数据结构侧重于记录 **用户与服务器资源、序列号的绑定关系**，每个序列号的激活与服务器资源、容器的管理挂钩。

#### **10.3 接口需求**
- **序列号核销接口**：用户在购买序列号后进行激活，并与 **服务器资源**（包括容器和 ACL 配置）关联。
- **续费管理接口**：用户通过购买新序列号或续费序列号来延长 **服务器资源的使用时间**。
- **自动资源释放接口**：当用户未续费时，自动注销对应的 Docker 容器和服务器资源。

---

### **11. 分销管理模块**

#### **11.1 分销员分销模式**
- **分销员的两种分销模式**：
  1. **第一种模式**：用户通过分销员的独特链接注册并购买序列号，分销员通过该模式获得佣金。
  2. **第二种模式**：分销员直接购买序列号并卖给客户，赚取差价。

#### **11.2 分销员佣金核算**
- **佣金核算**：通过 **第一种模式** 的分销序列号销售额来核算分销员的佣金收入。
- 通过 **月度计划** 进行统计，按月核算分销员的 **佣金总额**。
- 分销员也可以根据自己的购买序列号的数量和销售价格获得相应的分销利润。

---

### **12. 服务器监控与负载管理**

#### **12.1 Docker 容器健康状态表 (`docker_health_status`)**
- 用于记录每个 **Docker 容器** 的健康状况，包括 **DERP 服务的健康状态** 和 **其他监控指标**（如容器负载等）。



#### **12.2 服务器负载监控表 (`server_load_status`)**
- 用于记录每台服务器的负载情况，包括当前运行的 Docker 容器数量、CPU 使用率、内存使用情况等。

---

### **13. SSH 链接服务器开 Docker 容器并部署 DERP 服务**

#### **13.1 SSH 链接与 Docker 容器部署**
- 系统通过 **SSH 连接服务器**，自动 **创建 Docker 容器** 并在其中部署 **DERP 服务**。
- 用户通过生成的 **ACL 配置** 来访问部署在容器中的 DERP 服务。

#### **13.2 目标与要求**
- 容器配置与 **DERP 服务** 自动化部署。
- 用户可以 **测试容器中的 DERP 服务**，并生成 **ACL 文本**。

---

### **14. 服务器类别管理模块**

#### **14.1 服务器类别**
- **ECS 服务器（按年租赁）**：按 **1 年租赁**，用户购买后使用指定期限。
- **ECS 服务器（按时按量后结算）**：按 **时计费**，价格为 **0.108 元/小时**，按实际使用时间计费。

#### **14.2 数据需求**
- **服务器类型表**：记录 **ECS 服务器** 的不同计费方式及资源配置。

---

### **总结**
- **需求完善**：涵盖了用户管理、序列号管理、服务器管理、容器管理、ACL 配置、监控与告警、财务管理、高可用等模块，已全面覆盖系统的核心功能。
- **序列号与用户时间管理**：确保了用户的租赁到期时间与 **序列号绑定** 和 **续费管理** 的关系紧密结合。
- **模块功能**：每个模块的功能需求、数据需求和接口需求都已明确，接下来可以进行逐步的代码开发和测试。

---

根据您提供的需求，以下是 **DERP 服务器租赁与管理系统** 的 **API 接口及说明** 和 **数据库结构表及说明**。

---

## **1. 用户管理模块**

### **1.1 用户管理功能**

#### **API 接口**
- **用户注册**
  - **URL**: `/api/user/register`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string",
      "verification_code": "string"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "message": "User registered successfully"
    }
    ```

- **用户登录**
  - **URL**: `/api/user/login`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "message": "Login successful",
      "token": "string"
    }
    ```

- **续费管理**
  - **URL**: `/api/user/renew`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "user_id": "int",
      "serial_code": "string"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "message": "Subscription renewed successfully",
      "new_expiry_time": "datetime"
    }
    ```

#### **数据库表结构**
- **用户表 (`users`)**
  ```sql
  CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username VARCHAR(80) UNIQUE NOT NULL,
      email VARCHAR(120) UNIQUE NOT NULL,
      password VARCHAR(200) NOT NULL,
      role VARCHAR(20) DEFAULT 'user',
      rental_expiry DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  ```

---

## **2. 序列号管理模块**

### **2.1 序列号管理功能**

#### **API 接口**
- **序列号生成**
  - **URL**: `/api/serial/generate`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "count": "int",
      "duration_days": "int"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "serial_numbers": ["string"]
    }
    ```

- **序列号激活**
  - **URL**: `/api/serial/activate`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "user_id": "int",
      "serial_code": "string"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "message": "Serial number activated successfully"
    }
    ```

#### **数据库表结构**
- **序列号表 (`serial_numbers`)**
  ```sql
  CREATE TABLE serial_numbers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code VARCHAR(255) UNIQUE NOT NULL,
      duration_days INTEGER NOT NULL,
      status VARCHAR(50) DEFAULT 'unused',
      user_id INTEGER,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      used_at DATETIME,
      expires_at DATETIME,
      FOREIGN KEY (user_id) REFERENCES users(id)
  );
  ```

---

## **3. 服务器管理模块**

### **3.1 服务器管理功能**

#### **API 接口**
- **添加服务器**
  - **URL**: `/api/server/add`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "ip": "string",
      "region": "string",
      "load": "float"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "server_id": "int",
      "message": "Server added successfully"
    }
    ```

- **查看服务器状态**
  - **URL**: `/api/server/status/{server_id}`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "server_status": "healthy"
    }
    ```

#### **数据库表结构**
- **服务器表 (`servers`)**
  ```sql
  CREATE TABLE servers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ip VARCHAR(255) UNIQUE NOT NULL,
      region VARCHAR(100) NOT NULL,
      load FLOAT DEFAULT 0.0,
      status VARCHAR(50) DEFAULT 'healthy',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  ```

---

## **4. 容器管理模块**

### **4.1 容器管理功能**

#### **API 接口**
- **容器分配**
  - **URL**: `/api/container/allocate`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "user_id": "int",
      "server_id": "int",
      "port": "int"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "container_id": "int"
    }
    ```

- **容器流量查看**
  - **URL**: `/api/container/traffic/{container_id}`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "upload_traffic": "float",
      "download_traffic": "float"
    }
    ```

#### **数据库表结构**
- **用户容器表 (`user_containers`)**
  ```sql
  CREATE TABLE user_containers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      server_id INTEGER NOT NULL,
      port INTEGER NOT NULL,
      upload_traffic FLOAT DEFAULT 0.0,
      download_traffic FLOAT DEFAULT 0.0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      status VARCHAR(50) DEFAULT 'active',
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (server_id) REFERENCES servers(id)
  );
  ```

---

## **5. ACL 管理模块**

### **5.1 ACL 配置管理**

#### **API 接口**
- **生成 ACL 配置**
  - **URL**: `/api/acl/generate`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "user_id": "int",
      "server_ids": ["int"]
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "acl_code": "string"
    }
    ```

- **下载 ACL 配置**
  - **URL**: `/api/acl/download/{acl_code}`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "acl_file": "base64_encoded_string"
    }
    ```

#### **数据库表结构**
- **ACL 配置表 (`acl_config`)**
  ```sql
  CREATE TABLE acl_config (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      server_ids TEXT,  -- JSON 数组格式存储服务器 ID
      acl_code VARCHAR(255) UNIQUE NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
  );
  ```

---

## **6. 监控与告警模块**

### **6.1 监控功能**

#### **API 接口**
- **服务器健康监控**
  - **URL**: `/api/monitoring/health/{server_id}`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "cpu_usage": "float",
      "memory_usage": "float",
      "ping_latency": "float"
    }
    ```

#### **数据库表结构**
- **服务器健康状态表 (`server_health_status`)**
  ```sql
  CREATE TABLE server_health_status (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      server_id INTEGER NOT NULL,
      cpu_usage FLOAT DEFAULT 0.0,
      memory_usage FLOAT DEFAULT 0.0,
      ping_latency FLOAT DEFAULT 0.0,
      status VARCHAR(50) DEFAULT 'healthy',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (server_id) REFERENCES servers(id)
  );
  ```

---

## **7. 财务管理模块**

### **7.1 财务统计功能**

#### **API 接口**
- **查看财务统计**
  - **URL**: `/api/finance/statistics`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "total_revenue": "float",
      "total_users": "int"
    }
    ```

#### **数据库表结构**
- **财务表 (`finance_stats`)**
  ```sql
  CREATE TABLE finance_stats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      revenue FLOAT NOT NULL,
      users_served INTEGER NOT NULL,
      period_start DATETIME NOT NULL,
      period_end DATETIME NOT

 NULL
  );
  ```

---

## **8. 高可用模块**

### **8.1 故障切换功能**

#### **API 接口**
- **故障切换接口**
  - **URL**: `/api/ha/failover`
  - **方法**: `POST`
  - **请求参数**:
    ```json
    {
      "server_id": "int"
    }
    ```
  - **返回**:
    ```json
    {
      "success": true,
      "message": "Failover completed"
    }
    ```

---

### **9. 流量管理模块**

#### **API 接口**
- **实时流量监控**
  - **URL**: `/api/traffic/realtime`
  - **方法**: `GET`
  - **返回**:
    ```json
    {
      "success": true,
      "traffic_data": [
        {
          "container_id": "int",
          "upload_traffic": "float",
          "download_traffic": "float"
        }
      ]
    }
    ```

#### **数据库表结构**
- **流量使用记录表 (`traffic_usage`)**
  ```sql
  CREATE TABLE traffic_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      container_id INTEGER NOT NULL,
      upload_traffic FLOAT DEFAULT 0.0,
      download_traffic FLOAT DEFAULT 0.0,
      month DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (container_id) REFERENCES user_containers(id)
  );
  ```

---

### **总结**
该系统涵盖了 **用户管理、序列号管理、服务器管理、容器管理、ACL 配置、监控与告警、财务管理、高可用、流量管理等模块**。每个模块的功能需求、数据需求和接口需求都已明确，确保了系统的核心功能可以逐步开发和测试。

根据您的需求和描述，我们可以进一步完善和丰富数据库设计。以下是基于您提供的需求分析，详细的数据库结构设计。每个模块的表和字段都会考虑到系统的多种功能、数据管理、扩展性和性能优化。

### 1. 用户管理模块
#### **1.1 用户表**
存储用户的基本信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 用户 ID，主键，自增长                     |
| `username`         | VARCHAR(255)    | 用户名，唯一                              |
| `email`            | VARCHAR(255)    | 邮箱地址，唯一                            |
| `password`         | VARCHAR(255)    | 密码                                      |
| `role`             | ENUM('user', 'admin', 'distributor', 'super_admin') | 用户角色                                  |
| `rental_expiry`    | DATETIME       | 租赁到期时间                              |
| `created_at`       | DATETIME       | 用户注册时间                              |
| `updated_at`       | DATETIME       | 用户信息更新时间                          |

#### **1.2 租赁表**
记录每个用户的租赁状态，管理租赁时间和状态。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 租赁记录 ID，主键，自增长                 |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `status`           | ENUM('active', 'expired', 'paused') | 租赁状态（活动、过期、暂停）       |
| `start_date`       | DATETIME       | 租赁开始时间                              |
| `end_date`         | DATETIME       | 租赁结束时间                              |
| `created_at`       | DATETIME       | 租赁记录创建时间                          |
| `updated_at`       | DATETIME       | 租赁记录更新时间                          |

#### **1.3 续费通知表**
记录续费通知的发送历史。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 记录 ID，主键，自增长                     |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `notification_type`| ENUM('7_days', '3_days', '1_day') | 通知类型（提前 7 天、3 天、1 天）|
| `sent_at`          | DATETIME       | 通知发送时间                              |

### 2. 序列号管理模块
#### **2.1 序列号表**
记录每个序列号的状态和有效期，关联用户和租赁服务。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 序列号 ID，主键，自增长                   |
| `code`             | VARCHAR(255)    | 序列号代码，唯一                          |
| `status`           | ENUM('unused', 'used', 'expired') | 序列号状态（未使用、已使用、已过期）|
| `user_id`          | INT (FK)       | 使用该序列号的用户 ID                    |
| `valid_days`       | INT            | 序列号的有效期（天数）                    |
| `start_date`       | DATETIME       | 序列号激活时间                            |
| `end_date`         | DATETIME       | 序列号到期时间                            |
| `created_at`       | DATETIME       | 序列号生成时间                            |
| `used_at`          | DATETIME       | 序列号使用时间                            |
| `expires_at`       | DATETIME       | 序列号过期时间                            |

#### **2.2 序列号与用户租赁时间关联表**
记录序列号激活时，如何影响用户的租赁到期时间。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 关联 ID，主键，自增长                     |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `serial_number_id` | INT (FK)       | 序列号 ID，外键，指向序列号表             |
| `updated_rental_expiry` | DATETIME   | 更新后的租赁到期时间                      |
| `created_at`       | DATETIME       | 记录创建时间                              |

### 3. 服务器管理模块
#### **3.1 服务器表**
记录服务器的基本信息、硬件配置和当前状态。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 服务器 ID，主键，自增长                   |
| `ip`               | VARCHAR(255)    | 服务器 IP 地址                            |
| `region`           | VARCHAR(255)    | 服务器所在地区                            |
| `status`           | ENUM('active', 'inactive', 'maintenance') | 服务器状态（活动、停用、维护） |
| `cpu`              | VARCHAR(255)    | CPU 配置                                  |
| `memory`           | VARCHAR(255)    | 内存配置                                  |
| `storage`          | VARCHAR(255)    | 存储配置                                  |
| `bandwidth`        | VARCHAR(255)    | 带宽配置                                  |
| `created_at`       | DATETIME       | 服务器创建时间                            |
| `updated_at`       | DATETIME       | 服务器更新时间                            |

#### **3.2 服务器负载监控表**
记录每台服务器的负载情况。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 记录 ID，主键，自增长                     |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `cpu_usage`        | DECIMAL(5, 2)  | CPU 使用率                                |
| `memory_usage`     | DECIMAL(5, 2)  | 内存使用率                                |
| `disk_usage`       | DECIMAL(5, 2)  | 磁盘使用率                                |
| `network_usage`    | DECIMAL(5, 2)  | 网络带宽使用率                            |
| `timestamp`        | DATETIME       | 监控时间                                  |

### 4. 容器管理模块
#### **4.1 用户容器表**
记录每个用户的 Docker 容器信息，包括容器状态、端口、流量等。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 容器 ID，主键，自增长                     |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `container_id`     | VARCHAR(255)    | Docker 容器 ID                            |
| `port`             | INT            | 容器端口                                  |
| `status`           | ENUM('running', 'stopped', 'paused') | 容器状态（运行、停止、暂停）       |
| `created_at`       | DATETIME       | 容器创建时间                              |
| `updated_at`       | DATETIME       | 容器更新时间                              |
| `traffic_usage`    | DECIMAL(10,2)  | 流量使用情况（MB）                        |
| `max_traffic`      | DECIMAL(10,2)  | 最大流量限制（MB）                        |

#### **4.2 容器流量统计表**
记录每个容器的流量统计信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 记录 ID，主键，自增长                     |
| `container_id`     | INT (FK)       | 容器 ID，外键，指向用户容器表             |
| `upload_traffic`   | DECIMAL(10,2)  | 上行流量（MB）                            |
| `download_traffic` | DECIMAL(10,2)  | 下行流量（MB）                            |
| `timestamp`        | DATETIME       | 流量记录时间                              |
                    

### 5. ACL 管理模块
#### **5.1 ACL 配置表**
记录每个用户的 ACL 配置，包括其访问权限。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 配置 ID，主键，自增长                     |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表

                 |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `permissions`      | TEXT           | 权限配置（如可访问的服务、端口等）       |
| `version`          | VARCHAR(50)     | ACL 配置版本号                            |
| `created_at`       | DATETIME       | 配置生成时间                              |
| `updated_at`       | DATETIME       | 配置更新时间                              |

#### **5.2 ACL 校验记录表**
记录每次用户请求访问时的 ACL 校验信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 校验记录 ID，主键，自增长                 |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `acl_version`      | VARCHAR(50)     | 使用的 ACL 版本号                         |
| `status`           | ENUM('success', 'fail') | 校验状态（成功、失败）                  |
| `timestamp`        | DATETIME       | 校验时间                                  |



### 6. 监控与告警模块

#### **6.1 监控日志表**
此表记录服务器的监控数据，包括 **Ping 可用性** 和 **Ping 时延**，以及 **流量统计**。监控信息可以定时收集并保存到数据库中。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 记录 ID，主键，自增长                     |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `is_reachable`     | BOOLEAN        | 服务器是否可用（Ping 是否通）             |
| `ping_latency`     | DECIMAL(10, 2) | Ping 时延，单位：毫秒                     |
| `total_traffic`    | DECIMAL(10, 2) | 总流量（单位：MB）                        |
| `download_traffic` | DECIMAL(10, 2) | 下载流量（单位：MB）                      |
| `upload_traffic`   | DECIMAL(10, 2) | 上传流量（单位：MB）                      |
| `timestamp`        | DATETIME       | 记录时间                                  |


#### **6.2 告警表**
此表记录系统中生成的告警信息，包括告警类型、严重性、消息内容、解决状态等。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 告警 ID，主键，自增长                     |
| `alert_type`       | VARCHAR(255)    | 告警类型                                  |
| `severity`         | ENUM('low', 'medium', 'high') | 告警严重程度（低、中、高） |
| `message`          | TEXT           | 告警消息                                  |
| `resolved`         | BOOLEAN        | 是否已解决                                |
| `created_at`       | DATETIME       | 告警创建时间                              |
| `updated_at`       | DATETIME       | 告警更新时间                              |

---

### 7. 财务管理模块
#### **7.1 套餐管理表**
记录不同租赁套餐的信息，包括套餐名称、时长、价格等。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 套餐 ID，主键，自增长                     |
| `name`             | VARCHAR(255)    | 套餐名称                                  |
| `duration_days`    | INT            | 套餐有效期（天数）                        |
| `price`            | DECIMAL(10, 2)  | 套餐价格                                  |
| `created_at`       | DATETIME       | 套餐创建时间                              |
| `updated_at`       | DATETIME       | 套餐更新时间                              |

#### **7.2 财务记录表**
记录所有与财务相关的收入和支出，包括用户支付、佣金、套餐销售等信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 财务记录 ID，主键，自增长                 |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `transaction_type` | ENUM('payment', 'refund', 'commission') | 交易类型（支付、退款、佣金） |
| `amount`           | DECIMAL(10, 2) | 交易金额                                  |
| `package_id`       | INT (FK)       | 关联套餐 ID（如用户购买套餐时）           |
| `created_at`       | DATETIME       | 交易时间                                  |
| `status`           | ENUM('pending', 'completed', 'failed') | 交易状态（待处理、已完成、失败） |

#### **7.3 财务统计表**
记录每月的收入、销售数量等汇总信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 统计记录 ID，主键，自增长                 |
| `month`            | DATE           | 月份（例如：2024-01-01）                   |
| `total_income`     | DECIMAL(10, 2) | 总收入                                    |
| `total_sales`      | INT            | 套餐销售总数量                            |
| `total_commission` | DECIMAL(10, 2) | 总佣金                                    |
| `created_at`       | DATETIME       | 创建时间                                  |

---

### 8. 高可用模块
#### **8.1 故障切换记录表**
记录系统故障切换的日志和状态。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 故障切换记录 ID，主键，自增长             |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `failover_status`  | ENUM('initiated', 'completed', 'failed') | 切换状态（已启动、已完成、失败） |
| `timestamp`        | DATETIME       | 故障切换时间                              |
| `reason`           | TEXT           | 故障切换原因                              |

---

### 9. 流量管理模块
#### **9.1 流量记录表**
记录每个容器和服务器的流量使用情况。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 流量记录 ID，主键，自增长                 |
| `container_id`     | INT (FK)       | 容器 ID，外键，指向容器表                 |
| `upload_traffic`   | DECIMAL(10, 2) | 上行流量（MB）                            |
| `download_traffic` | DECIMAL(10, 2) | 下行流量（MB）                            |
| `timestamp`        | DATETIME       | 流量记录时间                              |

#### **9.2 流量限制表**
记录容器的流量限制。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 限制记录 ID，主键，自增长                 |
| `container_id`     | INT (FK)       | 容器 ID，外键，指向容器表                 |
| `max_upload`       | DECIMAL(10, 2) | 最大上传流量（MB）                        |
| `max_download`     | DECIMAL(10, 2) | 最大下载流量（MB）                        |
| `created_at`       | DATETIME       | 限制设置时间                              |

---

### 10. 安全与设备绑定模块
#### **10.1 设备绑定表**
记录设备与服务器资源、序列号的绑定信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 绑定 ID，主键，自增长                     |
| `user_id`          | INT (FK)       | 用户 ID，外键，指向用户表                 |
| `serial_number_id` | INT (FK)       | 序列号 ID，外键，指向序列号表             |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `container_id`     | INT (FK)       | 容器 ID，外键，指向容器表                 |
| `acl_id`           | INT (FK)       | ACL 配置 ID，外键，指向 ACL 配置表         |
| `created_at`       | DATETIME       | 绑定时间                                  |
| `updated_at`       | DATETIME       | 更新时间                                  |

---

### 11. 分销管理模块
#### **11.1 分销记录表**
记录分销员的销售记录，包括分销方式和佣金。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 分销记录 ID，主键，自增长                 |
| `distributor_id`   | INT (FK)       | 分销员 ID，外键，指向分销管理员表         |
| `sale_type`        | ENUM('link', 'direct') | 销售模式（通过链接，直接销售）       |
| `sale_amount`      | DECIMAL(10, 2) | 销售额                                    |
| `commission`       | DECIMAL(10, 2) | 分销佣金                                  |
| `created_at`       | DATETIME       | 销售时间                                  |

#### **11.2 分销员佣金表**
记录分销员的佣金收入。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 佣金记录 ID，主键，自增长                 |
| `distributor_id`   | INT (FK)       | 分销员 ID，外键，指向分销管理员表         |
| `commission_amount`| DECIMAL(10, 2) | 佣金金额                                  |
| `month`            | DATE           | 佣金计算的月份                            |
| `created_at`       | DATETIME       | 佣金生成时间                              |

---

### 12. 服务器监控与负载管理
#### **12.1 Docker 容器健康状态表**
记录每个容器的健康状况和负载信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 健康状态 ID，主键，自增长                 |
| `container_id`     | INT (FK)       | 容器 ID，外键，指向容器表                 |
| `health_status`    | ENUM('healthy', 'unhealthy') | 健康状态（健康、异常）           |
| `cpu_usage`        | DECIMAL(5, 2)  | 容器 CPU 使用率                           |
| `memory_usage`     | DECIMAL(5, 2)  | 容器内存使用率                           |
| `disk_usage`       | DECIMAL(5, 2)  | 容器磁盘使用率                           |
| `timestamp`        | DATETIME       | 健康状态记录时间                         |

#### **12.2 服务器负载监控表**
记录服务器的负载状态。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------

|-------------------------------------------|
| `id`               | INT (PK)       | 负载记录 ID，主键，自增长                 |
| `server_id`        | INT (FK)       | 服务器 ID，外键，指向服务器表             |
| `cpu_usage`        | DECIMAL(5, 2)  | CPU 使用率                                |
| `memory_usage`     | DECIMAL(5, 2)  | 内存使用率                                |
| `container_count`  | INT            | 当前运行的 Docker 容器数量                |
| `timestamp`        | DATETIME       | 记录时间                                  |

---

### 13. SSH 链接与 Docker 容器部署
此模块没有独立的数据表设计，因为它主要是一个操作流程和自动化部署的接口。不过，可以通过操作日志记录相关事件。

---

### 14. 服务器类别管理模块
#### **14.1 服务器类型表**
记录不同服务器的类型、计费方式、资源配置等信息。

| 字段               | 类型           | 描述                                      |
|--------------------|----------------|-------------------------------------------|
| `id`               | INT (PK)       | 服务器类型 ID，主键，自增长               |
| `name`             | VARCHAR(255)    | 服务器类型名称                            |
| `pricing_model`    | ENUM('hourly', 'annual') | 定价模型（按小时计费，按年计费） |
| `price_per_hour`   | DECIMAL(10, 2) | 每小时价格（仅限按小时计费）              |
| `price_per_year`   | DECIMAL(10, 2) | 每年价格（仅限按年计费）                  |
| `created_at`       | DATETIME       | 创建时间                                  |

---

