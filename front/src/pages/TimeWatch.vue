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

<script>
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

export default {
  data() {
    return {
      message: '',
      hasPunchIn: false
    };
  },
  created() {
    this.checkPunchInStatus();
  },
  methods: {
    async checkPunchInStatus() {
      try {
        const response = await axios.post('http://localhost:3000/api/timestamps/punch_in_status', {
          user_id: this.authStore.user.id
        });
        this.hasPunchIn = response.data.has_punch_in;
      } catch (error) {
        console.error('Error checking punch-in status:', error);
      }
    },
    async punchIn() {
      try {
        const response = await axios.post('http://localhost:3000/api/timestamps/', {
          user_id: this.authStore.user.id,
          entered_by: this.authStore.user.id,
          punch_type: 0,  // 0 for automatic
          reporting_type: null,
          detail: null
        });
        this.message = 'Punched in successfully';
        this.hasPunchIn = true;
      } catch (error) {
        console.error('Error punching in:', error);
      }
    },
    async punchOut() {
      try {
        const response = await axios.post('http://localhost:3000/api/timestamps/punch_out', {
          user_id: this.authStore.user.id,
          entered_by: this.authStore.user.id,
          reporting_type: null,
          detail: null
        });
        this.message = response.data.message;
        this.hasPunchIn = false;
      } catch (error) {
        if (error.response && error.response.data.action_required === 'manual_punch_in') {
          this.message = 'No punch-in found for today. Please manually add a punch-in entry.';
        } else {
          console.error('Error punching out:', error);
        }
      }
    }
  },
  computed: {
    authStore() {
      return useAuthStore();
    }
  }
};
</script>

<style scoped>
button {
  margin: 10px;
}
</style>
