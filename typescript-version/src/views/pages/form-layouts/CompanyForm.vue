<script lang="ts" setup>
import { ref } from 'vue';

const firstName = ref('');
const email = ref('');
const mobile = ref<number>();
const password = ref<string>();
const checkbox = ref(false);
const companyName = ref('');  // New field for company name

const submitForm = async () => {
  // Handle form submission
  try {
    const response = await fetch('http://localhost:3000/api/companies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: companyName.value,
        // Include additional user-related fields if needed
      }),
    });

    if (response.ok) {
      console.log('Company registered successfully');
      // Reset the form or redirect as needed
    } else {
      console.error('Failed to register company');
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
</script>

<template>
  <VForm @submit.prevent="submitForm">
    <VRow>
      <!-- First Name -->
      <VCol cols="12">
        <VTextField
          v-model="firstName"
          prepend-inner-icon="ri-user-line"
          label="First Name"
          placeholder="John"
        />
      </VCol>

      <!-- Email -->
      <VCol cols="12">
        <VTextField
          v-model="email"
          prepend-inner-icon="ri-mail-line"
          label="Email"
          type="email"
          placeholder="johndoe@example.com"
        />
      </VCol>

      <!-- Mobile -->
      <VCol cols="12">
        <VTextField
          v-model="mobile"
          prepend-inner-icon="ri-smartphone-line"
          label="Mobile"
          placeholder="+1 123 456 7890"
          type="number"
        />
      </VCol>

      <!-- Password -->
      <VCol cols="12">
        <VTextField
          v-model="password"
          prepend-inner-icon="ri-lock-line"
          label="Password"
          autocomplete="on"
          type="password"
          placeholder="············"
        />
      </VCol>

      <!-- Company Name -->
      <VCol cols="12">
        <VTextField
          v-model="companyName"
          prepend-inner-icon="ri-building-line"
          label="Company Name"
          placeholder="Your Company Name"
        />
      </VCol>

      <!-- Remember Me -->
      <VCol cols="12">
        <VCheckbox
          v-model="checkbox"
          label="Remember me"
        />
      </VCol>

      <!-- Submit and Reset Buttons -->
      <VCol cols="12">
        <VBtn
          type="submit"
          class="me-2"
        >
          Submit
        </VBtn>

        <VBtn
          color="secondary"
          type="reset"
          variant="outlined"
        >
          Reset
        </VBtn>
      </VCol>
    </VRow>
  </VForm>
</template>
