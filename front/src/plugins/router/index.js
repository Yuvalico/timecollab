import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { useAuthStore } from '@/store/auth';



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard to protect routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const token = authStore.accessToken;  // Check if the token is stored in localStorage

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      // If there's no token and the route requires authentication, redirect to login
      next({ path: '/login' });
    } else {
      // If the token exists, allow access
      next();
    }
  } else {
    // If the route doesn't require authentication, allow access
    next();
  }
});

export default function (app) {
  app.use(router)
}
export { router }
