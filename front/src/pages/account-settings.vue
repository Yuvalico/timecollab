<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth'; 
import { endpoints } from '@/utils/backendEndpoints';

const api = inject('api');
const route = useRoute();
const authStore = useAuthStore(); 
const userInfo = ref({}); 
const companyName = ref([]); 
const newPassword = ref('');
const confirmPassword = ref('');

function formatTimeFromHours(totalHours) {
  const seconds = Math.round(totalHours * 3600);
  const hours = Math.round(seconds / 3600).toString().padStart(2, '0');
  const minutes = Math.round((seconds % 3600) / 60).toString().padStart(2, '0');
  // const seconds = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

function formatDate(dateString) {
  if (dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  }
  return '';
}

onMounted(async () => {
  try {
    await fetchSelf()
    userInfo.value.work_capacity = formatTimeFromHours(userInfo.value.work_capacity)
    userInfo.value.employment_start = formatDate(userInfo.value.employment_start )
  } catch (error) {
    console.error('Error fetching user info:', error);
    // Handle the error, e.g., show an error message
  }
});

async function fetchSelf() {
  try {
    const userResponse = await api.get(`${endpoints.users.getByEmail}/${authStore.user.email}`);
    // Access the first (and only) user object directly
    const user = userResponse.data; 
    userInfo.value = { ...user}
    fetchConpanyName();
    console.log('User fetched:', userInfo.value);
  } catch (error) {
    console.error('Error fetching user:', error);
  }
}
async function fetchConpanyName() {
  try {
    const response = await api.get(`${endpoints.companies.getCompanyNamebyID}/${authStore.user.company_id}/name`);
    // Access the first (and only) user object directly
    const company = response.data; 
    companyName.value = company.company_name;

    console.log('User fetched:', userInfo.value);
  } catch (error) {
    console.error('Error fetching user:', error);
  }
}

const passwordsMatch = (value) => {
  if (value !== newPassword.value) {
    return 'Passwords do not match';
  }
  return true;
};

const changePassword = async () => {
  try {
    const response = await api.post(endpoints.users.changePassword, {
      email: userInfo.value.email,
      new_password: newPassword.value, 
    });

    if (response.status === 200) {
      // Optionally, show a success message to the user
      alert('Password changed successfully!');
      newPassword.value = '';
      confirmPassword.value = '';
    } else {
      console.error('Failed to change password');
      // Handle the error, e.g., show an error message
    }
  } catch (error) {
    console.error('Error changing password:', error);
    // Handle the error, e.g., show an error message
  }
};

</script>

<template>
  <div v-if="userInfo != null">
    <VRow>
      <VCol cols="12">
        <VCard title="Account Details">
          <VDivider />
          <VCardText>
            <VRow>
              <VCol md="6" cols="12">
                <VTextField
                  v-model="userInfo.first_name" 
                  label="First Name"
                  readonly
                />
              </VCol>
              <VCol md="6" cols="12">
                <VTextField
                  v-model="userInfo.last_name" 
                  label="Last Name"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.email"
                  label="E-mail"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="companyName" 
                  label="Company"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.mobile_phone" 
                  label="Phone Number"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.role" 
                  label="Role"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.salary" 
                  label="Salary"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.work_capacity" 
                  label="Work Capacity"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.weekend_choice" 
                  label="Weekend Selection"
                  readonly
                />
              </VCol>
              <VCol cols="12" md="6">
                <VTextField
                  v-model="userInfo.employment_start" 
                  label="Employment Start"
                  readonly
                />
              </VCol>

              <VCol cols="12" md="6">
                <VTextField
                  v-model="newPassword" 
                  label="New Password"
                  type="password" 
                />
              </VCol>

              <VCol cols="12" md="6">
                <VTextField
                  v-model="confirmPassword" 
                  label="Confirm Password"
                  type="password" 
                  :rules="[passwordsMatch]" 
                />
              </VCol>

              <VCol
                cols="12"
                class="d-flex flex-wrap gap-4"
              >
                <VBtn @click="changePassword" type="submit">Change Password</VBtn> 
              </VCol>
            </VRow>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>

  