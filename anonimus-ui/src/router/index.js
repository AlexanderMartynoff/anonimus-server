import { createRouter, createWebHistory } from 'vue-router'
import MessangerPage from '../page/MessangerPage.vue'
import IndexPage from '../page/IndexPage.vue'


const routes = [
  {
    path: '/',
    component: IndexPage,
  },
  {
    name: 'messanger',
    path: '/messanger/:chat',
    component: MessangerPage,
    props: true,
  },
]

const history = createWebHistory('/')

const router = createRouter({
  routes,
  history,
})

export default router
