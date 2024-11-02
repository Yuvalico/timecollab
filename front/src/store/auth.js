import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,  
    refreshToken: null,
    userPermission: 2, 
    remember: false,
  }),
  actions: {
    setUser(user, access_token, refresh_token, remember) {  
      this.user = user;
      this.accessToken = access_token;
      this.refreshToken = refresh_token;
      this.userPermission = user.permission;
      this.remember = remember;
    },
    logout() {
      // this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.userPermission = 2; 
      this.remember = false;
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
