<script lang="ts" setup>
import { ref, onMounted, defineEmits } from 'vue';

// Declare emitted events
const emit = defineEmits(['userCreated']);

const showForm = ref(false);
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const mobile = ref<number | null>(null);
const password = ref<string>('');
const selectedCompany = ref('');
const role = ref('');
const permission = ref<number | null>(null);
const salary = ref<number | null>(null);
const workCapacity = ref<number | null>(null);
const companies = ref([]); // To hold the list of companies fetched from API

const permissions = ref(['Net Admin', 'Employer', 'Employee']);
const requiredRule = (value: string) => !!value || 'Required';
const emailRule = (value: string) => /.+@.+\..+/.test(value) || 'E-mail must be valid';

// Fetch companies from the API
async function fetchCompanies() {
  try {
    const response = await fetch('http://localhost:3000/api/companies');
    const data = await response.json();

    companies.value = data.map(company => company.company_name);
    
    console.log('Companies fetched:', companies.value);
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

onMounted(fetchCompanies);

// Submit handler
const submitForm = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/users/create-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName.value,
        last_name: lastName.value,
        email: email.value,
        mobile: mobile.value,
        password: password.value,
        company_name: selectedCompany.value,
        role: role.value,
        permission: permission.value,
        salary: salary.value,
        work_capacity: workCapacity.value,
      }),
    });

    if (response.ok) {
      console.log('User created successfully');
      emit('userCreated');  // Emit event on success
      showForm.value = false; // Close the modal on success
    } else {
      console.error('Failed to create user');
    }
  } catch (error) {
    console.error('Error submitting form:', error);
  }
};
</script>

<template>
  <!-- Button to open the form -->
  <VBtn @click="showForm = true" color="primary">
    + User
  </VBtn>

  <!-- Dialog/Modal for the form -->
  <VDialog v-model="showForm" persistent max-width="600px">
    <VCard>
      <VCardTitle>
        <span class="headline">Register a New User</span>
      </VCardTitle>

      <VCardText>
        <VForm @submit.prevent="submitForm">
          <VRow>
            <VCol cols="12">
              <VTextField
                v-model="firstName"
                prepend-inner-icon="ri-user-line"
                label="First Name"
                placeholder="John"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="lastName"
                prepend-inner-icon="ri-user-line"
                label="Last Name"
                placeholder="Doe"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="email"
                prepend-inner-icon="ri-mail-line"
                label="Email"
                type="email"
                placeholder="johndoe@example.com"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="mobile"
                prepend-inner-icon="ri-smartphone-line"
                label="Mobile"
                placeholder="+1 123 456 7890"
                type="number"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="password"
                prepend-inner-icon="ri-lock-line"
                label="Password"
                autocomplete="on"
                type="password"
                placeholder="············"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VAutocomplete
                v-model="selectedCompany"
                :items="companies"
                label="Company Name"
                item-text="company_name"
                item-value="company_id"
                prepend-inner-icon="ri-building-line"
                placeholder="Select or Search Company"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="role"
                prepend-inner-icon="ri-briefcase-line"
                label="Role"
                placeholder="Developer"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VSelect
                v-model="permission"
                :items="permissions"
                label="Permission"
                item-text="text"
                item-value="value"
                prepend-inner-icon="ri-shield-line"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="salary"
                prepend-inner-icon="ri-money-dollar-circle-line"
                label="Salary"
                type="number"
                placeholder="50000"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="workCapacity"
                prepend-inner-icon="ri-time-line"
                label="Work Capacity"
                type="number"
                placeholder="160"
              />
            </VCol>

            <VCol cols="12" class="d-flex justify-end">
              <VBtn
                color="secondary"
                type="reset"
                variant="outlined"
                @click="showForm = false"
                class="me-2"
              >
                Cancel
              </VBtn>

              <VBtn
                type="submit"
              >
                Submit
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>
