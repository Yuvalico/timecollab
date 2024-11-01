<template>
  <table>
    <thead>
      <tr>
        <th v-for="header in headers" :key="header.value">{{ header.text }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in items" :key="index"  :style="{ backgroundColor: rowBgColor(item) }">
        <td v-for="header in headers" :key="header.value">
          <!-- Use default slot content if no slot is provided -->
          <slot :name="`item.${header.value}`" :item="item">
            {{ item[header.value] }}
          </slot>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
const props = defineProps({
  headers: Array,
  items: Array,
   rowBgColor: {
    type: Function, 
    default: function (){return "inherit";},
  }
});
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f2f2f2;
}
</style>
