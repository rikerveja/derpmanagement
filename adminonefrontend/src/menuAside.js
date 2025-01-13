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
  mdiHeartPulse,
  mdiPlus,
  mdiKeyVariant,
  mdiChartBar,
  mdiClipboardTextClock,
  mdiHistory,
  mdiCalendarClock,
  mdiAlertCircleOutline,
  mdiCogOutline,
  mdiTextBoxOutline,
  mdiServerSecurity,
  mdiAccountCircle,
  mdiReceipt
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
        label: 'ACL列表',
        icon: mdiShieldAccount
      },
      {
        to: '/acl/generate',
        label: '生成ACL',
        icon: mdiPlus
      },
      {
        to: '/acl/logs',
        label: 'ACL日志',
        icon: mdiClipboardList
      }
    ]
  },
  {
    icon: mdiKey,
    label: '序列号管理',
    menu: [
      {
        to: '/serials/manage',
        label: '序列号管理',
        icon: mdiKeyVariant
      },
      {
        to: '/serials/stats',
        label: '序列号统计',
        icon: mdiChartBar
      }
    ]
  },
  {
    icon: mdiReceipt,
    label: '租赁管理',
    menu: [
      {
        to: '/rental',
        label: '租赁列表',
        icon: mdiClipboardTextClock
      },
      {
        to: '/rental/expiry',
        label: '到期检查',
        icon: mdiCalendarClock
      },
      {
        to: '/rental/history',
        label: '租赁历史',
        icon: mdiHistory
      }
    ]
  },
  {
    icon: mdiBell,
    label: '告警管理',
    menu: [
      {
        to: '/alerts',
        label: '告警列表',
        icon: mdiAlertCircle
      },
      {
        to: '/alerts/settings',
        label: '告警设置',
        icon: mdiAlertCircleOutline
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
        label: '系统日志',
        icon: mdiTextBoxOutline
      },
      {
        to: '/system/ha',
        label: '高可用配置',
        icon: mdiServerSecurity
      },
      {
        to: '/system/settings',
        label: '系统设置',
        icon: mdiCogOutline
      }
    ]
  }
]
