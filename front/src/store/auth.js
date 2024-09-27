import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null, // User can be null initially
    token: localStorage.getItem('authToken') || '',
    userPermission: parseInt(localStorage.getItem('userPermission') || '2'), // Default to non-admin if not found
  }),
  actions: {
    setUser(user, token) {  // No explicit types in JavaScript
      this.user = user;
      this.token = token;
      this.userPermission = user.permission;
      localStorage.setItem('authToken', token);
      localStorage.setItem('userPermission', user.permission.toString());
    },
    logout() {
      this.user = null;
      this.token = '';
      this.userPermission = 2; // Reset to default non-admin
      localStorage.removeItem('authToken');
      localStorage.removeItem('userPermission');
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    isNetAdmin: (state) => state.userPermission === 0,
    isEmployer: (state) => state.userPermission === 1,
    isEmployee: (state) => state.userPermission === 2,
  },
});
