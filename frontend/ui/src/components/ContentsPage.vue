<template>
  <div>
    <v-tabs fixed-tabs v-model="activeTab" style="">
      <v-tab v-for="tab of tabs" :key="tab.id" :to="tab.route" exact>
        {{ tab.name }}
      </v-tab>

      <v-tab-item v-for="tab of tabs" :key="tab.id" :value="tab.route">
        <router-view></router-view>
      </v-tab-item>
    </v-tabs>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        activeTab: `/contents`,
        tabs: [
          { id: 1, name: "Announcements", route: `/contents` },
          { id: 2, name: "News", route: `/contents/news` },
          { id: 3, name: "Forecast", route: `/contents/forecast`}
        ]
      };
    }
  }
</script>