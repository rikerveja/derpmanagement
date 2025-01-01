import {
  mdiMenu,
  mdiAccount,
  mdiCogOutline,
  mdiEmail,
  mdiLogout,
  mdiThemeLightDark
} from '@mdi/js'

export default [
  {
    isCurrentUser: true,
    label: 'admin',
    menu: [
      {
        icon: mdiAccount,
        label: '我的账户',
        to: '/profile'
      },
      {
        icon: mdiCogOutline,
        label: '设置',
        to: '/settings'
      },
      {
        isDivider: true
      },
      {
        icon: mdiLogout,
        label: '退出',
        isLogout: true
      }
    ]
  },
  {
    icon: mdiThemeLightDark,
    label: '主题切换',
    isDesktopNoLabel: true,
    isToggleLightDark: true
  }
]
