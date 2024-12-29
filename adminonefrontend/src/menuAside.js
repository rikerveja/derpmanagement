import {
  mdiHome,
  mdiAccountGroup,
  mdiDocker,
  mdiChartLine,
  mdiBell,
  mdiServer,
  mdiKey,
  mdiShieldAccount,
  mdiCog
} from '@mdi/js'

export default [
  {
    to: '/dashboard',
    icon: mdiHome,
    label: '首页'
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
        to: '/users/distributor',
        label: '分销商管理'
      }
    ]
  }
  // ... 其他菜单项
]
