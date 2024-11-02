<script setup>
import { useAuthStore } from '@/store/auth';
import VerticalNavSectionTitle from '@/@layouts/components/VerticalNavSectionTitle.vue'
import VerticalNavGroup from '@layouts/components/VerticalNavGroup.vue'
const authStore = useAuthStore();
import VerticalNavLink from '@layouts/components/VerticalNavLink.vue'
</script>

<template>

  <!-- Time Tracking -->
  <VerticalNavSectionTitle
  :item="{
    heading: 'Time Tracking',
  }"
/>
  <VerticalNavLink
    v-if="authStore.isEmployer || authStore.isNetAdmin"
    :item="{
      title: 'Management',
      icon: 'ri-team-line',
      to: '/management',
    }"
    />
  <VerticalNavLink
    :item="{
      title: 'TimeWatch',
      icon: 'ri-calendar-schedule-line',
      to: '/timewatch',
    }"
    />
  <VerticalNavLink
    :item="{
      title: 'Reports',
      icon: 'ri-file-chart-line',
      to: '/reports',
    }"
    />

  <!-- Profile -->
  <VerticalNavSectionTitle
    :item="{
      heading: 'Profile',
    }"
  />

  <VerticalNavLink
    :item="{
      title: 'Account Settings',
      icon: 'ri-user-settings-line',
      to: '/account-settings',
    }"
  />


</template>
