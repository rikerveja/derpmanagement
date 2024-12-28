### **完整的 API 文档**

#### **1. 用户相关 API**

##### **1.1 创建用户**
- **URL**: `/api/add_user`
- **Method**: `POST`
- **Description**: 创建一个新用户。
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "User created successfully",
      "user_id": 123
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid data"
    }
    ```
- **Database Interaction**: 向 `users` 表插入新用户。

##### **1.2 用户登录**
- **URL**: `/api/login`
- **Method**: `POST`
- **Description**: 用户登录，验证用户名和密码。
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Login successful",
      "token": "jwt_token_string"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Invalid username or password"
    }
    ```
- **Database Interaction**: 根据用户名查询数据库中的密码，并验证其正确性。如果正确，返回一个 JWT token。

##### **1.3 发送验证邮件**
- **URL**: `/api/send_verification_email`
- **Method**: `POST`
- **Description**: 向指定邮箱发送验证邮件。
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Verification email sent successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid email address"
    }
    ```

##### **1.4 获取用户租赁信息**
- **URL**: `/api/user/rental_info`
- **Method**: `GET`
- **Description**: 获取当前用户的租赁信息。
- **Response**:
  ```json
  {
    "user_id": 123,
    "rental_status": "active",
    "rental_expiry": "2024-12-30"
  }
  ```

##### **1.5 获取用户历史记录**
- **URL**: `/api/user/history/<int:user_id>`
- **Method**: `GET`
- **Description**: 获取指定用户的历史记录。
- **Response**:
  ```json
  {
    "user_id": 123,
    "history": [
      {
        "rental_id": 1,
        "status": "active",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
      }
    ]
  }
  ```

##### **1.6 申请成为分销商**
- **URL**: `/api/user/apply_distributor`
- **Method**: `POST`
- **Description**: 用户申请成为分销商。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "distributor_code": "ABC123"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Distributor application successful"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid distributor data"
    }
    ```

##### **1.7 下载 ACL**
- **URL**: `/api/user/download_acl`
- **Method**: `GET`
- **Description**: 下载用户的 ACL（访问控制列表）。
- **Response**:
  ```json
  {
    "acl_file": "url_to_acl_file"
  }
  ```

---
好的，我将为你单独列出这部分的 API 文档。你可以将其添加到汇总文件中。

---

### **1. 服务器相关 API**

#### **1.1 添加服务器**
- **URL**: `/api/add_server`
- **Method**: `POST`
- **Description**: 向系统中添加一个新服务器。
- **Request Body**:
  ```json
  {
    "server_name": "string",
    "ip_address": "string",
    "status": "string"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Server added successfully",
      "server_id": 123
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid server data"
    }
    ```

#### **1.2 获取服务器状态**
- **URL**: `/api/server/status/<int:server_id>`
- **Method**: `GET`
- **Description**: 获取指定服务器的当前状态。
- **Response**:
  ```json
  {
    "server_id": 123,
    "status": "online"
  }
  ```

#### **1.3 健康检查**
- **URL**: `/api/server/health_check`
- **Method**: `GET`
- **Description**: 检查服务器的健康状态。
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

---
好的，以下是你提供的 API 路由的详细文档。你可以将它们添加到你的汇总文件中。

---

### **2. 日志相关 API**

#### **2.1 获取系统日志**
- **URL**: `/api/logs/system`
- **Method**: `GET`
- **Description**: 获取系统日志。
- **Response**:
  ```json
  {
    "logs": [
      {
        "log_id": 1,
        "message": "System started",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    ]
  }
  ```

#### **2.2 获取用户日志（按时间）**
- **URL**: `/api/logs/user_by_time`
- **Method**: `GET`
- **Description**: 根据时间获取用户日志。
- **Response**:
  ```json
  {
    "user_id": 123,
    "logs": [
      {
        "log_id": 1,
        "message": "User logged in",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ]
  }
  ```

#### **2.3 更新日志**
- **URL**: `/api/logs/update/<int:id>`
- **Method**: `PUT`
- **Description**: 更新指定日志的信息。
- **Request Body**:
  ```json
  {
    "message": "Updated log message"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Log updated successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid log data"
    }
    ```

#### **2.4 删除日志**
- **URL**: `/api/logs/delete/<int:id>`
- **Method**: `DELETE`
- **Description**: 删除指定日志。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Log deleted successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid log ID"
    }
    ```

### **2. 容器相关 API**

#### **2.1 获取容器列表**
- **URL**: `/api/containers`
- **Method**: `GET`
- **Description**: 获取所有容器的列表。
- **Response**:
  ```json
  {
    "containers": [
      {
        "container_name": "container1",
        "status": "running"
      },
      {
        "container_name": "container2",
        "status": "stopped"
      }
    ]
  }
  ```

#### **2.2 创建容器**
- **URL**: `/api/containers`
- **Method**: `POST`
- **Description**: 创建一个新容器。
- **Request Body**:
  ```json
  {
    "container_name": "string",
    "image": "string"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Container created successfully",
      "container_id": 123
    }
    ```

#### **2.3 获取容器状态**
- **URL**: `/api/containers/<container_name>/status`
- **Method**: `GET`
- **Description**: 获取指定容器的状态。
- **Response**:
  ```json
  {
    "container_name": "container1",
    "status": "running"
  }
  ```

#### **2.4 停止容器**
- **URL**: `/api/containers/<container_name>/stop`
- **Method**: `POST`
- **Description**: 停止指定容器。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Container stopped successfully"
    }
    ```

#### **2.5 更新容器**
- **URL**: `/api/containers/<container_name>`
- **Method**: `PUT`
- **Description**: 更新指定容器的信息。
- **Request Body**:
  ```json
  {
    "container_name": "new_name",
    "image": "new_image"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Container updated successfully"
    }
    ```

---

### **3. 访问控制列表 (ACL) 相关 API**

#### **3.1 生成 ACL**
- **URL**: `/api/acl/generate`
- **Method**: `POST`
- **Description**: 生成一个新的 ACL。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "permissions": ["read", "write"]
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "ACL generated successfully"
    }
    ```

#### **3.2 更新 ACL**
- **URL**: `/api/acl/update`
- **Method**: `POST`
- **Description**: 更新 ACL。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "permissions": ["read", "write", "execute"]
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "ACL updated successfully"
    }
    ```

#### **3.3 获取 ACL 日志**
- **URL**: `/api/acl/logs/<int:user_id>`
- **Method**: `GET`
- **Description**: 获取指定用户的 ACL 日志。
- **Response**:
  ```json
  {
    "user_id": 123,
    "logs": [
      {
        "action": "created",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ]
  }
  ```

#### **3.4 下载 ACL**
- **URL**: `/api/acl/download/<username>`
- **Method**: `GET`
- **Description**: 下载指定用户的 ACL 文件。
- **Response**:
  ```json
  {
    "acl_file": "url_to_acl_file"
  }
  ```

---

### **3. 流量相关 API**

#### **3.1 获取实时流量**
- **URL**: `/api/traffic/realtime`
- **Method**: `GET`
- **Description**: 获取所有容器的实时流量数据。
- **Response**:
  ```json
  {
    "traffic": {
      "in": 2048,
      "out": 4096
    }
  }
  ```

#### **3.2 获取指定容器的实时流量**
- **URL**: `/api/traffic/realtime/<int:container_id>`
- **Method**: `GET`
- **Description**: 获取指定容器的实时流量数据。
- **Response**:
  ```json
  {
    "container_id": 123,
    "traffic": {
      "in": 1024,
      "out": 2048
    }
  }
  ```

#### **3.3 获取用户流量历史**
- **URL**: `/api/traffic/history/<int:user_id>`
- **Method**: `GET`
- **Description**: 获取指定用户的流量历史记录。
- **Response**:
  ```json
  {
    "user_id": 123,
    "traffic_history": [
      {
        "timestamp": "2024-01-01T00:00:00Z",
        "in": 1024,
        "out": 2048
      }
    ]
  }
  ```

#### **3.4 获取流量统计**
- **URL**: `/api/traffic/stats`
- **Method**: `POST`
- **Description**: 获取流量统计数据。
- **Request Body**:
  ```json
  {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "total_in": 1048576,
      "total_out": 2097152
    }
    ```

#### **3.5 检测超限用户**
- **URL**: `/api/traffic/overlimit`
- **Method**: `GET`
- **Description**: 检测超限流量的用户。
- **Response**:
  ```json
  {
    "overlimit_users": [
      {
        "user_id": 123,
        "traffic_in": 10240,
        "traffic_out": 20480
      }
    ]
  }
  ```

---

如果你有更多的 API 或其他需求，欢迎继续提问！
### **4. 租赁相关 API**

#### **4.1 检查租赁到期**
- **URL**: `/api/rental/check_expiry`
- **Method**: `GET`
- **Description**: 检查所有租赁的到期情况。
- **Response**:
  ```json
  {
   

 "expired_rentals": [
      {
        "rental_id": 1,
        "user_id": 123,
        "expiry_date": "2024-12-30"
      }
    ]
  }
  ```

#### **4.2 发送到期通知**
- **URL**: `/api/rental/send_expiry_notifications`
- **Method**: `POST`
- **Description**: 发送租赁到期通知。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "expiry_date": "2024-12-30"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Expiry notification sent"
    }
    ```

#### **4.3 续租**
- **URL**: `/api/rental/renew`
- **Method**: `POST`
- **Description**: 续租操作。
- **Request Body**:
  ```json
  {
    "rental_id": 1,
    "new_expiry_date": "2025-12-31"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Rental renewed successfully"
    }
    ```

#### **4.4 删除租赁**
- **URL**: `/api/rental/delete/<int:serial_id>`
- **Method**: `DELETE`
- **Description**: 删除指定租赁。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Rental deleted successfully"
    }
    ```
---

### **6. 租赁历史和用户历史相关 API**

#### **6.1 获取用户租赁历史**
- **URL**: `/api/rental/history/<int:user_id>`
- **Method**: `GET`
- **Description**: 获取指定用户的租赁历史记录。
- **Response**:
  ```json
  {
    "user_id": 123,
    "rental_history": [
      {
        "rental_id": 1,
        "status": "active",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
      }
    ]
  }
  ```

#### **6.2 更新用户历史记录**
- **URL**: `/api/rental/history/update/<int:id>`
- **Method**: `PUT`
- **Description**: 更新指定用户的租赁历史记录。
- **Request Body**:
  ```json
  {
    "status": "renewed",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "User rental history updated successfully"
    }
    ```

#### **6.3 删除用户历史记录**
- **URL**: `/api/rental/history/delete/<int:id>`
- **Method**: `DELETE`
- **Description**: 删除指定的用户租赁历史记录。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "User rental history deleted successfully"
    }
    ```

### **4. 告警相关 API**

#### **4.1 获取实时告警**
- **URL**: `/api/alerts/realtime`
- **Method**: `GET`
- **Description**: 获取所有实时告警数据。
- **Response**:
  ```json
  {
    "alerts": [
      {
        "alert_id": 1,
        "message": "High traffic detected",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    ]
  }
  ```

#### **4.2 添加告警**
- **URL**: `/api/alerts/add`
- **Method**: `POST`
- **Description**: 添加一个新的告警。
- **Request Body**:
  ```json
  {
    "alert_type": "traffic",
    "threshold": 10000,
    "message": "Traffic limit exceeded"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Alert added successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid alert data"
    }
    ```

#### **4.3 检查每月流量**
- **URL**: `/api/alerts/traffic`
- **Method**: `POST`
- **Description**: 检查每月的流量告警。
- **Request Body**:
  ```json
  {
    "month": "2024-01"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Monthly traffic alert checked successfully"
    }
    ```

#### **4.4 检查服务器健康状态**
- **URL**: `/api/alerts/server_health`
- **Method**: `POST`
- **Description**: 检查服务器健康状态是否触发告警。
- **Request Body**:
  ```json
  {
    "server_id": 123
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Server health status alert checked successfully"
    }
    ```

#### **4.5 检查 Docker 流量健康**
- **URL**: `/api/alerts/docker_traffic`
- **Method**: `POST`
- **Description**: 检查 Docker 容器流量是否触发告警。
- **Request Body**:
  ```json
  {
    "container_id": 123
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Docker container traffic health checked successfully"
    }
    ```

#### **4.6 检查 Docker 容器状态**
- **URL**: `/api/alerts/docker_container`
- **Method**: `POST`
- **Description**: 检查 Docker 容器状态是否触发告警。
- **Request Body**:
  ```json
  {
    "container_id": 123
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Docker container status alert checked successfully"
    }
    ```

#### **4.7 删除告警**
- **URL**: `/api/alerts/delete/<int:id>`
- **Method**: `DELETE`
- **Description**: 删除指定的告警。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Alert deleted successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid alert ID"
    }
    ```

#### **4.8 获取所有告警**
- **URL**: `/api/alerts`
- **Method**: `GET`
- **Description**: 获取所有告警的列表。
- **Response**:
  ```json
  {
    "alerts": [
      {
        "alert_id": 1,
        "message": "High traffic detected",
        "timestamp": "2024-01-01T00:00:00Z"
      },
      {
        "alert_id": 2,
        "message": "Server down",
        "timestamp": "2024-01-01T01:00:00Z"
      }
    ]
  }
  ```

---

### **5. 序列号相关 API**

#### **5.1 检查序列号**
- **URL**: `/api/serial/check/<serial_code>`
- **Method**: `GET`
- **Description**: 检查指定的序列号是否有效。
- **Response**:
  ```json
  {
    "serial_code": "ABC123",
    "status": "valid",
    "issued_to": "user@example.com"
  }
  ```

#### **5.2 生成序列号**
- **URL**: `/api/serial/generate`
- **Method**: `POST`
- **Description**: 生成一个新的序列号。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "type": "rental",
    "expiry_date": "2025-12-31"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Serial number generated successfully",
      "serial_code": "XYZ789"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid data"
    }
    ```

#### **5.3 更新序列号**
- **URL**: `/api/serial/update/<int:id>`
- **Method**: `PUT`
- **Description**: 更新指定序列号的信息。
- **Request Body**:
  ```json
  {
    "serial_code": "XYZ789",
    "expiry_date": "2026-12-31"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Serial number updated successfully"
    }
    ```

#### **5.4 删除序列号**
- **URL**: `/api/serial/delete/<int:id>`
- **Method**: `DELETE`
- **Description**: 删除指定的序列号。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Serial number deleted successfully"
    }
    ```
### **5. 高可用性 (HA) 相关 API**

#### **5.1 检查服务器健康状态**
- **URL**: `/api/ha/health`
- **Method**: `GET`
- **Description**: 获取所有服务器的健康状态。
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

#### **5.2 检查单个服务器健康**
- **URL**: `/api/ha/health/<server_id>`
- **Method**: `GET`
- **Description**: 获取指定服务器的健康状态。
- **Response**:
  ```json
  {
    "server_id": 123,
    "status": "healthy"
  }
  ```

#### **5.3 获取容器流量**
- **URL**: `/api/ha/container_traffic/<container_id>`
- **Method**: `GET`
- **Description**: 获取指定容器的实时流量。
- **Response**:
  ```json
  {
    "container_id": 123,
    "traffic": {
      "in": 1024,
      "out": 2048
    }
  }
  ```

#### **5.4 启动故障转移**
- **URL**: `/api/ha/failover`
- **Method**: `POST`
- **Description**: 启动故障转移操作。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Failover operation successful"
    }
    ```

#### **5.5 启动负载均衡**
- **URL**: `/api/ha/load_balance`
- **Method**: `POST`
- **Description**: 启动负载均衡操作。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Load balance operation successful"
    }
    ```

#### **5.6 启动灾难恢复**
- **URL**: `/api/ha/disaster_recovery`
- **Method**: `POST`
- **Description**: 启动灾难恢复操作。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Disaster recovery operation successful"
    }
    ```

#### **5.7 替换 Docker 容器**
- **URL**: `/api/ha/replace_container`
- **Method**: `POST`
- **Description**: 替换指定的 Docker 容器。
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Docker container replaced successfully"
    }
    ```
---

### **7. 通知相关 API**

#### **7.1 发送提醒通知**
- **URL**: `/api/notifications/send_reminder`
- **Method**: `POST`
- **Description**: 发送租赁到期或其他事件的提醒通知。
- **Request Body**:
  ```json
  {
    "user_id": 123,
    "message": "Your rental is about to expire",
    "reminder_date": "2024-12-15"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Reminder notification sent successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid notification data"
    }
    ```

### **8. 监控相关 API**

#### **8.1 获取监控状态**
- **URL**: `/api/monitoring`
- **Method**: `GET`
- **Description**: 获取当前系统的监控状态。
- **Response**:
  ```json
  {
    "status": "healthy",
    "uptime": "72 hours",
    "issues": [
      {
        "type": "server_down",
        "timestamp": "2024-01-01T12:00:00Z",
        "message": "Server 123 is down"
      }
    ]
  }
  ```

---

### **9. 安全相关 API**

#### **9.1 获取用户的 ACL 信息**
- **URL**: `/api/security/user_acl_info/<int:user_id>`
- **Method**: `GET`
- **Description**: 获取指定用户的 ACL（访问控制列表）信息。
- **Response**:
  ```json
  {
    "user_id": 123,
    "acl_info": {
      "permissions": ["read", "write", "execute"],
      "role": "admin"
    }
  }
  ```
---

### **10. 获取 API 列表**

#### **10.1 获取所有 API 路由**
- **URL**: `/api/urls`
- **Method**: `GET`
- **Description**: 获取系统中所有 API 路由的列表，包括每个 API 的 `endpoint`、`methods` 和 `url`。
- **Response**:
  ```json
  [
    {
      "endpoint": "user.add_user",
      "methods": "OPTIONS, POST",
      "url": "/api/add_user"
    },
    {
      "endpoint": "user.login",
      "methods": "OPTIONS, POST",
      "url": "/api/login"
    },
    {
      "endpoint": "server.add_server",
      "methods": "OPTIONS, POST",
      "url": "/api/add_server"
    },
    {
      "endpoint": "traffic.realtime_traffic",
      "methods": "OPTIONS, GET, HEAD",
      "url": "/api/traffic/realtime"
    },
    // ... 其他 API 路由
  ]
  ```

---
