
<script setup>
// Inject the Axios instance
import { endpoints } from '@/utils/backendEndpoints';
import { useAuthStore } from '@/store/auth';
import { ref, onMounted, computed } from 'vue';
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'; 
import { VIcon } from 'vuetify/components/VIcon';
import timestampForm from '@/components/timestampForm.vue'; 


const api = inject('api');
const authStore = useAuthStore();
const message = ref(''); 
const hasPunchIn = ref(false);
const punchOutDescription = ref(''); // Add a ref to store the description
const selectedUser = ref(authStore.user.email);
const selectedUserData = ref([])
const userList = ref([])
const selectedCompany = ref(authStore.user.company_id);
const companyList = ref([])
const currentDate = ref(new Date());
const calendarData = ref([]);
const timestampFormRef = ref(null); 
const weekDays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth());
const availableYears = ref([]); 
const reportingType = ref(null);
const reportingTypeOptions = ref([
  { value: 'work', title: 'Work' },
  { value: 'unpaidoff', title: 'Unpaid Day Off' },
  { value: 'paidoff', title: 'Paid Day Off' },
]);
const availableMonths = ref([
  { title: 'January', value: 0 },
  { title: 'February', value: 1 },
  { title: 'March', value: 2 },
  { title: 'April', value: 3 },
  { title: 'May', value: 4 },
  { title: 'June', value: 5 },
  { title: 'July', value: 6 },
  { title: 'August', value: 7 },
  { title: 'September', value: 8 },
  { title: 'October', value: 9 },
  { title: 'November', value: 10 },
  { title: 'December', value: 11 },
]);

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

const editEntry = (event) => {
  console.log("Editing event: ", event);
  timestampFormRef.value.openForm(event);
};

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
      punch_type: 0,  // 0 for automatic
      reporting_type: "work",
      detail: null
    });
    message.value = 'Punched in successfully';
    hasPunchIn.value = true;
    updateCalendar();
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
      detail: punchOutDescription.value
    });
    message.value = response.data.message;
    hasPunchIn.value = false;
    updateCalendar();
  } catch (error) {
    if (error.response && error.response.data.action_required === 'manual_punch_in') {
      message.value = 'No punch-in found for today. Please manually add a punch-in entry.';
    } else {
      console.error('Error punching out:', error);
    }
  }
};

async function deleteEntry(event) {
  try {
    if (confirm('Are you sure you want to delete this entry?')) { // Confirm deletion
      const response = await api.delete(`${endpoints.timestamps.delete}/${event.id}`);
      console.log(response.data.message); 
      updateCalendar(); // Refresh the calendar after successful deletion
    }
  } catch (error) {
    console.error('Error deleting time entry:', error);
    // Optionally, display an error message to the user
    if (error.response) {
      message.value = 'Error deleting entry: ' + error.response.data.error; 
    } else {
      message.value = 'Error deleting entry.';
    }
  }
}

const addEntry = (dayData) => {
  // Create a new event object with the date from dayData
  const initialDate = new Date(selectedYear.value, selectedMonth.value, dayData.day);
  timestampFormRef.value.openForm(initialDate); 
};

function calculateDailyTotal(events) {
  let totalTime = 0;
  events.forEach(event => {
    if (event.reporting_type === 'paidoff') {
      totalTime += 8 * 3600; // Add 8 hours in seconds for paid days off
    } else {
      totalTime += event.total_time; // Otherwise, add the actual total_time
    }
  });
  return totalTime
}

function calculateDailyTotalString(events) {
  const total = calculateDailyTotal(events)
  return formatTimeFromSeconds(total); 
}

const totalTimeWorkedThisMonth = computed(() => {
  let totalTime = 0;
  calendarData.value.forEach(week => {
    Object.values(week).forEach(day => {
      if (day.events) {
        totalTime += calculateDailyTotal(day.events); // Use calculateDailyTotal here
      }
    });
  });
  return formatTimeFromSeconds(totalTime);
});

function formatTimeFromSeconds(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600).toString().padStart(2, '0');
  const minutes = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0');
  // const seconds = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

function buildCalendar(currentDate) {
  const firstDay = (new Date(currentDate.getFullYear(), currentDate.getMonth())).getDay();
  const daysInMonth = 32 - new Date(currentDate.getFullYear(), currentDate.getMonth(), 32).getDate();
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

    const response = await api.get(`${endpoints.timestamps.getRange}/${selectedUser.value}`, {
      params: {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      },
    });

    const events = response.data.map(entry => ({
      id: entry.uuid,
      inTime: new Date(entry.punch_in_timestamp),
      outTime: entry.punch_out_timestamp ? new Date(entry.punch_out_timestamp) : null, // Check for null
      description: entry.detail? entry.detail : null,
      total_time: entry.total_work_time,
      punchType: entry.punch_type,
      reporting_type: entry.reporting_type
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

          eventsForDay.sort((a, b) => a.inTime - b.inTime); 
          dayData.events = eventsForDay;
        }
      });
    });
  } catch (error) {
    console.error('Error fetching time entries:', error);
  }
}

function formatTime(date) {
  if (!date) return '?';
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  // const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

const updateCalendar = () => {
  console.log("updating calendar");
  currentDate.value = new Date(selectedYear.value, selectedMonth.value); // Update currentDate
  console.log(currentDate.value);
  buildCalendar(currentDate.value); 
  fetchTimeEntries(currentDate.value);
  checkPunchInStatus()
};

// Fetch companies from the API
async function fetchCompanies() {
  try {
    const response = await api.get(`${endpoints.companies.getActive}`);
    companyList.value = response.data; // Access the data property of the response
    console.log('Companies fetched:', companyList.value);
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

async function fetchUsers() {
  try {
    const userResponse = await api.get(`${endpoints.companies.getCompanyUsers}/${selectedCompany.value}/users`);
    userList.value = userResponse.data.map(user => ({
      "company_id": user.company_id,
      "company_name": user.company_name,
      "email": user.email,
      "is_active": user.is_active,
      "mobile_phone": user.mobile_phone,
      "permission": user.permission,
      "role": user.role,
      "salary": user.salary,
      "work_capacity": user.work_capacity,
      "full_name": `${user.first_name} ${user.last_name}` // Added full_name
    }));
    console.log('Users fetched:', userList.value);
  } catch (error) {
    console.error('Error fetching users:', error);
  }
}

async function fetchSelf() {
  try {
    const userResponse = await api.get(`${endpoints.users.getByEmail}/${authStore.user.email}`);
    // Access the first (and only) user object directly
    const user = userResponse.data; 

    selectedUserData.value = {
      "company_id": user.company_id,
      "company_name": user.company_name,
      "email": user.email,
      "is_active": user.is_active,
      "mobile_phone": user.mobile_phone,
      "permission": user.permission,
      "role": user.role,
      "salary": user.salary,
      "work_capacity": user.work_capacity,
      "full_name": `${user.first_name} ${user.last_name}` 
    };

    console.log('User fetched:', selectedUserData.value);
  } catch (error) {
    console.error('Error fetching user:', error);
  }
}

function hasDayOff(dayData) {
  if (dayData && dayData.events) {
    return dayData.events.some(event => 
      event.reporting_type === 'unpaidoff' || event.reporting_type === 'paidoff'
    );
  }
  return false;
}

const hasCurrentDayOff = computed(() => {
  const today = new Date();
  const day = today.getDate();
  const month = today.getMonth();
  const year = today.getFullYear();

  // Find the current day's data in the calendar
  const currentDayData = calendarData.value.flatMap(week => Object.values(week))
    .find(dayData => dayData.day === day);

  return hasDayOff(currentDayData);
});
onMounted(async () => {
  checkPunchInStatus();
  buildCalendar(currentDate.value);
  await fetchTimeEntries(currentDate.value);
  const thisYear = new Date().getFullYear();
  for (let i = thisYear - 5; i <= thisYear + 5; i++) {
    availableYears.value.push(i);
  }
  fetchSelf()
  if (authStore.isNetAdmin || authStore.isEmployer){
    fetchCompanies();
    fetchUsers();
  }
});

watch(selectedMonth, (newMonth) => {
  console.log('Selected month:', newMonth);
  // selectedMonthName.value = monthIntToName(newMonth)
  updateCalendar(); // Trigger calendar update
});

watch(selectedYear, (newYear) => {
  console.log('Selected year:', newYear);
  // selectedMonthName.value = monthIntToName(newMonth)
  updateCalendar(); // Trigger calendar update
});

watch(selectedCompany, (newCompany) => {
  console.log('Selected company:', newCompany);
  fetchUsers().then(() => { // Ensure fetchUsers completes before selecting a user
    selectedUser.value = ''; // Or '' if you prefer an empty string
  });
});

watch(selectedUser, (newUser) => {
  console.log('Selected User:', newUser);
  selectedUserData.value = userList.value.find(user => user.email === selectedUser.value);
  updateCalendar();
});

</script>


<style scoped>
.punch-buttons {
  display: flex;
  align-items: flex-end; /* Align to the bottom of the container */
}

.punch-out-group {
  display: flex;
  align-items: flex-end; /* Align items to the bottom */
  margin-left: 15px; /* Add space between button groups */
}

.punch-button {
  margin: 15px 0; /* Top/bottom margin, no left/right */
  height: 60px;
  font-size: 22px;
  width: 150px;
}

.description-field {
  margin: 15px; /* Add space between button and input */
  height: 60px;
  width: 300px; /* Adjust width as needed */
  align-self: flex-end; 
}

.description-field textarea { 
  resize: none; /* Prevent manual resizing */
}

.user-info {
  background-color: #f5f5f5; /* Light background color */
  border: 1px solid #ccc;  /* Subtle border */
  padding: 20px;           /* Increased padding */
  border-radius: 8px;      /* More rounded corners */
  margin-bottom: 20px;      /* Space between this section and the next */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow */
}

.info-item {
  display: flex;           /* Use flexbox for layout */
  align-items: center;   /* Align items to the baseline */ 
  margin-bottom: 15px;     /* Increased space between items */
}

.info-item .label {
  font-weight: bold;       /* Make labels bold */
  font-size: 18px;        /* Increased font size for labels */
  margin-right: 10px;      /* Space between label and value */
}

.user-info .v-select { /* Target v-select inside .user-info */
  align-self: /* Adjust this value as needed */
}

.info-item .value {
  font-size: 20px;        /* Increased font size for values */
}

.user-info .v-row {  /* Target v-row inside .user-info */
  margin-bottom: 0px; 
}
  
.user-info .v-col { /* Target v-col inside .user-info */
  padding: 0 10px; /* Add some horizontal padding within columns */
}

table {
  width: 100%;
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
  display: flex;
  padding-top: 30px;
  height: 100%;
  flex-direction: column;
  align-items: center;
}

.calendar-cell::before {
  content: '';
  display: block;
  padding-top: 25%; /* Maintain aspect ratio */
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
  flex-direction: column;
}

.day-number {
  font-size: 1em;
  font-weight: bold;
  color: #333; /* Dark gray text */
}

.event-list {
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  order: -1;
  margin-top: 10px; 
  width: 100%;
  text-align: left;
}

.event-list ul {
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  padding-left: 0px;
  list-style-type:disc;
  text-align: left;
  list-style-position: inside;
}

.event-list li {
  align-items: center;
  justify-content: space-between;
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  font-size: 1em;
  margin-top: 5px;
  text-align: left
  
}

.calendar-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.total-time {
    white-space: nowrap;
    overflow: hidden; 
    text-overflow: ellipsis;
    font-weight: bold;
    position: absolute; 
    bottom: 5px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0 5px;
    font-size: 1em; /* Slightly smaller font size */
  }

.add-entry-button {
  position: absolute;
  top: 0px; 
  right: 5px; 
}
  
.event-description {
  display: block;  /* Or inline-block */
  font-size: 0.8em;
  margin-top: 5px;
}

.day-off-message {
  color: red; /* Or any color you prefer */
  font-weight: bold;
  margin-bottom: 10px; /* Add some spacing below the message */
  font-size: 1.2em;
}

</style>

<template>
  <div>
    <h2>Time Watch</h2>
    <div v-if="selectedUser === authStore.user.email" class="punch-buttons">
      <VBtn @click="punchIn" :disabled="hasPunchIn || hasCurrentDayOff" color="primary" class="punch-button">Punch In</VBtn>
      <div class="punch-out-group">
        <VBtn @click="punchOut" :disabled="!hasPunchIn || hasCurrentDayOff" color="primary" class="punch-button">Punch Out</VBtn>
        <VTextarea
        v-if="hasPunchIn"
        v-model="punchOutDescription"
        label="Task Description"
        placeholder="Enter task description"
        class="description-field"
        auto-grow
        rows="1" 
        />
      </div>
    </div>
    <div v-if="hasCurrentDayOff" class="day-off-message">
      Day Off - Cannot Punch In/Out
    </div>
    <div v-if="message">
      <VAlert
        type="warning"
        dismissible
        @click:close="() => { console.log('Clicked'); message = '' }"
        style="z-index: 10"
      >
        {{ message }}
    </VAlert>
    </div>
    <br>

    <div class="user-info"> 
        <div class="info-item full-width"> 
          <span class="label">Company:</span>
          <VSelect
          v-if="authStore.isNetAdmin"
          v-model="selectedCompany"
          :items="companyList"
          item-title="company_name"
          item-value="company_id"
        ></VSelect>
        <span v-else class="value">{{ authStore.user.company_name }}</span> 
      </div>
      
      <div class="info-item full-width">
        <span class="label">User:</span>
        <VSelect
          v-if="authStore.isNetAdmin || authStore.isEmployer" 
          :items="userList"
          item-title="full_name"
          item-value="email"
          v-model="selectedUser"
        ></VSelect>
        <span v-else class="value">{{ authStore.user.f_name }} {{ authStore.user.l_name }}</span> 
      </div>

       <VRow no-gutters>
        <VCol cols="6" sm="6" md="6" lg="6"> 
          <div class="info-item">
            <span class="label">Email:</span>
            <span class="value">{{ selectedUser }}</span>
          </div>
          <div class="info-item">
            <span class="label">Role:</span>
            <span class="value">{{ selectedUserData.role }}</span>
          </div>
          <div class="info-item">
            <span class="label">Total time worked in {{ selectedMonth + 1 }}/{{ selectedYear }}:</span>
            <span class="value">{{ totalTimeWorkedThisMonth }} Hours</span>
          </div>
        </VCol>
        <VCol cols="6" sm="6" md="6" lg="6"> 
          <div class="info-item">
            <span class="label">Phone:</span>
            <span class="value">{{ selectedUserData.mobile_phone }}</span>
          </div>
          <div class="info-item">
            <span class="label">Salary:</span>
            <span class="value">{{ selectedUserData.salary }} USD</span>
          </div>
          <div class="info-item">
            <span class="label">Work Capacity:</span>
            <span class="value">{{ selectedUserData.work_capacity }} Hours</span>
          </div>
         
        </VCol>
      </VRow>
    </div>

    <br>
    <div class="calendar-controls"> 
      <VSelect
        v-model="selectedYear"
        :items="availableYears"
        label="Year"
      ></VSelect>

      <VSelect 
        v-model="selectedMonth"
        :items="availableMonths"
        label="Month"
        item-text="title"
        item-value="value"
      ></VSelect>
    </div>

    <SimpleTable :headers="calendarHeaders" :items="calendarData">
      <template v-for="dayName in weekDays" :key="dayName" v-slot:[`item.${dayName}`]="{ item }">
        <div class="calendar-cell"> 
          <div v-if="item[dayName]?.day" class="day-number-frame">
            <span class="day-number">{{ item[dayName].day }}</span>
          </div>
          <IconBtn v-if="item[dayName]?.day && !hasDayOff(item[dayName])" class="add-entry-button" @click="addEntry(item[dayName])"> 
            <VIcon icon="ri-add-circle-fill" color="primary" size="18" /> 
          </IconBtn>
          <span class="total-time" v-if="item[dayName]?.events?.length">
            Total: {{ calculateDailyTotalString(item[dayName].events) }}
          </span>
          <div v-if="item[dayName]?.events?.length" class="event-list">
            <ul>
              <li v-for="event in item[dayName].events" :key="event.id">
                <VTooltip location="top">  
                  <template v-slot:activator="{ props }">
                    <span v-if="event.reporting_type === 'work'" v-bind="props">
                      {{ formatTime(event.inTime) }} - {{ formatTime(event.outTime) }}
                    </span>
                    <span v-if="event.reporting_type === 'unpaidoff'" v-bind="props">
                      <strong>Unpaid Day Off</strong>
                    </span>
                    <span v-if="event.reporting_type === 'paidoff'" v-bind="props">
                      <strong>Paid Day Off</strong>
                    </span>
                  </template>
                  <span>{{ event.description }}</span>
                </VTooltip>
                <IconBtn @click="editEntry(event)"> 
                  <VIcon icon="ri-edit-line" size="18" /> 
                </IconBtn>
                <IconBtn @click="deleteEntry(event)">
                  <VIcon icon="ri-delete-bin-line" size="18" /> 
                </IconBtn>
              </li>
            </ul>
          </div>
        </div>
        <timestampForm ref="timestampFormRef" 
                 @timestampCreated="updateCalendar"  
                 @timestampUpdated="updateCalendar"
                 :selectedUser="selectedUser" /> 
      </template>
    </SimpleTable>
  </div>
</template>