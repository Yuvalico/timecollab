<script setup>
import { ref, computed } from 'vue';
import { useTheme } from 'vuetify';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { endpoints } from '@/utils/backendEndpoints';

import AuthProvider from '@/views/pages/authentication/AuthProvider.vue';

import logo from '@images/logo.svg?raw';
import authV1MaskDark from '@images/pages/auth-v1-mask-dark.png';
import authV1MaskLight from '@images/pages/auth-v1-mask-light.png';
import authV1Tree2 from '@images/pages/auth-v1-tree-2.png';
import authV1Tree from '@images/pages/auth-v1-tree.png';

// Inject the Axios instance
const api = inject('api');

const authStore = useAuthStore();
const router = useRouter();

const form = ref({
  email: '',
  password: '',
  remember: false,
});

const vuetifyTheme = useTheme();

const authThemeMask = computed(() => {
  return vuetifyTheme.global.name.value === 'light'
    ? authV1MaskLight
    : authV1MaskDark;
});

const isPasswordVisible = ref(false);

// New function to handle login
const handleLogin = async () => {
  try {
    const response = await api.post(endpoints.auth.login, {
      email: form.value.email,
      password: form.value.password,
    }, {
      withCredentials: true
    });

    const { access_token, refresh_token, permission, company_id } = response.data;
    authStore.setUser({ email: form.value.email, 
                        permission: permission,
                        company_id: company_id
                      }, 
                      access_token,
                      refresh_token,
                    );

    //Get user data
    const user_details = await api.get(`${endpoints.users.getByEmail}/${form.value.email}`)
    const user_data = user_details.data

    // Get company data
    const company_details = await api.get(`${endpoints.companies.getCompanyDetails}/${user_data.company_id}`)
    const company_data = company_details.data

    // // Store the JWT token in localStorage
    // localStorage.setItem('authToken', access_token);
    // localStorage.setItem('refreshToken', refresh_token);
    // localStorage.setItem('userPermission', permission);
    authStore.setUser({ email: form.value.email, 
      // id: user_data.id,
      f_name: user_data.first_name, 
      l_name: user_data.last_name, 
      company_id: company_data.company_id,
      company_name: company_data.company_name,
      permission: permission 
    }, 
    access_token,
    refresh_token
  );
    
  console.log(/*authStore.user.id, */authStore.user.f_name, authStore.user.l_name)

    // Redirect to a protected route, e.g., dashboard
    router.push('/dashboard');
  } catch (error) {
    console.error('Login failed:', error);
    // Optionally, show an error message to the user
  }
};
</script>

<template>
  <!-- eslint-disable vue/no-v-html -->

  <div class="auth-wrapper d-flex align-center justify-center pa-4">
    <VCard
      class="auth-card pa-4 pt-7"
      max-width="448"
    >
      <VCardItem class="justify-center">
        <RouterLink
          to="/"
          class="d-flex align-center gap-3"
        >
          <!-- eslint-disable vue/no-v-html -->
          <div
            class="d-flex"
            v-html="logo"
          />
          <h2 class="font-weight-medium text-2xl text-uppercase">
            Materio
          </h2>
        </RouterLink>
      </VCardItem>

      <VCardText class="pt-2">
        <h4 class="text-h4 mb-1">
          Welcome to Materio! 👋🏻
        </h4>
        <p class="mb-0">
          Please sign-in to your account and start the adventure
        </p>
      </VCardText>

      <VCardText>
        <VForm @submit.prevent="handleLogin">
          <VRow>
            <!-- email -->
            <VCol cols="12">
              <VTextField
                v-model="form.email"
                label="Email"
                type="email"
                required
              />
            </VCol>

            <!-- password -->
            <VCol cols="12">
              <VTextField
                v-model="form.password"
                label="Password"
                placeholder="············"
                :type="isPasswordVisible ? 'text' : 'password'"
                :append-inner-icon="isPasswordVisible ? 'ri-eye-off-line' : 'ri-eye-line'"
                @click:append-inner="isPasswordVisible = !isPasswordVisible"
                required
              />

              <!-- remember me checkbox -->
              <div class="d-flex align-center justify-space-between flex-wrap my-6">
                <VCheckbox
                  v-model="form.remember"
                  label="Remember me"
                />

                <a
                  class="text-primary"
                  href="javascript:void(0)"
                >
                  Forgot Password?
                </a>
              </div>

              <!-- login button -->
              <VBtn
                block
                type="submit"
              >
                Login
              </VBtn>
            </VCol>

            <!-- create account -->
            <VCol
              cols="12"
              class="text-center text-base"
            >
              <span>New on our platform?</span>
              <RouterLink
                class="text-primary ms-2"
                to="/register"
              >
                Create an account
              </RouterLink>
            </VCol>

            <VCol
              cols="12"
              class="d-flex align-center"
            >
              <VDivider />
              <span class="mx-4">or</span>
              <VDivider />
            </VCol>

            <!-- auth providers -->
            <VCol
              cols="12"
              class="text-center"
            >
              <AuthProvider />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>

    <VImg
      class="auth-footer-start-tree d-none d-md-block"
      :src="authV1Tree"
      :width="250"
    />

    <VImg
      :src="authV1Tree2"
      class="auth-footer-end-tree d-none d-md-block"
      :width="350"
    />

    <!-- bg img -->
    <VImg
      class="auth-footer-mask d-none d-md-block"
      :src="authThemeMask"
    />
  </div>
</template>

<style lang="scss">
@use "@core/scss/template/pages/page-auth";
</style>
