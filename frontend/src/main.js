import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import * as echarts from 'echarts'

const app = createApp(App)

app.config.globalProperties.$echarts = echarts
app.use(ElementPlus)
app.use(router)
app.use(store)

app.mount('#app') 