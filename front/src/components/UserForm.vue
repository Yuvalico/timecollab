<script setup>
import { ref, onMounted, defineEmits, defineExpose } from 'vue';
import { endpoints } from '@/utils/backendEndpoints';

// Inject the Axios instance
const api = inject('api');

// Declare emitted events
const emit = defineEmits(['userCreated', 'userUpdated']);

const showForm = ref(false);
const isEditing = ref(false); // Flag to check if the form is in editing mode
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const mobile_phone = ref(null);
const password = ref('');
const selectedCompany = ref('');
const role = ref('');
const permission = ref(null);
const salary = ref(null);
const workCapacity = ref(null);
const companies = ref([]); // To hold the list of companies fetched from API

const permissions = ref(['Net Admin', 'Employer', 'Employee']);
const requiredRule = (value) => !!value || 'Required';
const emailRule = (value) => /.+@.+\..+/.test(value) || 'E-mail must be valid';

// Fetch companies from the API
async function fetchCompanies() {
  try {
    const response = await api.get(`${endpoints.companies.getActive}`);
    const data = await response.data;

    companies.value = data.map(company => company.company_name);
    
    console.log('Companies fetched:', companies.value);
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

onMounted(fetchCompanies);

// Method to open the form for editing a user
function openForm(user = null) {
  if (user) {
    isEditing.value = true;
    firstName.value = user.first_name;
    lastName.value = user.last_name;
    email.value = user.email;
    mobile_phone.value = user.mobile_phone;
    password.value = ''; // Password might not be provided directly, depending on your logic
    selectedCompany.value = user.company_name;
    role.value = user.role;
    permission.value = permissions.value[user.permission];
    salary.value = user.salary;
    workCapacity.value = user.work_capacity;
  } else {
    isEditing.value = false;
    resetForm();
  }
  showForm.value = true;
}

// Method to reset the form fields
function resetForm() {
  firstName.value = '';
  lastName.value = '';
  email.value = '';
  mobile_phone.value = null;
  password.value = '';
  selectedCompany.value = '';
  role.value = '';
  permission.value = null;
  salary.value = null;
  workCapacity.value = null;
}

// Submit handler
const submitForm = async () => {
  try {
    const method = isEditing.value ? 'put' : 'post';
    const url = isEditing.value
      ? `${endpoints.users.update}` 
      : endpoints.users.create;

    // Log data to be sent
    console.log({
      first_name: firstName.value,
      last_name: lastName.value,
      mobile_phone: mobile_phone.value,
      email: email.value,
      password: password.value, // Ensure password is sent when creating a user
      company_name: selectedCompany.value,
      role: role.value,
      permission: permission.value,
      salary: salary.value,
      work_capacity: workCapacity.value,
    });

    const response = await api({
      method,
      url,
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        first_name: firstName.value,
        last_name: lastName.value,
        mobile_phone: mobile_phone.value,
        email: email.value,
        password: password.value,
        company_name: selectedCompany.value,
        role: role.value,
        permission: {
          'Net Admin': 0,
          'Employer': 1,
          'Employee': 2
        }[permission.value],
        salary: salary.value,
        work_capacity: workCapacity.value,
      },
    });

    if ((response.status === 200) || (response.status === 201)) {
      if (isEditing.value) {
        console.log('User updated successfully');
        emit('userUpdated');  // Emit event on success
      } else {
        console.log('User created successfully');
        emit('userCreated');  // Emit event on success
      }
      showForm.value = false; // Close the modal on success
    } else {
      console.error('Failed to submit form');
      const errorData = await response.data;
      console.error('Error details:', errorData);
    }
  } catch (error) {
    console.error('Error submitting form:', error);
  }
};

defineExpose({
  openForm,
});
</script>

<template>
  <!-- Button to open the form -->
  <VBtn @click="openForm()" color="primary">
    + User
  </VBtn>

  <!-- Dialog/Modal for the form -->
  <VDialog v-model="showForm" persistent max-width="600px">
    <VCard>
      <VCardTitle>
        <span class="headline">{{ isEditing ? 'Edit User' : 'Register a New User' }}</span>
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
                v-model="mobile_phone"
                prepend-inner-icon="ri-smartphone-line"
                label="Mobile Phone"
                placeholder="+1 123 456 7890"
                type="number"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="email"
                prepend-inner-icon="ri-mail-line"
                label="Email"
                type="email"
                placeholder="johndoe@example.com"
                :rules="[requiredRule, emailRule]"
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
                :rules="isEditing ? [] : [requiredRule]"
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
                {{ isEditing ? 'Update' : 'Submit' }}
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>
