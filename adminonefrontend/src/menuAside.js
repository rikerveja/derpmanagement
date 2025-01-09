import {
  mdiViewDashboard,
  mdiAccountGroup,
  mdiDocker,
  mdiChartLine,
  mdiBell,
  mdiCog,
  mdiKey,
  mdiClipboardList,
  mdiShieldAccount,
  mdiServerNetwork,
  mdiMonitor,
  mdiAlertCircle,
  mdiServer,
  mdiHeartPulse
} from '@mdi/js'

export default [
  {
    to: '/dashboard',
    icon: mdiViewDashboard,
    label: '仪表盘'
  },
  {
    icon: mdiServerNetwork,
    label: '服务器管理',
    menu: [
      {
        to: '/servers/list',
        label: '服务器列表',
        icon: mdiServer
      },
      {
        to: '/servers/health',
        label: '健康检查',
        icon: mdiHeartPulse
      }
    ]
  },
  {
    icon: mdiDocker,
    label: '容器管理',
    menu: [
      {
        to: '/containers',
        label: '容器列表',
        icon: mdiDocker
      },
      {
        to: '/containers/add',
        label: '新建容器',
        icon: mdiServer
      }
    ]
  },
  {
    icon: mdiChartLine,
    label: '流量监控',
    menu: [
      {
        to: '/traffic/realtime',
        label: '实时流量',
        icon: mdiChartLine
      },
      {
        to: '/traffic/history',
        label: '历史流量',
        icon: mdiChartLine
      },
      {
        to: '/traffic/stats',
        label: '流量统计',
        icon: mdiChartLine
      }
    ]
  },
  {
    icon: mdiAccountGroup,
    label: '用户管理',
    menu: [
      {
        to: '/users',
        label: '用户列表',
        icon: mdiAccountGroup
      },
      {
        to: '/users/add',
        label: '添加用户',
        icon: mdiAccountGroup
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
      },
      {
        to: '/acl/logs',
        label: 'ACL日志'
      }
    ]
  },
  {
    icon: mdiKey,
    label: '序列号管理',
    menu: [
      {
        to: '/serials/manage',
        label: '序列号管理'
      },
      {
        to: '/serials/stats',
        label: '序列号统计'
      }
    ]
  },
  {
    icon: mdiClipboardList,
    label: '租赁管理',
    menu: [
      {
        to: '/rental',
        label: '租赁列表'
      },
      {
        to: '/rental/history',
        label: '租赁历史'
      },
      {
        to: '/rental/expiry',
        label: '到期检查'
      }
    ]
  },
  {
    icon: mdiBell,
    label: '告警管理',
    menu: [
      {
        to: '/alerts',
        label: '告警列表'
      },
      {
        to: '/alerts/settings',
        label: '告警设置'
      }
    ]
  },
  {
    icon: mdiMonitor,
    label: '监控管理',
    to: '/monitoring'
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
      },
      {
        to: '/system/settings',
        label: '系统设置'
      }
    ]
  }
]
