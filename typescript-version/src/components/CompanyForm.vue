<script setup lang="ts">
import { ref, defineExpose } from 'vue';

const showForm = ref(false);
const companyName = ref('');
const valid = ref(false);
const isEditing = ref(false);
let editingCompanyId = null;

const rules = {
  required: (value: string) => !!value || 'Required.',
};

const emit = defineEmits(['companyCreated', 'companyUpdated']);

const openForm = (company = null) => {
  if (company) {
    // Editing mode: pre-fill the form with the company data
    companyName.value = company.company_name; 
    isEditing.value = true;
    editingCompanyId = company.company_id;
  } else {
    // Creating mode
    companyName.value = '';
    isEditing.value = false;
    editingCompanyId = null;
  }
  showForm.value = true;
};

const closeForm = () => {
  showForm.value = false;
};

const submitForm = async () => {
  if (valid.value) {
    try {
      const url = isEditing.value
        ? `http://localhost:3000/api/companies/update-company/${editingCompanyId}`
        : 'http://localhost:3000/api/companies/create-company';
      
      const method = isEditing.value ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_name: companyName.value }),
      });

      if (response.ok) {
        if (isEditing.value) {
          emit('companyUpdated');
        } else {
          emit('companyCreated');
        }
        closeForm();
      } else {
        console.error('Failed to submit company form');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  }
};

defineExpose({
  openForm,
});
</script>

<template>
  <div>
    <VBtn @click="openForm()" color="primary">
      + Company
    </VBtn>

    <VDialog v-model="showForm" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">{{ isEditing ? 'Edit Company' : 'Register a New Company' }}</span>
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
          <VBtn color="secondary" text @click="closeForm">Cancel</VBtn>
          <VBtn color="primary" text @click="submitForm">Submit</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </div>
</template>

<style scoped>
.headline {
  font-weight: bold;
}
</style>
