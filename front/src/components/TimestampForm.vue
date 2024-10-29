<template>
    <VDialog v-model="showForm" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">{{ isEditing ? 'Edit Timestamp' : 'Add New Timestamp' }}</span>
        </VCardTitle>
        <VCardText>
          <VForm @submit.prevent="submitForm">
            <VCol cols="12">
              <VSelect
                v-model="reportingType"
                :items="reportingTypeOptions"
                label="Reporting Type"
                :rules="[requiredRule]"
              />
            </VCol>
            <VRow>
              <VCol v-if="reportingType === 'work'" cols="12">
                <VTextField
                  v-model="inTime"
                  label="In Time"
                  type="time"
                  :rules="[requiredRule]"
                />
              </VCol>
              <VCol v-if="reportingType === 'work'" cols="12">
                <VTextField
                  v-model="outTime"
                  label="Out Time"
                  type="time"
                  :rules="[requiredRule]"
                />
              </VCol>
              <VCol cols="12"> 
                <VTextField 
                  v-model="description" 
                  label="Description" 
                  placeholder="Add a description" 
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
                <VBtn type="submit">
                  {{ isEditing ? 'Update' : 'Submit' }}
                </VBtn>
              </VCol>
            </VRow>
          </VForm>
        </VCardText>
      </VCard>
    </VDialog>
  </template>
  
  <script setup>
  import { endpoints } from '@/utils/backendEndpoints';

  const api = inject('api');
  
  const emit = defineEmits(['timestampCreated', 'timestampUpdated']);
  const showForm = ref(false);
  const isEditing = ref(false);
  const entryId = ref(null); 
  const inTime = ref(null);
  const outTime = ref(null);
  const IsoInTime = ref(null);
  const IsoOutTime = ref(null);
  const description = ref(null);
  const reportingType = ref(null);
const reportingTypeOptions = ref([
  { value: 'work', title: 'Work' },
  { value: 'unpaidoff', title: 'Unpaid Day Off' },
  { value: 'paidoff', title: 'Paid Day Off' },
]);
  
  const props = defineProps({
    selectedUser: {  // Add a prop for the selected user
        type: String, 
        required: true, 
        },
    });

  const requiredRule = (value) => !!value || 'Required';
  
  function formatTime(dateObj) {
    if (!(dateObj instanceof Date)) {
        dateObj = new Date(dateObj); 
    }
    return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    }

    function updateIsoTime(timeInHHMM, fullIsoTime) {
    // Split the HH:MM time into hours and minutes
    const [hours, minutes] = timeInHHMM.split(':');
    const seconds = "00";
    // Parse the full ISO time string into a Date object
    const isoDate = new Date(fullIsoTime);

    // Update the hours and minutes of the Date object
    isoDate.setHours(hours);
    isoDate.setMinutes(minutes);
    isoDate.setSeconds(seconds);

    // Return the updated ISO time string
    return isoDate.toISOString();
}

  function openForm(timestamp  = null) {
    if (timestamp && timestamp.id) {
        console.log("reading timestamp")
        isEditing.value = true;
        entryId.value = timestamp.id;
        IsoInTime.value = timestamp.inTime;
        IsoOutTime.value = timestamp.inTime;
        inTime.value = timestamp.inTime ? formatTime(timestamp.inTime): null;
        outTime.value = timestamp.outTime ? formatTime(timestamp.outTime): null;
        description.value = timestamp.description;
        reportingType.value = timestamp.reporting_type; // Set reporting type from timestamp
    } else {
        isEditing.value = false;
        const day = timestamp.getDate(); 
        const month = timestamp.getMonth(); 
        const year = timestamp.getFullYear();
        console.log(day, month, year);
        IsoInTime.value = new Date(year, month, day,1,1,1);
        IsoOutTime.value = new Date(year, month, day,1,1,1);
        reportingType.value = null;

        resetForm();
    }
    showForm.value = true;
  }
  
  function resetForm() {
    inTime.value = null;
    outTime.value = null;
    description.value = null;
  }
  
  const submitForm = async () => {
    try {
        // Here you'll need to implement the logic to send the data to your backend
        // using your API (similar to the userForm.vue example)
        console.log('Submitting:', {
            entryId: entryId.value,
            inTime: inTime.value,
            outTime: outTime.value,
            description: description.value,
            isoin: IsoInTime.value,
            isoout: IsoOutTime.value,
            reporting_type: reportingType.value,
        });
        
        const method = isEditing.value ? 'put' : 'post';
        const url = isEditing.value
        ? `${endpoints.timestamps.edit}/${entryId.value}` 
        : endpoints.timestamps.create;

        const response = await api({
        method,
        url,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            punch_in_timestamp: reportingType.value === 'work' ? updateIsoTime(inTime.value, IsoInTime.value) : updateIsoTime('00:00', IsoInTime.value), // Set punch_in_timestamp to 00:00 if not 'work'
            punch_out_timestamp: reportingType.value === 'work' ? updateIsoTime(outTime.value, IsoOutTime.value) : updateIsoTime('00:00', IsoOutTime.value), // Set punch_out_timestamp to 00:00 if not 'work'
            detail: description.value,
            punch_type: 1,
            reporting_type: reportingType.value,
             
            ...( isEditing.value ? {} : {
                user_email: props.selectedUser, // Use selectedUser from props
                }),
            }
        });
  
        if (isEditing.value) {
            console.log('Timestamp updated successfully');
            emit('timestampUpdated'); 
        } else {
            console.log('Timestamp created successfully');
            emit('timestampCreated'); 
        }
        showForm.value = false; 
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };
  
  defineExpose({ openForm });
  </script>