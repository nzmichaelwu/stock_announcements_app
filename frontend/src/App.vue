<template>
  <v-app>
    <v-app-bar
      app
      color="blue darken-1"
      dark
    >
      <div class="d-flex align-center">
        <h1>
          ASX Stock Announcements
        </h1>
        <!-- <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        /> -->
      </div>

      <v-spacer></v-spacer>
      
    </v-app-bar>

    <v-main>
      <DataTable/>
    </v-main>
  </v-app>
</template>

<script>
import DataTable from './components/DataTable';

export default {
  name: 'App',
  components: {
    DataTable,
  },

  data: () => ({
    //
  }),
};
</script>
