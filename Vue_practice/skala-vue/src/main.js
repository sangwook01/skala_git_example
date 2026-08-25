import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

//import App from './App.vue'
//import App from './HelloWorld.vue'
//import App from './SampleOne.vue'
import App from './SampleTwo.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
