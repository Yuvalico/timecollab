
<script setup>
// Inject the Axios instance
import { endpoints } from '@/utils/backendEndpoints';
import { useAuthStore } from '@/store/auth';
import { ref, onMounted, computed } from 'vue';
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'; // Assuming this is the correct path


const api = inject('api');
const authStore = useAuthStore();
const message = ref(''); 
const hasPunchIn = ref(false);
const currentMonth = ref(new Date());
const calendarData = ref([]);
const weekDays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

const calendarHeaders = ref([
  { text: 'Sun', value: 'sunday' },
  { text: 'Mon', value: 'monday' },
  { text: 'Tue', value: 'tuesday' },
  { text: 'Wed', value: 'wednesday' },
  { text: 'Thu', value: 'thursday' },
  { text: 'Fri', value: 'friday'   
 },
  { text: 'Sat', value: 'saturday'   
 },
]);


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

function buildCalendar(currentMonth) {
  const firstDay = (new Date(currentMonth.getFullYear(), currentMonth.getMonth())).getDay();
  const daysInMonth = 32 - new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 32).getDate();
  const days = [];
  let dayCounter = 1;

  for (let i = 0; i < 6; i++) {
    let isEmptyWeek = true;
    const week = {};

    for (let j = 0; j < 7; j++) {
      const dayName = weekDays[j];
      if (i === 0 && j < firstDay) {
        week[dayName] = '';
      } else if (dayCounter > daysInMonth) {
        week[dayName] = '';
      } else {
        week[dayName] = {
          day: dayCounter,
          events: [],
        };
        dayCounter++;
        isEmptyWeek = false;
      }
    }
    if (!isEmptyWeek) {
      days.push(week);
    }
  }
  calendarData.value = days;
}


async function fetchTimeEntries(currentDate) {
  try {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    const response = await api.get(`${endpoints.timestamps.getRange}/${authStore.user.email}`, {
      params: {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      },
    });

    const events = response.data.map(entry => ({
      id: entry.uuid,
      inTime: new Date(entry.punch_in_timestamp),
      outTime: new Date(entry.punch_out_timestamp),
      total_time: entry.total_work_time,
    }));

    // Iterate over the calendar data to populate events for each day
    calendarData.value.forEach((week, weekIndex) => {
      Object.keys(week).forEach(dayName => {
        const dayData = week[dayName];
        if (dayData && dayData.day) {
          const eventsForDay = events.filter(event => {
            return (
              event.inTime.getDate() === dayData.day &&
              event.inTime.getMonth() === currentDate.getMonth() &&
              event.inTime.getFullYear() === currentDate.getFullYear()
            );
          });
          dayData.events = eventsForDay;
        }
      });
    });
  } catch (error) {
    console.error('Error fetching time entries:', error);
  }
}


function formatTime(date) {
  if (!date) return '';
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}


onMounted(async () => {
  checkPunchInStatus();
  buildCalendar(currentMonth.value);
  await fetchTimeEntries(currentMonth.value);
});

watch(currentMonth, async (newCurrentMonth) => {
  buildCalendar(newCurrentMonth);
  await fetchTimeEntries(newCurrentMonth);
});

</script>


<style scoped>
button {
  margin: 10px;
}

table {
  width: 80%;
  border-collapse: collapse;
  table-layout: fixed;
}

th, td {
  border: 1px solid #ccc;
  text-align: center;
  padding: 10px;
  height: 120px; /* Adjust height as needed */
  position: relative;
}

.calendar-cell {
  position: relative;
  height: 100%;
  padding-top: 30px; /* Space for the day number */
  display: flex;
  flex-direction: column;
  align-items: center;
}

.day-number-frame {
  position: absolute;
  top: 5px; /* Distance from the top border */
  left: 50%;
  transform: translateX(-50%);
  background-color: #e2c6f5; 
  border-radius: 50%;
  width: 25px; 
  height: 25px; 
  display: flex;
  justify-content: center;
  align-items: center;
}

.day-number {
  font-size: 1em;
  font-weight: bold;
  color: #333; /* Dark gray text */
}

.event-list {
  margin-top: 10px; 
  width: 100%;
  text-align: left;
}

.event-list ul {
  padding-left: 10px;
  list-style-type: none;
}

.event-list li {
  font-size: 0.85em;
  margin-bottom: 5px;
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
    <br>
    <SimpleTable :headers="calendarHeaders" :items="calendarData">
      <template v-for="dayName in weekDays" 
                :key="dayName" 
                v-slot:[`item.${dayName}`]="{ item }">
        <div class="calendar-cell"> 
          <div v-if="item[dayName]?.day" class="day-number-frame"> 
            <span class="day-number">{{ item[dayName].day }}</span>
          </div>
          <div v-if="item[dayName]?.events?.length" class="event-list">
            <ul>
              <li v-for="event in item[dayName].events" :key="event.id">
                <span>{{ formatTime(event.inTime) }} - {{ formatTime(event.outTime) }}</span>
                <span>Total: {{ event.total_time }}</span>
              </li>
            </ul>
          </div>
        </div>
      </template>
    </SimpleTable>
  </div>
</template>