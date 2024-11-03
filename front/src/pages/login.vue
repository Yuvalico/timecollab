<script setup>
import { ref, computed } from 'vue';
import { useTheme } from 'vuetify';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { endpoints } from '@/utils/backendEndpoints';

import logo from '@images/logo.svg?raw';

// Inject the Axios instance
const api = inject('api');

const authStore = useAuthStore();
const router = useRouter();

const loginError = ref(null);
const form = ref({
  email: '',
  password: '',
  remember: false,
});

const vuetifyTheme = useTheme();

const isPasswordVisible = ref(false);

// New function to handle login
const handleLogin = async () => {
  try {
    const response = await api.post(endpoints.auth.login, {
      email: form.value.email,
      password: form.value.password,
      remember: form.value.remember,
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
                      form.value.remember,
                    );

    //Get user data
    const user_details = await api.get(`${endpoints.users.getByEmail}/${form.value.email}`)
    const user_data = user_details.data

    // Get company data
    const company_details = await api.get(`${endpoints.companies.getCompanyDetails}/${user_data.company_id}`)
    const company_data = company_details.data

    authStore.setUser({ email: form.value.email, 
      // id: user_data.id,
        f_name: user_data.first_name, 
        l_name: user_data.last_name, 
        company_id: company_data.company_id,
        company_name: company_data.company_name,
        permission: permission 
      }, 
      access_token,
      refresh_token,
      form.value.remember,
    );
    
    console.log(/*authStore.user.id, */authStore.user.f_name, authStore.user.l_name)

    // Redirect to a protected route, e.g., dashboard
    router.push('/timewatch');
  } catch (error) {
    console.error('Login failed:', error);

    // Check if the error response contains an error message
    if (error.response && error.response.data && error.response.data.error) {
      loginError.value = `Login failed. ${error.response.data.error}`;
    } else {
      // Set a generic error message if no specific message is found
      loginError.value = 'Login failed. Please check your credentials.'; 
    }
    form.value.email = '';
    form.value.password = '';
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
            TimeTracker
          </h2>
        </RouterLink>
      </VCardItem>

      <VCardText class="pt-2">
        <h4 class="text-h4 mb-1">
          Welcome! 👋🏻
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

              </div>

              <!-- login button -->
              <VBtn
                block
                type="submit"
              >
                Login
              </VBtn>

              <div v-if="loginError" class="text-error-login">
                {{ loginError }}
              </div>
            </VCol>

          </VRow>
        </VForm>
      </VCardText>
    </VCard>

  </div>
</template>

<style lang="scss">
@use "@core/scss/template/pages/page-auth";

.text-error-login {
  color: red; /* Or any color you prefer for error messages */
  text-align: center;
  margin-top: 10px; /* Add some spacing above the message */
}
</style>
