/*
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './practice/WeatherMockup_ver3/WeatherParent.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

*/

import { createApp } from 'vue'
import { createPinia } from 'pinia'
//import router from './router_ver4'
//import router from './router_ver5'
//import router from './router_ver6'
import router from './router_ver7'

// import App from './practice/WeatherMockup_ver1.vue'
// import App from './practice/WeatherMockup_ver2.vue'
// import App from './practice/WeatherMockup_ver3/WeatherParent.vue'
//import App from './App_ver4.vue'
//import App from './App_ver5.vue'
//import App from './basic/library/AxiosJson.vue'
//import App from './App_ver6.vue'
import App from './App_ver7.vue'
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
