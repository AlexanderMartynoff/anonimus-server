import { createRouter, createWebHistory } from 'vue-router'
import MessangerPage from '../page/MessangerPage.vue'
import WelcomPage from '../page/WelcomPage.vue'


const routes = [
  {
    path: '/',
    component: WelcomPage,
  },
  {
    path: '/messanger',
    component: MessangerPage,
  },
]

const history = createWebHistory('/')

const router = createRouter({
  routes,
  history,
})

export default router
