<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'

// Refs to store users and companies
const users = ref([])
const companies = ref([])

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

const companiesWithAdmins = ref([])

// Fetch data from the API
async function fetchData() {
  try {
    const [userResponse, companyResponse] = await Promise.all([
      fetch('http://localhost:3000/api/users'),
      fetch('http://localhost:3000/api/companies')
    ])

    users.value = (await userResponse.json()).map(user => ({
      ...user,
      fullName: `${user.first_name} ${user.last_name}`,
    }));    
    companies.value = await companyResponse.json()

    // Map companies to include admin user
    companiesWithAdmins.value = companies.value.map(company => ({
      companyName: company.company_name,
      adminUser: getAdminUser(company.companyID),
    }));

    console.log(users.value);
    console.log(companiesWithAdmins.value);
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

// Helper functions
function getCompanyName(companyID: string) {
  const company = companies.value.find(c => c.companyID === companyID)
  return company ? company.companyName : 'Unknown'
}

function getAdminUser(companyID: string) {
  const adminUser = users.value.find(user => user.companyID === companyID && user.role === 'admin')
  return adminUser ? `${adminUser.first_name} ${adminUser.last_name}` : 'No Admin'
}

// Fetch data on component mount
onMounted(fetchData)
</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard title="Users">
        <SimpleTable :headers="userHeaders" :items="users" />
      </VCard>
    </VCol>
    
    <VCol cols="12" class="mt-4">
      <VCard title="Companies">
        <SimpleTable :headers="companyHeaders" :items="companiesWithAdmins" />
      </VCard>
    </VCol>
  </VRow>
</template>
