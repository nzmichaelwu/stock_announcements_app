<template>
  <v-app>
    <v-app-bar
      app
      color="blue darken-1"
      dark
    >
      <div class="d-flex align-center">
        <h1>
          ASX Stock Announcements & News App
        </h1>
      </div>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
  export default {
    name: 'App',
  };
</script>
