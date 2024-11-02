import { createApp, ref } from 'vue';
import App from '@/App.vue';
import { registerPlugins } from '@core/utils/plugins';
import axios from 'axios'; 
import { useAuthStore } from '@/store/auth'; 
import { endpoints } from '@/utils/backendEndpoints';
// import router from '@/plugins/router/index.js';


// Styles
import '@core/scss/template/index.scss';
import '@layouts/styles/index.scss';

// Create an Axios instance
const api = axios.create({
  baseURL: endpoints.api_base_url, 
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    const refreshToken = authStore.refreshToken;

    if (token) {
      if (config.url !== endpoints.auth.refresh) { 
        config.headers.Authorization = `Bearer ${token}`;
      }else{
        config.headers.Authorization = `Bearer ${refreshToken}`; 
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

function clearAuthStoreOnUnload() {
  const authStore = useAuthStore();
  if (!authStore.remember) { // Only clear if "Remember me" is not checked
    authStore.logout();
  }
}

window.addEventListener('beforeunload', clearAuthStoreOnUnload);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    // Check for 401 and the specific error message
    const authStore = useAuthStore();
    if (
      error.response.status === 401 && 
      error.response.data.msg === "Token has expired" &&
      !originalRequest._retry && error.config.url != endpoints.auth.refresh
    ) {
      originalRequest._retry = true;
      const refreshToken = authStore.refreshToken;
      try {
        // Include the refresh token in the Authorization header
        const refreshResponse = await api.post(endpoints.auth.refresh);

        const newAccessToken = refreshResponse.data.access_token;
        const newRefreshToken = refreshResponse.data.refresh_token;

        authStore.$patch({ 
          accessToken: newAccessToken,
          refreshToken: newRefreshToken 
        });
        // originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
          console.error("Failed to refresh token:", refreshError);
          authStore.logout(); 
          return Promise.reject(refreshError);
        }
    }else if(error.response.status === 401 && 
      error.response.data.msg === "Fresh token required"){
        const authStore = useAuthStore();
        authStore.logout();
    }
    return Promise.reject(error); 
  }
);

// Create vue app
const app = createApp(App);

// Register plugins
registerPlugins(app);

// Provide the Axios instance to your app
app.provide('api', api); // Make it available globally

// Mount vue app
app.mount('#app');