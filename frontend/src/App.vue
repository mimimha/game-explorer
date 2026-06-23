<template>
  <div>
    <nav class="nav">
    
    <RouterLink :to="{ name: 'home' }" class="link">홈</RouterLink>|
    <RouterLink :to="{ name: 'home' }" class="link">탐험 지도</RouterLink>|
    <RouterLink :to="{ name: 'home' }" class="link">탐험대 광장</RouterLink>
    <form @submit.prevent="onSearch">
    <input v-model="keyword" type="text" />
    <button type="submit">검색</button>
    </form>


    </nav>
  </div>

  <RouterView />
</template>

<script setup>
import { ref } from 'vue';

const keyword = ref('')

const onSearch = () => {
  console.log(keyword.value)
}

</script>

<style scoped>
.nav {
  background-color: rgb(166, 208, 255);
  padding: 16px;
}

</style>