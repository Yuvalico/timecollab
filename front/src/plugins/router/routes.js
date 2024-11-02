export const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    children: [
      {
        path: 'dashboard',
        component: () => import('@/pages/dashboard.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'management',
        component: () => import('@/pages/management/management.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'timewatch',
        component: () => import('@/pages/Timewatch.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'reports',
        component: () => import('@/pages/Reports.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'account-settings',
        component: () => import('@/pages/account-settings.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/blank.vue'),
    children: [
      {
        path: 'login',
        component: () => import('@/pages/login.vue'),
      },
      {
        path: '/:pathMatch(.*)*',
        component: () => import('@/pages/[...error].vue'),
      },
    ],
  },
]
