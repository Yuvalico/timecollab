<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'
import CompanyForm from '@/components/CompanyForm.vue'

// Refs to store users and companies
const users = ref([])
const companies = ref([])
const companiesWithAdmins = ref([])

// Headers for tables
const userHeaders = [
  { text: 'Name', value: 'fullName' },
  { text: 'Company Name', value: 'company_name' },
  { text: 'Role', value: 'role' },
  { text: 'Salary', value: 'salary' },
]

const companyHeaders = [
  { text: 'Company Name', value: 'companyName' },
  { text: 'Admin User', value: 'adminUser' },
]

// Fetch users from the API
async function fetchUsers() {
  try {
    const userResponse = await fetch('http://localhost:3000/api/users');
    users.value = (await userResponse.json()).map(user => ({
      ...user,
      fullName: `${user.first_name} ${user.last_name}`,
    }));

    console.log('Users fetched:', users.value);
  } catch (error) {
    console.error('Error fetching users:', error);
  }
}

// Fetch companies from the API
async function fetchCompanies() {
  try {
    const companyResponse = await fetch('http://localhost:3000/api/companies')
    companies.value = await companyResponse.json()

    // Map companies to include admin user
    companiesWithAdmins.value = companies.value.map(company => ({
      companyName: company.company_name,
      adminUser: getAdminUser(company.company_id),
    }));
  } catch (error) {
    console.error('Error fetching companies:', error)
  }
}

// Helper functions
function getAdminUser(companyID: string) {
  console.log('Looking for admin in companyID:', companyID);
  
  // Find the admin user with the matching companyID
  const adminUser = users.value.find(user => {
    return user.company_id === companyID && user.permission === 1;
  });

  console.log('Admin user found:', adminUser);
  return adminUser ? `${adminUser.first_name} ${adminUser.last_name}` : 'No Admin';
}

// Fetch data on component mount
onMounted(() => {
  fetchUsers();
  fetchCompanies();
})
</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>Users</span>
          <UserForm @userCreated="fetchUsers" />
        </VCardTitle>
        <SimpleTable :headers="userHeaders" :items="users" />
      </VCard>
    </VCol>
    
    <VCol cols="12" class="mt-4">
      <VCard >
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>Companies</span>
          <CompanyForm @companyCreated="fetchCompanies" />
        </VCardTitle>
        <SimpleTable :headers="companyHeaders" :items="companiesWithAdmins" />
      </VCard>
    </VCol>
  </VRow>
</template>
