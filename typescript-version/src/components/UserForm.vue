<template>
  <div>
    <VBtn @click="showForm = true" color="primary">
      + User
    </VBtn>

    <VDialog v-model="showForm" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">Register a New User</span>
        </VCardTitle>

        <VCardText>
          <VForm ref="form" v-model="valid" lazy-validation>
            <!-- First Name -->
            <VTextField
              v-model="firstName"
              label="First Name"
              :rules="[rules.required]"
              required
            ></VTextField>

            <!-- Last Name -->
            <VTextField
              v-model="lastName"
              label="Last Name"
              :rules="[rules.required]"
              required
            ></VTextField>

            <!-- Email -->
            <VTextField
              v-model="email"
              label="Email"
              type="email"
              :rules="[rules.required, rules.email]"
              required
            ></VTextField>

            <!-- Company Name (Dropdown) -->
            <VAutocomplete
              v-model="selectedCompany"
              :items="companies"
              label="Company Name"
              :rules="[rules.required]"
              item-text="company_name"
              item-value="company_id"
              required
            ></VAutocomplete>

            <!-- Role -->
            <VTextField
              v-model="role"
              label="Role"
              :rules="[rules.required]"
              required
            ></VTextField>

            <!-- Permission -->
            <VSelect
              v-model="permission"
              :items="permissions"
              label="Permission"
              :rules="[rules.required]"
              required
            ></VSelect>

            <!-- Password -->
            <VTextField
              v-model="password"
              label="Password"
              type="password"
              :rules="[rules.required]"
              required
            ></VTextField>

            <!-- Salary -->
            <VTextField
              v-model="salary"
              label="Salary"
              type="number"
              required
            ></VTextField>

            <!-- Work Capacity -->
            <VTextField
              v-model="workCapacity"
              label="Work Capacity"
              type="number"
              required
            ></VTextField>
          </VForm>
        </VCardText>

        <VCardActions>
          <VSpacer></VSpacer>
          <VBtn color="secondary" text @click="showForm = false">Cancel</VBtn>
          <VBtn color="primary" text @click="submitForm">Submit</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// Emit event setup
const emit = defineEmits(['userCreated']);

// State variables
const showForm = ref(false);
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const selectedCompany = ref('');
const role = ref('');
const permission = ref('');
const password = ref('');
const salary = ref<number | null>(null);
const workCapacity = ref<number | null>(null);
const valid = ref(false);
const companies = ref([]); // Holds companies fetched from the API

// Permission options
const permissions = [
  { text: 'Net Admin', value: 0 },
  { text: 'Employer', value: 1 },
  { text: 'Employee', value: 2 },
];

// Validation rules
const rules = {
  required: (value: string) => !!value || 'Required.',
  email: (value: string) => /.+@.+\..+/.test(value) || 'Email must be valid.',
};

// Fetch existing companies from the API
async function fetchCompanies() {
  try {
    const response = await fetch('http://localhost:3000/api/companies');
    companies.value = await response.json();
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

onMounted(fetchCompanies);

// Submit form handler
const submitForm = async () => {
  if (valid.value) {
    try {
      const response = await fetch('http://localhost:3000/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: firstName.value,
          last_name: lastName.value,
          email: email.value,
          company_id: selectedCompany.value,
          role: role.value,
          permission: permission.value,
          password: password.value,
          salary: salary.value,
          work_capacity: workCapacity.value,
        }),
      });

      if (response.ok) {
        emit('userCreated');  // Emit event on success
        showForm.value = false;  // Close the form dialog
      } else {
        console.error('Failed to create user');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  }
};
</script>

<style scoped>
.headline {
  font-weight: bold;
}
</style>
