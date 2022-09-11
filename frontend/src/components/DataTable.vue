<template>
  <v-app>
    <v-data-table
      :headers="headers"
      :items="items"
      :items-per-page="10"
      class="elevation-1"
    ></v-data-table>
  </v-app>
</template>


<script>
import axios from 'axios'

export default {
  data(){
    return {
      headers: [
        { text: "Ticker", value: 'ticker'},
        { text: "Name", value: 'name'},
        { text: "Price", value: 'price'},
        { text: "Market Cap", value: 'market_cap'},
        { text: "Announcement", value: 'announcement'},
        { text: "Price Sensitive", value: 'price_sensitive'},
        { text: "Announcement Time", value: 'announcement_time'},
      ],
      items: []
    }
  },
  created(){
    axios
      .get('http://localhost:1234/')
      .then(response => (
        this.items = response.data.items,
        console.log(response.data.items)
      ))
        // 
  },
  // computed:{
  //   filteredRows() {
  //     return this.items.filter(item => {
  //       const name = item.name.toLowerCase();
  //       const searchTerm = this.filter.toLowerCase();

  //       return name.includes(searchTerm)
  //     });
  //   }
  // }
}
</script>