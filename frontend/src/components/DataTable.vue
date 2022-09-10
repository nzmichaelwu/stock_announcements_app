<template>
  <v-app>
    <v-container fluid>
      <v-row>
        <v-col cols="3">
          <v-row class="pa-6">
            <v-text-field
              v-mode="name"
              append-icon="mdi-magnify"
              type="text"
              label="Name"
            ></v-text-field>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    <v-data-table
      :headers="headers"
      :items="announcements"
      item-key="name"
      :search="nameFilterValue"
      :sort-by="['market_cap']"
      :sort-desc="[true]"
      multi-sort
      :items-per-page="10"
      class="elevation-1"
    ></v-data-table>
  </v-app>
</template>


<script>
import axios from 'axios'
import { ref } from "vue";

export default {
  name: 'DataTable',
  
  data(){
    return {
      headers:[
        { text: "Ticker", value: 'ticker'},
        { text: "Name", value: 'name'},
        { text: "Price", value: 'price'},
        { text: "Market Cap", value: 'market_cap'},
        { text: "Announcement", value: 'announcement'},
        { text: "Price Sensitive", value: 'price_sensitive'},
        { text: "Announcement Time", value: 'announcement_time'},
      ],
      announcements: ref([])
    }
  },
  created(){
    axios
      .get('http://localhost:1234/')
      .then((response) => {
        // JSON responses are automatically parsed.
        this.announcements = response.data;
      })
      .catch((e) => {
        this.errors.push(e);
      });
  },
}
</script>