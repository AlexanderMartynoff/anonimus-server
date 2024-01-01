import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import naive from 'naive-ui'

import 'vfonts/Lato.css'
import 'vfonts/FiraCode.css'


import Root from './Root.vue'
import routes from './route.js'

import './style/main.scss'


const router = createRouter({
    routes,
    history: createWebHistory(),
})

createApp(Root)
    .use(router)
    .use(naive)
    .mount('body')
