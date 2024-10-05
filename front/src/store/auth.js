import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,  // No need to initialize from localStorage
    refreshToken: null,
    userPermission: 2, // Default to non-admin
  }),
  actions: {
    setUser(user, access_token, refresh_token) {  // No explicit types in JavaScript
      this.user = user;
      this.accessToken = access_token;
      this.refreshToken = refresh_token;
      this.userPermission = user.permission;
    },
    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.userPermission = 2; // Reset to default non-admin
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken ,
    isNetAdmin: (state) => state.userPermission === 0,
    isEmployer: (state) => state.userPermission === 1,
    isEmployee: (state) => state.userPermission === 2,
  },
  persist: true,
});
