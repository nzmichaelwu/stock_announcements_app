import Vue from 'vue'
import Router from 'vue-router'
import HomePage from './components/HomePage.vue'
import Contents from './components/ContentsPage.vue'
import AnnouncementsTab from './components/DataTable.vue'
import NewsTab from './components/NewsPage.vue'
import ForecastTab from './components/ForecastPage.vue'

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      component: HomePage
    },
    {
      path: "/contents",
      component: Contents,
      props: true,
      children: [
        {
          path: "",
          component: AnnouncementsTab
        },
        {
          path: "news",
          component: NewsTab
        },
        {
          path: "forecast",
          component: ForecastTab
        }
      ]
    }
  ],
  mode: "history"
})