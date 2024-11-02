<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import SimpleTable from '@/views/pages/tables/SimpleTable.vue';
import UserForm from '@/components/UserForm.vue';
import CompanyForm from '@/components/CompanyForm.vue';
import { endpoints } from '@/utils/backendEndpoints';

// Inject the Axios instance
const api = inject('api');

const router = useRouter();
const authStore = useAuthStore();
console.log(authStore);


// if (!authStore.isNetAdmin) {
//   router.push('/dashboard'); // Redirect non-admin users to the dashboard
// }

// Refs to store users and companies
const users = ref([]);
const companies = ref([]);
const companiesWithAdmins = ref([]);
const selectedCompany = ref("Filter Users by Company"); // To store the selected company name
const showRemoveUserDialog = ref(false);
const userToRemove = ref(null);
const employmentEndDate = ref(new Date()); 
const today = new Date().toISOString().slice(0, 10); 


// Headers for tables
const userHeaders = computed(() => {
  const headers  = [
    { text: 'Name', value: 'fullName' },
    { text: 'Mobile Phone', value: 'mobile_phone' },
    { text: 'Email', value: 'email' },
    { text: 'Company Name', value: 'company_name' },
    { text: 'Role', value: 'role' },
    { text: 'Salary', value: 'salary' },
    { text: 'Work Capacity', value: 'work_capacity' },
    { text: 'Employment Start', value: 'employment_start' },
    { text: 'Weekend Choice', value: 'weekend_choice' },
    { text: 'Permission', value: 'permission' },
    // { text: '', value: 'actions', align: 'center', sortable: false },
  ];
  if (authStore.isNetAdmin) {
      headers.push({ text: '', value: 'actions', align: 'center', sortable: false });
    }
    return headers;
});

const companyHeaders = [
  { text: 'Company Name', value: 'companyName' },
  { text: 'Admin User', value: 'adminUser' },
  { text: '', value: 'actions', align: 'center', sortable: false },
];

// Computed property for company filtering options
const companyOptions = computed(() => {
  return ['No Filter'].concat(companies.value.map(company => company.company_name));
});

// Computed property to filter users by company
const filteredUsers = computed(() => {
  console.log("Filtering users by company:", selectedCompany.value);
  if (authStore.isNetAdmin && selectedCompany.value !== "Filter Users by Company" && selectedCompany.value !== "No Filter") { // Check if a company is actually selected
    return users.value.filter(user => user.company_name === selectedCompany.value);
  } else {
    return users.value; 
  }
});

// function to filter users when a company is selected
const filterUsersByCompany = () => {
  // This will automatically trigger the 'filteredUsers' computed property
};

// Watch for changes in users.value and log them
watch(() => users.value, (newUsers) => {
  console.log('users.value changed:', newUsers);
});

// Fetch users from the API
async function fetchUsers() {
  try {
    const userResponse = await api.get(`${endpoints.users.getActive}`);
    console.log(userResponse.data)
    users.value = (await userResponse.data).map(user => ({
      ...user,
      fullName: `${user.first_name} ${user.last_name}`,
      actions: {
        edit: () => editUser(user),
        remove: () => removeUser(user),
      },
    }));

    console.log('Users fetched:', users.value);
  } catch (error) {
    console.error('Error fetching users:', error);
  }
}

// Fetch companies from the API
async function fetchCompanies() {
  try {
    const companyResponse =  await api.get(`${endpoints.companies.getActive}`); 
    companies.value = (await companyResponse.data).map(company => ({
      ...company,
      companyName: company.company_name,
      actions: {
        edit: () => editCompany(company),
        remove: () => removeCompany(company),
      },
    }));

    // Map companies to include admin user
    companiesWithAdmins.value = companies.value.map(company => ({
      companyName: company.company_name,
      adminUser: getAdminUser(company.company_id),
      actions: company.actions,
    }));
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

// Helper functions
function getAdminUser(companyID) {
  console.log('Looking for admin in companyID:', companyID);
  
  // Find the admin user with the matching companyID
  const adminUser = users.value.find(user => {
    return user.company_id === companyID && user.permission === 1;
  });

  console.log('Admin user found:', adminUser);
  return adminUser ? `${adminUser.first_name} ${adminUser.last_name}` : 'No Admin';
}

function editUser(user) {
  console.log("Editing user: ", user);
  // Use ref function to open the form with pre-filled data
  userFormRef.value.openForm(user);
  // Refresh the users list after editing
  fetchUsers();
}

const userFormRef = ref(null); // Ref for the UserForm component

// const removeUser = async (user) => {
//   try {
//     const response = await api.put(`${endpoints.users.remove}/${user.email}`);

//     if (response.status === 200) {
//       console.log('User removed successfully');
//       // Refresh the users list after removal
//       fetchUsers();
//     } else {
//       console.error('Failed to remove user');
//     }
//   } catch (error) {
//     console.error('Error removing user:', error);
//   }
// };
const removeUser = (user) => {
  userToRemove.value = user;
  showRemoveUserDialog.value = true;
};

const cancelRemoveUser = () => {
  showRemoveUserDialog.value = false;
  userToRemove.value = null;
  employmentEndDate.value = new Date(); // Reset the date picker to today
};

const confirmRemoveUser = async () => {
  try {
    const user = userToRemove.value;
    user.employment_end = employmentEndDate.value ? employmentEndDate.value.toISOString() : new Date().toISOString();

    const response = await api.put(`${endpoints.users.remove}/${user.email}`, user);

    if (response.status === 200) {
      console.log('User removed successfully');
      fetchUsers();
    } else {
      console.error('Failed to remove user');
    }
  } catch (error) {
    console.error('Error removing user:', error);
  } finally {
    showRemoveUserDialog.value = false;
    userToRemove.value = null;
    employmentEndDate.value = new Date();
    fetchUsers();
  }
};

function editCompany(company) {
  console.log("Editing company: ", company);
  companyFormRef.value.openForm(company);
  // Refresh the companies list after editing
  fetchCompanies();
}


function formatWeekendChoice(weekendChoice) {
  if (weekendChoice) {
    return weekendChoice.split(',').join(', '); // Add a space after each comma
  }
  return '';
}

function formatDate(dateString) {
  if (dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  }
  return '';
}

const companyFormRef = ref(null); // Ref for the CompanyForm component

const removeCompany = async (company) => {
  try {
    const response = await api.put(`${endpoints.companies.remove}/${company.company_id}`);

    if (response.status === 200) {
      console.log('Company removed successfully');
      // Refresh the companies list after removal
      fetchCompanies();
    } else {
      console.error('Failed to remove company');
    }
  } catch (error) {
    console.error('Error removing company:', error);
  }
};

// Fetch data on component mount
onMounted(() => {
  fetchUsers();
  if (authStore.isNetAdmin){
    fetchCompanies();
  }
});
</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>
            <span v-if="authStore.isEmployer">
              {{ authStore.user.company_name }} - 
            </span>
            <span>Users</span>
          </span>

          <div v-if="authStore.isNetAdmin" class="d-flex align-center"> 
            <VSelect
              v-model="selectedCompany"
              :items="companyOptions"
              label="Select Company"
              @change="filterUsersByCompany"
              class="mr-4" 
            />
          </div>

          <UserForm v-if="authStore.isNetAdmin" ref="userFormRef" @userCreated="fetchUsers" @userUpdated="fetchUsers" />
        </VCardTitle>

        <SimpleTable :headers="userHeaders" :items="filteredUsers">
          <template v-slot:item.actions="{ item }">
            <div class="actions-col" v-if="authStore.isNetAdmin">
              <IconBtn
                icon="ri-edit-line"
                @click="item.actions.edit"
              />
              <IconBtn
                icon="ri-delete-bin-line"
                @click="item.actions.remove"
              />
            </div>
          </template>
          <template v-slot:item.employment_start="{ item }">
            {{ formatDate(item.employment_start) }} 
          </template>
          <template v-slot:item.weekend_choice="{ item }">
            {{ formatWeekendChoice(item.weekend_choice) }} 
          </template>
        </SimpleTable>
      </VCard>
    </VCol>

    <VCol cols="12" class="mt-4" v-if="authStore.isNetAdmin"> 
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>Companies</span>
          <CompanyForm ref="companyFormRef" @companyCreated="fetchCompanies" @companyUpdated="fetchCompanies" />
        </VCardTitle>
        <SimpleTable :headers="companyHeaders" :items="companiesWithAdmins">
          <template v-slot:item.actions="{ item }">
            <div class="actions-col">
              <IconBtn
                icon="ri-edit-line"
                @click="item.actions.edit"
              />
              <IconBtn
                icon="ri-delete-bin-line"
                @click="item.actions.remove"
              />
            </div>
          </template>
          
        </SimpleTable>
      </VCard>
    </VCol>
    <VDialog v-model="showRemoveUserDialog" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">Remove User</span>
        </VCardTitle>
        <VCardText>
          <div>
            <p v-if="userToRemove">Are you sure you want to remove <strong>{{ userToRemove.first_name }} {{userToRemove.first_name}}</strong>?</p> 
            <VDatePicker v-model="employmentEndDate" :value="today" /> 
          </div>
        </VCardText>
        <VCardActions>
          <VBtn color="secondary" variant="outlined" @click="cancelRemoveUser">Cancel</VBtn>
          <VBtn color="error" @click="confirmRemoveUser">Remove</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </VRow>
</template>
