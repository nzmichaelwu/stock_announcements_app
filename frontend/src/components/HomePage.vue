<template>
  <v-main>
    <v-container fluid>
      <div class="homepage-button-box">
        <router-link tag="button" to="/contents">
          <h2>
            Contents
          </h2>
        </router-link>
      </div>
    </v-container>
  </v-main>
</template>

<script>
  export default {}
</script>

<style scoped>
  .homepage-button-box {
    position: fixed;
    top:20%;
    left: 40%;
    right: 40%;
    width: 7%;
    margin: auto;
    color: #1E90FF;
    background: #ffff;
    box-shadow: 0px 0px 9px -2px #000;
  }
</style>