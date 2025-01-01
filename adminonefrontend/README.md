# DERP Management System

基于 [Admin One Vue.js 3.x Tailwind 3.x](https://justboil.me/tailwind-admin-templates/free-vue-dashboard/) 模板开发的 DERP 管理系统。

[![Vue 3.x](https://img.shields.io/badge/vue-3.x-brightgreen.svg)](https://v3.vuejs.org/)
[![Tailwind 3.x](https://img.shields.io/badge/tailwind-3.x-blue.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 功能特性

- 📊 实时仪表盘
- 🔐 用户管理与权限控制
- 🐳 容器管理
- 📈 流量监控
- 🔔 告警管理
- ⚙️ 系统管理
- 🎫 序列号管理
- 📝 租赁管理
- 🌓 深色模式支持
- 📱 响应式设计

## 技术栈

- Vue 3.x + Composition API
- Vite
- Vue Router
- Tailwind CSS 3.x
- MDI Icons
- Axios
- Pinia 状态管理

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

### 生产环境构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

### 代码检查

```bash
npm run lint
```

## API 功能说明

### 用户相关
- 用户登录 `/login`
- 添加用户 `/add_user`
- 发送验证邮件 `/send_verification_email`
- 获取租赁信息 `/user/rental_info`
- 获取用户历史 `/user/history/:userId`
- 申请分销商 `/user/apply_distributor`
- 下载 ACL `/user/download_acl`
- 获取用户 ACL 信息 `/user/acl_info/:userId`

### 服务器相关
- 添加服务器 `/add_server`
- 获取服务器状态 `/server/status/:serverId`
- 检查服务器健康 `/server/health_check`
- 获取服务器健康检查 `/server/health_check/:serverId`

### 日志相关
- 获取系统日志 `/logs/system`
- 获取用户时间日志 `/logs/user_by_time`
- 更新日志 `/logs/update/:id`
- 删除日志 `/logs/delete/:id`

### 容器相关
- 获取容器列表 `/containers`
- 添加容器 `/containers/add`
- 获取容器状态 `/containers/status/:id`
- 获取容器流量 `/containers/traffic/:id`

### 序列号相关
- 获取序列号列表 `/serial/list`
- 检查序列号 `/serial/check/:serialCode`
- 生成序列号 `/serial/generate`
- 更新序列号 `/serial/update/:id`
- 删除序列号 `/serial/delete/:id`

### 高可用性相关
- 获取高可用健康状态 `/ha/health`
- 获取服务器健康状态 `/ha/health/:serverId`
- 获取容器流量 `/ha/container_traffic/:containerId`
- 启动故障转移 `/ha/failover`
- 启动负载均衡 `/ha/load_balance`
- 启动灾难恢复 `/ha/disaster_recovery`
- 替换容器 `/ha/replace_container`

### 通知相关
- 发送提醒通知 `/notifications/send_reminder`
- 获取通知列表 `/notifications`
- 标记通知已读 `/notifications/:notificationId/read`

### 监控相关
- 获取监控状态 `/monitoring`

### 租赁历史相关
- 获取租赁历史 `/rental/history/:userId`
- 更新租赁历史 `/rental/history/update/:id`
- 删除租赁历史 `/rental/history/delete/:id`

## 目录结构

```
src/
├── assets/          # 静态资源
├── components/      # 通用组件
├── layouts/         # 布局组件
├── router/          # 路由配置
├── services/        # API 服务
├── stores/          # 状态管理
└── views/           # 页面视图
    ├── acl/         # ACL管理
    ├── alerts/      # 告警管理
    ├── auth/        # 认证相关
    ├── containers/  # 容器管理
    ├── dashboard/   # 仪表盘
    ├── rental/      # 租赁管理
    ├── serial/      # 序列号管理
    ├── system/      # 系统管理
    ├── traffic/     # 流量监控
    └── users/       # 用户管理
```

## 响应式布局

### 移动端和平板

- 隐藏侧边菜单
- 可折叠的卡片和表格
- 优化的触摸操作体验

### 小型笔记本 (1024px)

- 可切换显示/隐藏侧边菜单
- 自适应的内容布局

### 笔记本和台式机

- 固定的左侧菜单布局
- 充分利用宽屏空间

## 环境变量

```
VITE_API_BASE_URL=http://localhost:8000
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 开发规范

- 使用 Vue 3 组合式 API
- 遵循 ESLint 配置
- 使用 Prettier 进行代码格式化
- 组件使用 PascalCase 命名
- 使用 Tailwind CSS 进行样式开发
- 使用 MDI 图标库

## License

[MIT](LICENSE)

## 致谢

- [JustBoil.me](https://justboil.me/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vue.js 3](https://v3.vuejs.org/)
- [Vite](https://vitejs.dev)
