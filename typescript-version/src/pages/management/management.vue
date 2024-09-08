<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'
import UserForm from '@/components/UserForm.vue';
import CompanyForm from '@/components/CompanyForm.vue'

// Refs to store users and companies
const users = ref([])
const companies = ref([])
const companiesWithAdmins = ref([])

// Headers for tables
const userHeaders = [
  { text: 'Name', value: 'fullName' },
  { text: 'Mobile Phone', value: 'mobile_phone' },
  { text: 'Email', value: 'email' },
  { text: 'Company Name', value: 'company_name' },
  { text: 'Role', value: 'role' },
  { text: 'Salary', value: 'salary' },
  { text: 'Work Capacity', value: 'work_capacity' },
  { text: '', value: 'actions', align: 'center', sortable: false },
]

const companyHeaders = [
  { text: 'Company Name', value: 'companyName' },
  { text: 'Admin User', value: 'adminUser' },
  { text: '', value: 'actions', align: 'center', sortable: false },
]

// Fetch users from the API
async function fetchUsers() {
  try {
    const userResponse = await fetch('http://localhost:3000/api/users/active');
    users.value = (await userResponse.json()).map(user => ({
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
    const companyResponse = await fetch('http://localhost:3000/api/companies/active');
    companies.value = (await companyResponse.json()).map(company => ({
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
function getAdminUser(companyID: string) {
  console.log('Looking for admin in companyID:', companyID);
  
  // Find the admin user with the matching companyID
  const adminUser = users.value.find(user => {
    return user.company_id === companyID && user.permission === 1;
  });

  console.log('Admin user found:', adminUser);
  return adminUser ? `${adminUser.first_name} ${adminUser.last_name}` : 'No Admin';
}

function editUser(user) {
  console.log("editing user: ", user);
  // Use ref method to open the form with pre-filled data
  userFormRef.value.openForm(user);
  // Refresh the users list after editing
  fetchUsers();
}

const userFormRef = ref(null); // Ref for the UserForm component

const removeUser = async (user) => {
  try {
    const response = await fetch(`http://localhost:3000/api/users/remove-user/${user.id}`, {
      method: 'PUT',
    });

    if (response.ok) {
      console.log('User removed successfully');
      // Refresh the users list after removal
      fetchUsers();
    } else {
      console.error('Failed to remove user');
    }
  } catch (error) {
    console.error('Error removing user:', error);
  }
};

function editCompany(company) {
  console.log("Editing company: ", company);
  companyFormRef.value.openForm(company);
  // Refresh the companies list after editing
  fetchCompanies();
}

const companyFormRef = ref(null); // Ref for the CompanyForm component

const removeCompany = async (company) => {
  try {
    const response = await fetch(`http://localhost:3000/api/companies/remove-company/${company.company_id}`, {
      method: 'PUT',
    });

    if (response.ok) {
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
  fetchCompanies();
})
</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>Users</span>
          <UserForm ref="userFormRef" @userCreated="fetchUsers" @userUpdated="fetchUsers" />
        </VCardTitle>
        <SimpleTable :headers="userHeaders" :items="users">
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

    <VCol cols="12" class="mt-4">
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
  </VRow>
</template>
