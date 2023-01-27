<template>
  <v-app>
    <div v-show="afr_homepage.length==0">
      <div class="news-loading-box">
        <grid-loader :loading="loading" :color="color" :size="size"></grid-loader>
      </div>
    </div>
    <v-row>
      <v-col cols="4">
        <v-container fluid>
          <v-row>
            <v-text-field
              v-model="afr_homepage_search"
              append-icon="mdi-magnify"
              type="text"
              label="Search"
            ></v-text-field>
          </v-row>
          <div>
            <h3>
              AFR Homepage
            </h3>
          </div>
          <v-data-table
            :headers="afr_homepage_headers"
            :items="afr_homepage"
            :search="afr_homepage_search"
            :items-per-page="5"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            v-show="afr_homepage.length!=0"
          >
          </v-data-table>
        </v-container>
      </v-col>
      <v-col cols="8">
        <v-container fluid>
          <v-row>
            <v-text-field
              v-model="afr_street_talk_search"
              append-icon="mdi-magnify"
              type="text"
              label="Search"
            ></v-text-field>
          </v-row>
          <div>
            <h3>
              AFR Street Talk
            </h3>
          </div>
          <v-data-table
            :headers="afr_street_talk_headers"
            :items="afr_street_talk"
            :search="afr_street_talk_search"
            :items-per-page="5"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            v-show="afr_street_talk.length!=0"
          >
          </v-data-table>
        </v-container>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="5">
        <v-container fluid>
          <v-row>
            <v-text-field
              v-model="aus_homepage_search"
              append-icon="mdi-magnify"
              type="text"
              label="Search"
            ></v-text-field>
          </v-row>
          <div>
            <h3>
              The Australian Homepage
            </h3>
          </div>
          <v-data-table
            :headers="aus_homepage_headers"
            :items="filteredAusHomepage"
            :search="aus_homepage_search"
            :items-per-page="5"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            v-show="filteredAusHomepage.length!=0"
          >
          <template v-slot:[`header.category`]="{ header }">
              {{ header.text }}
              <v-menu offset-y :close-on-content-click="false">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn icon v-bind="attrs" v-on="on">
                    <v-icon small :color="categorySelect ? 'primary' : ''">
                      mdi-filter
                    </v-icon>
                  </v-btn>
                </template>
                <div style="background-color: white; width: 280px">
                  <v-select
                    v-model="categorySelect"
                    label="Select"
                    :items="CategoryList"
                  ></v-select>
                  <v-btn
                    @click="categorySelect = ''"
                    small
                    text
                    color="primary"
                    class="ml-2 mb-2"
                  >Clean</v-btn>
                </div>
              </v-menu>
            </template>
          </v-data-table>
        </v-container>
      </v-col>
      <v-col cols="7">
        <v-container fluid>
          <v-row>
            <v-text-field
              v-model="aus_sections_search"
              append-icon="mdi-magnify"
              type="text"
              label="Search"
            ></v-text-field>
          </v-row>
          <div>
            <h3>
              The Australian Sections (Dataroom & Trading Day)
            </h3>
          </div>
          <v-data-table
            :headers="aus_sections_headers"
            :items="aus_sections"
            :search="aus_sections_search"
            :items-per-page="5"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            v-show="aus_sections.length!=0"
          >
          </v-data-table>
        </v-container>
      </v-col>
    </v-row>
  </v-app>
</template>

<script>
  import axios from '../axios/axios'
  import GridLoader from 'vue-spinner/src/GridLoader.vue'

  export default {
    data(){
      return {
        afr_homepage_search: '',
        afr_street_talk_search: '',
        aus_homepage_search: '',
        aus_sections_search:'',
        categorySelect: null,
        afr_homepage_headers: [
          { text: "Headlines", value: 'headline' }, 
          { text: "Extract Time", value: 'date_time'},
        ],
        afr_homepage: [],
        afr_street_talk_headers: [
          { text: "Headlines", value: 'headline' },
          { text: "Summary", value: 'summary' },
          { text: "Extract Time", value: 'date_time'},
        ],
        afr_street_talk: [],
        aus_homepage_headers: [
          { text: "Category", value: 'category' },
          { text: "Headlines", value: 'headline' },
          { text: "Extract Time", value: 'date_time'},
        ],
        aus_homepage: [],
        aus_sections_headers: [
          { text: "Category", value: 'category' },
          { text: "Headlines", value: 'headline' },
          { text: "Summary", value: 'summary' },
          { text: "Extract Time", value: 'date_time'},
        ],
        aus_sections: [],
        color: 'rgb(93, 197, 150)',
        size: '45px',
        margin: '2px',
        radius: '2px',
        sortBy: 'date_time',
        sortDesc: true, 
      }
    },
    components: {
      GridLoader
    },
    created(){
      axios
        .get('/api/contents/news')
        .then(response => (
          this.afr_homepage_data = response.data.items.afr_homepage,
          this.afr_homepage = this.afr_homepage_data,

          this.afr_street_talk_data = response.data.items.afr_street_talk,
          this.afr_street_talk = this.afr_street_talk_data,

          this.aus_homepage_data = response.data.items.aus_homepage,
          this.aus_homepage = this.aus_homepage_data,

          this.aus_sections_data = response.data.items.aus_sections,
          this.aus_sections = this.aus_sections_data

          // console.log(response.data)
          // console.log(this.afr_homepage)
        ))
    },
    computed: {
      CategoryList: function({ aus_homepage }){
        return [...new Set(aus_homepage.map(d =>
        d.category))];
      },
      filteredAusHomepage() {
        
        const conditions = [];

        if (this.categorySelect) {
          conditions.push(this.filterAusHomepageCategory);
        }

        if (conditions.length > 0){
          return this.aus_homepage.filter((content) => {
            return conditions.every((condition) => {
              return condition(content)
            })
          })
        }

        return this.aus_homepage
      }
    },
    methods: {
      filterAusHomepageCategory(item) {
        return item.category == this.categorySelect
      }
    }
  }
</script>

<style scoped>
  .news-loading-box {
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