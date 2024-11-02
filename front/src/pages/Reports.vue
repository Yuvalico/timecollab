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
          v-if="authStore.isNetAdmin && (reportType === 'user' || reportType === 'company')"
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
          <VDatePicker 
            class="my-datepicker" 
            v-model="startDate" 
            title="Start Date" 
            label="Start Date" 
            density="compact">
          </VDatePicker>
          <VDatePicker 
            class="my-datepicker" 
            v-model="endDate" 
            title="End Date" 
            label="End Date" 
            density="compact">
          </VDatePicker>
        </div>
  
        <VBtn @click="generateReport" color="primary" :disabled="!areReportFieldsFilled">Generate Report</VBtn>
        
      </div>
      <div v-if="serverErrorMessage" class="server-error"> 
        {{ serverErrorMessage }}
      </div>
  
      <div v-if="reportData && reportType === 'user'" class="report-section">
        <h3>Report for {{ reportData.employeeName }}
            <span class="date-range">({{ formattedDateRange }})</span>
        </h3> 
        <div class="user-details"> 
            <VRow>
                <VCol cols="3"> 
                  <p><strong>Email:</strong> {{ reportData.userDetails.email }}</p>
                  <p><strong>Phone:</strong> {{ reportData.userDetails.phone }}</p>
                  <p><strong>Role:</strong> {{ reportData.userDetails.role }}</p>
                  <p v-if="authStore.isNetAdmin || authStore.isEmployer">
                    <strong>Company: </strong> 
                    <a href="#" @click.prevent="generateCompanyReport(getCompanyName(selectedCompany))">{{ getCompanyName(selectedCompany) }}</a>
                  </p> 
                  <p v-else><strong>Company: </strong> {{ authStore.user.company_name }}</p> 
                </VCol>
                <VCol cols="3"> 
                  <p><strong>Hourly Salary:</strong> ${{ reportData.userDetails.salary }}</p>
                  <p><strong>Daily Work Capacity:</strong> {{ reportData.userDetails.workCapacity }}</p>
                  
                </VCol>
              </VRow>
        </div>

        <div class="user-details"> 
            <VRow>
                <VCol cols="3"> 
                  <p><strong>Potential Work Days:</strong> {{ reportData.potentialWorkDays }}</p> 
                  <p><strong>Days Worked:</strong> {{ reportData.daysWorked }}</p>
                  <p><strong>Paid Days Off:</strong> {{ reportData.paidDaysOff }}</p>
                  <p><strong>Unpaid Days Off:</strong> {{ reportData.unpaidDaysOff }}</p>
                  <p><strong>Days Not Reported:</strong> {{ reportData.daysNotReported }}</p>
                </VCol>
                <VCol cols="3"> 
                  <p><strong>Total Hours Potential: </strong>{{ reportData.workCapacityforRange }}</p>
                  <p><strong>Total Hours Worked: </strong>{{ reportData.totalHoursWorked }}</p>
                  <p><strong>Total Payment Required: </strong> ${{ parseFloat(reportData.totalPaymentRequired).toFixed(2) }}</p> 
                  
                </VCol>
              </VRow>
        </div>

        <h3>Daily Breakdown</h3>
        <SimpleTable :headers="dailyBreakdownHeaders" :items="reportData.dailyBreakdown" :rowBgColor="item => isWeekend(new Date(item.date).toLocaleDateString('en-US', { weekday: 'long' })) ? '#d3d3d3' : null" >
          <template v-slot:item.date="{ item }">
            <span>
            {{ formatDate(item.date) }}
          </span>
          </template>
          <template v-slot:item.hoursWorked="{ item }">
            {{ item.hoursWorked }}
          </template>
          <template v-slot:item.reportingType="{ item }">
            <span v-if="isWeekend(new Date(item.date).toLocaleDateString('en-US', { weekday: 'long' }))">Weekend</span>
            <span v-else-if="item.reportingType === 'work'">Work</span>
            <span v-else-if="item.reportingType === 'unpaidoff'">Unpaid Day Off</span>
            <span v-else-if="item.reportingType === 'paidoff'">Paid Day Off</span>
            <span v-else>Not Reported</span>
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
            <a href="#" @click.prevent="generateUserReport(item.userDetails.email)">{{ item.employeeName }}</a> 
          </template>
          <template v-slot:item.role="{ item }">
          {{ item.userDetails.role }}
          </template>
          <template v-slot:item.dailyWorkCapacity="{ item }">
          {{ item.userDetails.workCapacity }}
          </template>
          <template v-slot:item.salary="{ item }">
          {{ item.userDetails.salary }}
          </template>
        </SimpleTable>
      </div>
      <div v-if="reportData && reportType === 'overview'" class="report-section">
        <h3>Company Overview Report
            <span class="date-range">({{ formattedDateRange }})</span> 
        </h3>
        <div class="company-summary">
            <VRow>
              <VCol cols="3">
                <p><strong>Total Companies:</strong> {{ reportData.length }}</p>
                <p><strong>Total Employees:</strong> {{ totalEmployeesOverview }}</p> 
                
              </VCol>
              <VCol cols="3">
                <p><strong>Total Salary:</strong> ${{ totalSalaryOverview }}</p> 
              </VCol>
            </VRow>
          </div>
        <SimpleTable :headers="companyOverviewHeaders" :items="reportData">
          <template v-slot:item.companyName="{ item }">
            <a href="#" @click.prevent="generateCompanyReport(item.companyName)">{{ item.companyName }}</a> 
          </template>
          <template v-slot:item.adminNames="{ item }"> 
            {{ item.adminNames.join(', ') }}  
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
  const selectedCompany = ref(authStore.user.company_id); 
  const selectedUser = ref(authStore.user.email);
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
  const serverErrorMessage = ref(null); 
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

// Add conditional logic for Overview report
if (authStore.isNetAdmin) {
  reportTypeOptions.value.push({ 
    value: 'overview', 
    title: 'Company Overview' 
  });
}

const companyOverviewHeaders = ref([
  { text: 'Company Name', value: 'companyName' },
  { text: 'Admin Users', value: 'adminNames' }, 
  { text: 'Employees', value: 'numEmployees' },
  { text: 'Total Hours Worked', value: 'totalHoursWorked' },
  { text: 'Total Monthly Salary', value: 'totalMonthlySalary' },
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
  { text: 'Daily Capacity', value: 'dailyWorkCapacity' },
  { text: 'Days Worked', value: 'daysWorked' },
  { text: 'Paid Days Off', value: 'paidDaysOff' }, 
  { text: 'Unpaid Days Off', value: 'unpaidDaysOff' }, 
  { text: 'Days Not Reported', value: 'daysNotReported' },
  { text: 'Total Days Potential', value: 'potentialWorkDays' },
  { text: 'Total Hours Potential', value: 'workCapacityforRange' },
  { text: 'Hours Worked', value: 'totalHoursWorked' },
  { text: 'Hourly Salary', value: 'salary' },
  { text: 'Total Salary', value: 'totalPaymentRequired' },
]);
  
  // Table Headers
  const dailyBreakdownHeaders = ref([
    { text: 'Date', value: 'date' },
    { text: 'Hours Worked', value: 'hoursWorked' },
    { text: 'Reporting Type', value: 'reportingType' }, 
  ]);


  // Computed properties for filtering userList based on selectedCompany
  const filteredUserList = computed(() => {
    if (!selectedCompany.value) return userList.value;
    return userList.value.filter(user => user.company_id === selectedCompany.value);
  });
  
  const totalEmployeesOverview = computed(() => {
  return reportData.value.reduce((sum, company) => sum + company.numEmployees, 0);
});

const totalSalaryOverview = computed(() => {
  return reportData.value.reduce((sum, company) => sum + company.totalMonthlySalary, 0);
});

  const totalHoursWorked = computed(() => {
    let totalSeconds = 0;
    if (reportData.value && reportData.value.length > 0) {
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
  
  function isWeekend(dayName){
  if(!reportData.value.userDetails.weekendChoice)
    return false;
  const weekendDays = reportData.value.userDetails.weekendChoice.split(',');
  const isDayOff = weekendDays.some(day => day.toLowerCase() === dayName.toLowerCase());
    return isDayOff
}


  async function fetchCompanies() {
    try {
      const response = await api.get(endpoints.companies.getActive);
      companyList.value = response.data;
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  }
  
  function getCompanyName(companyId) {
  const company = companyList.value.find(c => c.company_id === companyId);
  return company ? company.company_name : '';
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
  
  async function generateUserReport(userEmail) {
  try {
    reportType.value = 'user'; // Switch to "User Report"
    selectedUser.value = userEmail; // Select the clicked user
    
    // Generate the report with the current date range and company
    await generateReport(); 
  } catch (error) {
    console.error('Error generating user report:', error);
  }
  fetchUsers();
  selectedUser.value = userEmail; // Select the clicked user
}

  async function generateCompanyReport(companyName) {
  try {
    reportType.value = 'company'; // Switch to "Company Report"
    const company = companyList.value.find(c => c.company_name === companyName);
    if (company) {
      selectedCompany.value = company.company_id; // Select the clicked company

      // Generate the report with the current date range
      await generateReport(); 
    }
  } catch (error) {
    console.error('Error generating company report:', error);
  }
}

async function generateReport() {
  serverErrorMessage.value = null;
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
        } else if (reportType.value === 'overview') {
            endpoint = endpoints.reports.generateCompanyOverview; // Use the new endpoint
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
      serverErrorMessage.value = error.response.data.error ||'Network error or server unavailable'
      reportData.value = null;
      // Handle error, e.g., show an error message to the user
    }
  }
  
  function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  }
  
  onMounted(async () => {
    const thisYear = new Date().getFullYear();
    for (let i = thisYear - 5; i <= thisYear + 5; i++) {
      availableYears.value.push(i);
    }
    if (authStore.isNetAdmin){
      fetchCompanies();
    } 
    if (authStore.isEmployer || authStore.isNetAdmin) {
      selectedCompany.value = authStore.user.company_id;
      fetchUsers(); // Call fetchUsers here to populate the user list
    }
    generateReport()
  });
  
  const areReportFieldsFilled = computed(() => {
    if (reportType.value === 'user') {
      if (authStore.isEmployee){
        return dateRangeType.value ? true : false;
      }else{
        return selectedCompany.value && selectedUser.value && dateRangeType.value;
      }
    } else if (reportType.value === 'company') {
      return selectedCompany.value && dateRangeType.value;
    } else if (reportType.value === 'overview') {
      return dateRangeType.value;
    }
    return false;
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
    justify-content: center; 
    align-items: center; 
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 20px;
    margin-bottom: 20px; 
  }
  
  /*.filters > * {
    flex: 0 0 auto; /* Prevent items from growing to fill the space 
  }*/
  .report-type-select-container,
  .company-select-container,
  .user-select-container,
  .date-range-select-container {
    min-width: 150px; /* Set a minimum width for the containers */
    flex: 1 1 auto;   /* Allow the containers to grow and shrink */
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

  .v-table >>> tbody tr { /* Target all rows in the table */
    background-color: inherit; /* Reset background color to inherit */
  }
  
  .v-table >>> tbody tr :first-child { /* Target the first cell in each row */
    background-color: inherit; /* Reset background color to inherit */
  }
  
  .v-table >>> tbody tr.weekend { /* Target rows with the class 'weekend' */
    background-color: #d3d3d3; /* Set the background color for weekend rows */
  }

  .server-error { /* Style for the server error message */
    color: red;
    margin-top: 10px;
    text-align: center;
    width: 100%;
  }

</style>