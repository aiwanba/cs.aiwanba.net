<template>
  <div id="app">
    <h1>Stock Trading Game</h1>
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: "Welcome to the Stock Trading Game!"
    };
  }
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 50px;
}
</style> 