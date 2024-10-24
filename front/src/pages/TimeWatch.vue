
<script setup>
// Inject the Axios instance
import { endpoints } from '@/utils/backendEndpoints';
import { useAuthStore } from '@/store/auth';
import { ref, onMounted, computed } from 'vue';

const api = inject('api');
const authStore = useAuthStore();
const message = ref(''); 
const hasPunchIn = ref(false);

async function checkPunchInStatus() {
  try {
    const response = await api.post(`${endpoints.timestamps.punchInStatus}`, {
      user_email: authStore.user.email
    });
    hasPunchIn.value = response.data.has_punch_in;
  } catch (error) {
    console.error('Error checking punch-in status:', error);
  }
};

async function punchIn() {
  try {
    const response = await api.post(`${endpoints.timestamps.create}`, {
      user_email: authStore.user.email,
      entered_by: authStore.user.email,
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
    const response = await api.put(`${endpoints.timestamps.punchOut}`, {
      user_email: authStore.user.email,
      entered_by: authStore.user.email,
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

async function fetchTimeEntries(currentDate) {
  try {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth()   
 + 1, 0);
    const response = await api.get(`${endpoints.timestamps.getRange}/${authStore.user.email}`, {
      params: {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      },
    });
    console.log("")
  } catch (error) {
    console.error('Error fetching time entries:', error);
  }
}

function formatTime(date) {
  if (!date) return ''; // Handle potential undefined or null values
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2,   
 '0');
  return `${hours}:${minutes}:${seconds}`;   

}

function calculateTotalTime(event) {
  // Assuming event has punch_in_time and punch_out_time properties
  const [inHour, inMin] = event.punch_in_time.split(':');
  const [outHour, outMin] = event.punch_out_time.split(':');
  const inTime = new Date(0, 0, 0, inHour, inMin);
  const outTime = new Date(0, 0, 0, outHour, outMin);
  const diffMs = outTime.getTime() - inTime.getTime();
  const diffHrs = Math.floor(diffMs / 1000 / 60 / 60);
  const diffMins = Math.round(((diffMs % 86400000) % 3600000) / 60000);
  return `${diffHrs}h ${diffMins}m`;
}



onMounted(async () => {
  checkPunchInStatus();
  fetchTimeEntries(currentMonth.value);
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