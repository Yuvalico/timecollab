import { defineStore } from 'pinia';

// Define a type for the user object
interface User {
  email: string;
  permission: number;
}

// Define a type for the token, typically a string
type Token = string;

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null, // User can be null initially
    token: localStorage.getItem('authToken') || '',
    userPermission: parseInt(localStorage.getItem('userPermission') || '2'), // Default to non-admin if not found
  }),
  actions: {
    setUser(user: User, token: Token) {  // Explicitly define types for user and token
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
  },
});
