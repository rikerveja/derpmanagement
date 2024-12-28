## **完整的 API 文档**

### **1. 用户相关 API**

#### **1.1 创建用户**
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

---

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
- **URL**: `/api/ha/replace_container

`
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

### **6. 监控和告警相关 API**

#### **6.1 获取实时流量**
- **URL**: `/api/traffic/realtime`
- **Method**: `GET`
- **Description**: 获取实时流量数据。
- **Response**:
  ```json
  {
    "traffic": {
      "in": 2048,
      "out": 4096
    }
  }
  ```

#### **6.2 添加告警**
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

---
