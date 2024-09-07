<template>
  <div>
    <VBtn @click="showForm = true" color="primary">
      + Company
    </VBtn>

    <VDialog v-model="showForm" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">Register a New Company</span>
        </VCardTitle>

        <VCardText>
          <VForm ref="form" v-model="valid" lazy-validation>
            <VTextField
              v-model="companyName"
              label="Company Name"
              :rules="[rules.required]"
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
import { ref } from 'vue';

const showForm = ref(false);
const companyName = ref('');
const valid = ref(false);

const rules = {
  required: (value: string) => !!value || 'Required.',
};

const emit = defineEmits(['companyCreated']);

const submitForm = async () => {
  if (valid.value) {
    try {
      const response = await fetch('http://localhost:3000/api/companies/create-company', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_name: companyName.value }),
      });

      if (response.ok) {
        emit('companyCreated');  // Emit event on success
        showForm.value = false;
      } else {
        console.error('Failed to create company');
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
