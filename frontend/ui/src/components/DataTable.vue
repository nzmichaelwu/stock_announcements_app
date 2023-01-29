<template>
  <v-app>
    <div v-show="announcements.length==0">
      <div class="announcement-loading-box">
        <grid-loader :loading="loading" :color="color" :size="size"></grid-loader>
      </div>
    </div>
    <v-container fluid>
      <v-row>
        <v-col cols="3">
          <v-row class="pa-6">
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              type="text"
              label="Search"
            ></v-text-field>
          </v-row>
        </v-col>
        <v-col offset-md="3" style="padding-top: 30px">
          <v-row class="pa-6">
            <label for="" style="padding-right: 10px">From:</label>
            <input type="datetime-local" v-model="startDate" style="padding-right: 10px">
            <label for="" style="padding-left: 20px; padding-right: 10px">To:</label>
            <input type="datetime-local" v-model="endDate">
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    <v-data-table
      :headers="headers"
      :items="filteredAnnouncements"
      :search="search"
      :items-per-page="10"
      class="elevation-1"
      v-show="announcements.length!=0"
    > 
      <template v-slot:[`item.market_cap`]="{ item }">
          {{ formatNumber(item.market_cap) }}
      </template>
      <template v-slot:[`header.market_cap`]="{ header }">
        {{ header.text }}
        <v-menu offset-y :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon small :color="marketCapFilter ? 'primary' : ''">
                mdi-filter
              </v-icon>
            </v-btn>
          </template>
          <div style="background-color: white; width: 280px">
            <v-select
              v-model="marketCapFilter"
              label="Select"
              :items="['0 to 1B', '1B to 20B', '20B+']"
            ></v-select>
            <v-btn
              @click="marketCapFilter = ''"
              small
              text
              color="primary"
              class="ml-2 mb-2"
            >Clean</v-btn>
          </div>
        </v-menu>
      </template>
      <template v-slot:[`header.price_sensitive`]="{ header }">
        {{ header.text }}
        <v-menu offset-y :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon small :color="priceSensitive ? 'primary' : ''">
                mdi-filter
              </v-icon>
            </v-btn>
          </template>
          <div style="background-color: white; width: 280px">
            <v-select
              v-model="priceSensitive"
              label="Select"
              :items="['PRICE SENSITIVE', 'NOT PRICE SENSITIVE']"
            ></v-select>
            <v-btn
              @click="priceSensitive = ''"
              small
              text
              color="primary"
              class="ml-2 mb-2"
            >Clean</v-btn>
          </div>
        </v-menu>
      </template>
    </v-data-table>
    <!-- <v-container>
      Value: {{market_cap}}
    </v-container> -->
  </v-app>
</template>


<script>
import axios from '../axios/axios'
import GridLoader from 'vue-spinner/src/GridLoader.vue'

export default {
  data(){
    return {
      search: '',
      marketCapFilter: null,
      priceSensitive: null,
      startDate: null,
      endDate: null,
      headers: [
        { text: "Ticker", value: 'ticker'},
        { text: "Name", value: 'name'},
        { text: "Price", value: 'price'},
        { text: "Market Cap", value:'market_cap'},
        { text: "Announcement", value: 'announcement'},
        { text: "Price Sensitive", value: 'price_sensitive'},
        { text: "Announcement Time", value: 'announcement_time'},
      ],
      announcements: [],
      color: 'rgb(93, 197, 150)',
      size: '45px',
      margin: '2px',
      radius: '2px'
    }
  },
  components: {
    GridLoader
  },
  created(){
    axios
      .get('/api/contents')
      .then(response => (
        this.full_data = response.data.items,
        this.announcements = this.full_data
        // console.log(response.data.items)
      ))
  },
  computed: {
    filteredAnnouncements() {
      
      const conditions = [];

      if (this.priceSensitive) {
        conditions.push(this.filterPriceSensitive);
      }

      if (this.marketCapFilter) {
        conditions.push(this.filterMarketCap);
      }

      if (this.startDate || this.endDate) {
        conditions.push(this.filterAnnouncementTime);
      }

      if (conditions.length > 0){
        return this.announcements.filter((announcement) => {
          return conditions.every((condition) => {
            return condition(announcement)
          })
        })
      }
      // console.log(this.announcements)
      return this.announcements
    }
  },
  methods: {
    formatDate(date){
      if (!date) return date
      const date_mod = date.replace("T", " ")
      return date_mod
    },
    formatNumber(value){
      var shortValue = new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'AUD',
        notation: 'compact',
      }).format(value)
      return shortValue
    },
    filterAnnouncementTime(item) {
      let startDate = this.formatDate(this.startDate);
      let endDate = this.formatDate(this.endDate);
      
      const annnouncementDate = item.announcement_time
      // console.log(annnouncementDate)
      // console.log(startDate)
      if (startDate && endDate) {
        return annnouncementDate >= startDate && annnouncementDate <= endDate;
      }
      if (startDate && !endDate) {
        return annnouncementDate >= startDate;
      }
      if (!startDate && endDate) {
        return annnouncementDate <= endDate;
      }
    },
    filterPriceSensitive(item) {
      return item.price_sensitive == this.priceSensitive
    },
    filterMarketCap(item){
      const market_cap_range = this.marketCapFilter
      if (market_cap_range == '0 to 1B') {
        return item.market_cap >= 0 && item.market_cap < 1000000000;
      }
      if (market_cap_range == '1B to 20B') {
        return item.market_cap >= 1000000000 && item.market_cap < 20000000000;
      }
      if (market_cap_range == '20B+') {
        return item.market_cap >= 20000000000
      }
    }
  }
}
</script>

<style scoped>
  .announcement-loading-box {
    position: fixed;
    top:40%;
    left: 40%;
    right: 40%;
    width: 10%;
    margin: auto;
    /* background: #ffff; */
    /* box-shadow: 0px 0px 9px -2px #000; */
  }
</style>