import {
  mdiViewDashboard,
  mdiAccountGroup,
  mdiDocker,
  mdiChartLine,
  mdiBell,
  mdiCog,
  mdiKey,
  mdiClipboardList,
  mdiShieldAccount
} from '@mdi/js'

export default [
  {
    to: '/',
    icon: mdiViewDashboard,
    label: '仪表盘'
  },
  {
    icon: mdiDocker,
    label: '容器管理',
    menu: [
      {
        to: '/containers',
        label: '容器列表'
      },
      {
        to: '/containers/add',
        label: '新建容器'
      }
    ]
  },
  {
    to: '/traffic',
    icon: mdiChartLine,
    label: '流量监控'
  },
  {
    icon: mdiAccountGroup,
    label: '用户管理',
    menu: [
      {
        to: '/users',
        label: '用户列表'
      },
      {
        to: '/users/add',
        label: '添加用户'
      }
    ]
  },
  {
    icon: mdiShieldAccount,
    label: 'ACL管理',
    menu: [
      {
        to: '/acl',
        label: 'ACL列表'
      },
      {
        to: '/acl/generate',
        label: '生成ACL'
      }
    ]
  },
  {
    icon: mdiKey,
    label: '序列号管理',
    to: '/serial'
  },
  {
    icon: mdiClipboardList,
    label: '租赁管理',
    to: '/rental'
  },
  {
    to: '/alerts',
    icon: mdiBell,
    label: '告警管理'
  },
  {
    icon: mdiCog,
    label: '系统管理',
    menu: [
      {
        to: '/system/logs',
        label: '系统日志'
      },
      {
        to: '/system/ha',
        label: '高可用配置'
      }
    ]
  }
]
