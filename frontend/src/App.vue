<template>
  <router-view />
</template>

<script setup>
// Sử dụng Vue Router để quản lý các trang
</script>

<style>
/* Thiết lập lại kiểu dáng toàn cục */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

/* Kiểu dáng thanh cuộn */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* Kiểu dáng nút toàn cục */
button {
  font-family: inherit;
}
</style>
