<template>
    <div>
      <h2>Reports</h2>
  
      <div class="filters">
        <div class="report-type-select-container">
            <VSelect
                v-if="authStore.isNetAdmin || authStore.isEmployer"
                v-model="reportType"
                :items="reportTypeOptions"
                label="Report Type"
                density="compact"
                style="min-width: 150px;"
            ></VSelect>
            <v-text-field
                v-else-if="authStore.isEmployee"
                :value="`User Report`"
                label="Report Type"
                readonly
                variant="outlined"
                density="compact"
                persistent-placeholder
            />
        </div>
    
        <VSelect
          v-if="authStore.isNetAdmin"
          v-model="selectedCompany"
          :items="companyList"
          item-title="company_name"
          item-value="company_id"
          label="Company"
          density="compact"
          style="min-width: 150px;"
        ></VSelect>
        <div v-else-if="authStore.isEmployer || authStore.isEmployee" class="company-display" style="min-width: 150px;">
            <v-text-field
              v-model="authStore.user.company_name"
              label="Company"
              readonly
              variant="outlined"
              density="compact"
            />
          </div>
          
        <div v-if="reportType === 'user'" class="user-select-container">
            <VSelect
                v-if="authStore.isEmployer || authStore.isNetAdmin"
                v-model="selectedUser"
                :items="filteredUserList"  
                item-title="full_name"
                item-value="email"
                label="User"
                density="compact"
            ></VSelect>

            <VTextField
                v-else-if="authStore.isEmployee"
                :value="`${authStore.user.f_name} ${authStore.user.l_name}`"
                label="User"
                readonly
                variant="outlined"
                density="compact"
                persistent-placeholder
                />
        </div>
  
        <VSelect
          v-model="dateRangeType"
          :items="dateRangeOptions"
          label="Date Range"
          density="compact"
          style="min-width: 150px;"
        ></VSelect>
  
        <div v-if="dateRangeType === 'monthly'" class="month-year-select"> 
          <VSelect
            v-model="selectedYear"
            :items="availableYears"
            label="Year"
            density="compact"
          ></VSelect>
  
          <VSelect
            v-model="selectedMonth"
            :items="availableMonths"
            item-text="title"
            item-value="value"
            label="Month"
            density="compact"
            style="min-width: 150px;"
          ></VSelect>
        </div>
  
        <div v-if="dateRangeType === 'custom'" class="date-pickers">
          <VDatePicker class="my-datepicker" v-model="startDate" label="Start Date" density="compact"></VDatePicker>
          <VDatePicker class="my-datepicker" v-model="endDate" label="End Date" density="compact"></VDatePicker>
        </div>
  
        <VBtn @click="generateReport" color="primary">Generate Report</VBtn>
      </div>
  
      <div v-if="reportData && reportType === 'user'" class="report-section">
        <h3>Report for {{ reportData.employeeName }}
            <span class="date-range">({{ formattedDateRange }})</span>
        </h3> 
        <div class="user-details"> 
            <VRow>
                <VCol cols="3"> 
                  <p><strong>Email:</strong> {{ reportData.userDetails.email }}</p>
                  <p><strong>Role:</strong> {{ reportData.userDetails.role }}</p>
                  <p><strong>Phone:</strong> {{ reportData.userDetails.phone }}</p>
                </VCol>
                <VCol cols="3"> 
                  <p><strong>Salary:</strong> ${{ reportData.userDetails.salary }}</p>
                  <p><strong>Work Capacity:</strong> {{ reportData.userDetails.workCapacity }}</p>
                </VCol>
              </VRow>
        </div>
        <p>Dates Worked: {{ formattedDatesWorked }}</p>
        <p>Dates Missed: {{ formattedDatesMissed }}</p>
        <p>Total Hours Worked: {{ reportData.totalHoursWorked }}</p>
        <p>Total Payment Required: ${{ parseFloat(reportData.totalPaymentRequired).toFixed(2) }}</p> 
  
        <h3>Daily Breakdown</h3>
        <SimpleTable :headers="dailyBreakdownHeaders" :items="reportData.dailyBreakdown">
          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>
          <template v-slot:item.hoursWorked="{ item }">
            {{ item.hoursWorked }}
          </template>
        </SimpleTable>
      </div>
      
      <div v-else-if="reportData && reportType === 'company'" class="report-section"> 
      <h3>{{ companyName }} Report
        <span class="date-range">({{ formattedDateRange }})</span> 
      </h3>
      <div class="company-summary">
        <VRow>
          <VCol cols="3">
            <p v-if="adminNames.length"><strong>Admin(s):</strong> {{ adminNames.join(', ') }}</p>
            <p><strong>Employees:</strong> {{ reportData.length }}</p> 
            
          </VCol>
          <VCol cols="3">
            <p><strong>Total Salary:</strong> ${{ totalSalary.toFixed(2) }}</p> 
            <p><strong>Total Hours Worked:</strong> {{ totalHoursWorked }}</p> 
          </VCol>
        </VRow>
      </div>
        <SimpleTable :headers="reportHeaders" :items="reportData">
          <template v-slot:item.employeeName="{ item }">
          {{ item.employeeName }}
          </template>
          <template v-slot:item.role="{ item }">
          {{ item.userDetails.role }}
          </template>
          <template v-slot:item.workCapacity="{ item }">
          {{ item.userDetails.workCapacity }}
          </template>
          <template v-slot:item.salary="{ item }">
          {{ item.userDetails.salary }}
          </template>
        </SimpleTable>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useAuthStore } from '@/store/auth';
  import { endpoints } from '@/utils/backendEndpoints';
  import SimpleTable from '@/views/pages/tables/SimpleTable.vue'; 
  
  const api = inject('api');
  const authStore = useAuthStore();
  
  // Filters
  const selectedCompany = ref(null); 
  const selectedUser = ref(null);
  const dateRangeType = ref('monthly');
  const selectedYear = ref(new Date().getFullYear());
  const selectedMonth = ref(new Date().getMonth());
  const startDate = ref(null);
  const endDate = ref(null);
  
  // Data
  const companyName = ref([]);
  const adminNames = ref([]);
  const reportData = ref(null);
  const companyList = ref([]); 
  const userList = ref([]);
  const dateRangeOptions = ref([
      { value: 'monthly', title: 'Monthly' },
      { value: 'custom', title: 'Custom' },
    ]);
  const dateRange = ref({  // Initialize dateRange as a ref
    type: dateRangeType.value,
    year: selectedYear.value,
    month: selectedMonth.value,
    startDate: startDate.value,
    endDate: endDate.value,
    });
  const reportType = ref('user'); 
  const reportTypeOptions = ref([
    { value: 'user', title: 'User Report' },
    { value: 'company', title: 'Company Report' },
]);
  const availableYears = ref([]);
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

  const reportHeaders = ref([
  { text: 'Name', value: 'employeeName' },
  { text: 'Role', value: 'role' },
  { text: 'Hourly Salary', value: 'salary' },
  { text: 'Hours Worked', value: 'totalHoursWorked' },
  { text: 'Work Capacity', value: 'workCapacity' },
  { text: 'Days Worked', value: 'daysWorked' },
  { text: 'Days Not Worked', value: 'daysNotWorked' },
  { text: 'Total Salary', value: 'totalPaymentRequired' },
]);
  
  // Table Headers
  const dailyBreakdownHeaders = ref([
    { text: 'Date', value: 'date' },
    { text: 'Hours Worked', value: 'hoursWorked' },
  ]);
  
  // Computed properties for filtering userList based on selectedCompany
  const filteredUserList = computed(() => {
    if (!selectedCompany.value) return userList.value;
    return userList.value.filter(user => user.company_id === selectedCompany.value);
  });
  
  const totalHoursWorked = computed(() => {
    let totalSeconds = 0;
    if (reportData.value) {
    reportData.value.forEach(user => {
      const [hours, minutes] = user.totalHoursWorked.split(':').map(Number);
      totalSeconds += hours * 3600 + minutes * 60;
    });
  }
  const totalHours = Math.floor(totalSeconds / 3600);
  const totalMinutes = Math.floor((totalSeconds % 3600) / 60);
  return `${totalHours.toString().padStart(2, '0')}:${totalMinutes.toString().padStart(2, '0')}`;
});

  const totalSalary = computed(() => {
  let salary = 0;
  if (reportData.value && reportData.value.length > 0) { 
    salary = reportData.value.reduce((sum, user) => user.totalPaymentRequired ? sum + parseFloat(user.totalPaymentRequired) : 0, 0); 
  }
  return salary;
});

  const formattedDateRange = computed(() => {
  if (dateRangeType.value === 'monthly') {
    const monthName = availableMonths.value[dateRange.value.month].title;
    const start_Date = new Date(dateRange.value.year, dateRange.value.month, 1).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    const end_Date = new Date(dateRange.value.year, dateRange.value.month + 1, 0).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    return `${start_Date} - ${end_Date}`; 
  } else {
    return `${formatDate(startDate.value)} - ${formatDate(endDate.value)}`;
  }
});
  // Watchers to update the selectedUser when filteredUserList changes
  watch(filteredUserList, (newFilteredUserList) => {
    // Reset selectedUser if it's not in the new filtered list
    if (!newFilteredUserList.find(user => user.email === selectedUser.value)) {
      selectedUser.value = null; 
    }
  });
  
  // Computed properties for formatted dates worked and missed
  const formattedDatesWorked = computed(() => {
     if (!reportData.value || !reportData.value.datesWorked) return ''
    return reportData.value.datesWorked.map(date => formatDate(date)).join(', ');
  });
  
  const formattedDatesMissed = computed(() => {
     if (!reportData.value || !reportData.value.datesMissed) return ''
    return reportData.value.datesMissed.map(date => formatDate(date)).join(', ');
  });
  
  async function fetchCompanies() {
    try {
      const response = await api.get(endpoints.companies.getActive);
      companyList.value = response.data;
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  }
  
  async function fetchUsers() {
    try {
      const response = await api.get(`${endpoints.companies.getCompanyUsers}/${selectedCompany.value}/users`);
      userList.value = response.data.map(user => ({
        "company_id": user.company_id,
        "email": user.email,
        "full_name": `${user.first_name} ${user.last_name}` 
      }));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }
  
  async function generateReport() {
    try {
      const params = {
        company_id: selectedCompany.value,
        dateRangeType: dateRangeType.value,
        };
  
      if (dateRangeType.value === 'monthly') {
        params.year = selectedYear.value;
        params.month = selectedMonth.value + 1; // Month is 0-indexed
      } else {
        params.start_date = startDate.value.toISOString();
        params.end_date = endDate.value.toISOString();
      }
      
      let endpoint = endpoints.reports.generateUser; 
      if (reportType.value === 'company') {
        endpoint = endpoints.reports.generateCompany; 
      } else {
        params.user_email = selectedUser.value; 
      }
      const response = await api.get(endpoint, { params });
      console.log( response.data) // Log the response data
      reportData.value = response.data;

      if (reportType.value === 'company') {
        companyName.value = companyList.value.find(c => c.company_id === selectedCompany.value)?.company_name || '';
        // Fetch admin names for the company (replace with your actual API call)
        const adminsResponse = await api.get(`${endpoints.companies.getCompanyAdmins}/${selectedCompany.value}/admins`); 
        adminNames.value = adminsResponse.data.map(admin => admin.first_name + ' ' + admin.last_name); 
      }
  
    } catch (error) {
      console.error('Error generating report:', error);
      // Handle error, e.g., show an error message to the user
    }
  }
  
  function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  }
  
  onMounted(async () => {
    const thisYear = new Date().getFullYear();
    for (let i = thisYear - 5; i <= thisYear + 5; i++) {
      availableYears.value.push(i);
    }
    if (authStore.isNetAdmin){
      fetchCompanies();
    } else if (authStore.isEmployer) {
      selectedCompany.value = authStore.user.company_id;
      fetchUsers(); // Call fetchUsers here to populate the user list
    }
  });
  
  watch(selectedCompany, (newCompany) => {
    if (newCompany) {
      fetchUsers();
    } else {
      userList.value = []; 
      selectedUser.value = null; 
    }
  });
  watch(reportType, () => {
    // Reset reportData, selectedUser, and dateRange when reportType changes
    reportData.value = null;
    selectedUser.value = null;
    dateRangeType.value = 'monthly'; // Reset date range type
    selectedYear.value = new Date().getFullYear(); // Reset year
    selectedMonth.value = new Date().getMonth(); // Reset month
    startDate.value = new Date(selectedYear.value, selectedMonth.value, 1); // Reset start date
    endDate.value = new Date(selectedYear.value, selectedMonth.value + 1, 0); // Reset end date

    // If switching to company report and not a net admin, reset selectedCompany
    if (reportType.value === 'company' && !authStore.isNetAdmin) {
        selectedCompany.value = authStore.user.company_id;
    }
  });

  </script>
  
  <style scoped>
  .filters {
    display: flex;
    flex-wrap: nowrap; /* Prevent wrapping to keep everything in one line */
    gap: 15px;
    margin-top: 20px;
    margin-bottom: 20px;
    align-items: center; /* Vertically align items in the center */
  }
  
  .filters > * {
    flex: 0 0 auto; /* Prevent items from growing to fill the space */
  }
  
  .report-section {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .report-section h3 {
    margin-bottom: 15px;
}

.report-section p {
  margin-bottom: 10px;
}

.v-table {
  border-collapse: collapse;
  width: 100%;
}

.v-table th,
.v-table td {
  border: 1px solid #ccc;
  padding: 10px;
  text-align: left;
}

.v-table th {
  background-color: #f0f0f0;
}

.month-year-select { 
  display: flex;
  gap: 15px;  
}

.month-year-select > * {  
  flex: 1 1 0px; 
}

.user-details { /* Style for the user details section */
    margin-bottom: 20px; 
  }
  
.user-details p {
    margin-bottom: 8px; /* Add some space between the details */
  }
  
.user-details strong { /* Make the labels bold */
    font-weight: bold;
  }

.date-pickers {  /* New style for the date pickers */
    display: flex;
    gap: 15px;
  }
  
.date-pickers {  /* New style for the date pickers */
    display: flex;
    gap: 15px;
  }

.date-range { /* Style for the date range span */
    font-size: 0.8em; /* Slightly smaller font size */
    font-weight: normal; /* Normal font weight */
    margin-left: 10px; /* Add some space to the left */
  }

.my-datepicker {
    font-size: 14px;
    display: flex;
}
  
.company-display .v-input__slot {
  text-align: center;
  width: auto;
}

.user-select-container {
    min-width: 150px;
    flex: 1 1 auto;  /* Allow both growing and shrinking */
    max-width: 300px; /* Set a maximum width */ 
    width: auto;
  }

.report-type-select-container {
    min-width: 150px;
    flex: 1 1 auto;  /* Allow both growing and shrinking */
    max-width: 200px; /* Set a maximum width */ 
    width: auto;
  }

</style>