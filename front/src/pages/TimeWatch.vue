
<script setup>
// Inject the Axios instance
import { endpoints } from '@/utils/backendEndpoints';
import { useAuthStore } from '@/store/auth';

const api = inject('api');
const authStore = useAuthStore();
const message = ref(''); 
const hasPunchIn = ref(false);

async function checkPunchInStatus() {
  try {
    const response = await api.post(`${endpoints.timestamps.punchInStatus}`, {
      user_id: authStore.user.id
    });
    hasPunchIn.value = response.data.has_punch_in;
  } catch (error) {
    console.error('Error checking punch-in status:', error);
  }
};

async function punchIn() {
  try {
    const response = await api.post(`${endpoints.timestamps.create}`, {
      user_id: authStore.user.id,
      entered_by: authStore.user.id,
      punch_type: 0,  // 0 for automatic
      reporting_type: null,
      detail: null
    });
    message.value = 'Punched in successfully';
    hasPunchIn.value = true;
  } catch (error) {
    console.error('Error punching in:', error);
  }
};

async function punchOut() {
  try {
    const response = await api.post(`${endpoints.timestamps.punchOut}`, {
      user_id: authStore.user.id,
      entered_by: authStore.user.id,
      reporting_type: null,
      detail: null
    });
    message.value = response.data.message;
    hasPunchIn.value = false;
  } catch (error) {
    if (error.response && error.response.data.action_required === 'manual_punch_in') {
      message.value = 'No punch-in found for today. Please manually add a punch-in entry.';
    } else {
      console.error('Error punching out:', error);
    }
  }
};

onMounted(() => {
  checkPunchInStatus();
});
</script>

<style scoped>
button {
  margin: 10px;
}
</style>

<template>
  <div>
    <h2>Time Watch</h2>
    <div>
      <VBtn @click="punchIn" color="primary">Punch In</VBtn>
      <VBtn @click="punchOut" :disabled="!hasPunchIn" color="secondary">Punch Out</VBtn>
    </div>
    <div v-if="message">
      <VAlert type="warning" dismissible>{{ message }}</VAlert>
    </div>
  </div>
</template>
