import WelcomPage from './page/WelcomPage.vue'
import MessangerPage from './page/MessangerPage.vue'
import SndboxPage from './page/SndboxPage.vue'


export default [
    { path: '/', component: WelcomPage },
    { path: '/chat', component: MessangerPage },
    { path: '/sandbox', component: SndboxPage },
]
