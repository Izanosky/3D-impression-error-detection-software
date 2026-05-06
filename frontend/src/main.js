import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import Tooltip from 'primevue/tooltip'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import router from './router'
import App from './App.vue'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Card from 'primevue/card'
import Panel from 'primevue/panel'
import Avatar from 'primevue/avatar'
import Toast from 'primevue/toast'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import FloatLabel from 'primevue/floatlabel'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Password from 'primevue/password'
import Dialog from 'primevue/dialog'
import ProgressBar from 'primevue/progressbar'
import Select from 'primevue/select'
import FileUpload from 'primevue/fileupload'
import ConfirmDialog from 'primevue/confirmdialog'
import Menubar from 'primevue/menubar'
import TieredMenu from 'primevue/tieredmenu'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ToastService)
app.use(ConfirmationService)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.dark-mode'
        }
    }
})
app.directive('tooltip', Tooltip)

// Componentes registrados de forma global
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Card', Card)
app.component('Panel', Panel)
app.component('Avatar', Avatar)
app.component('Toast', Toast)
app.component('Message', Message)
app.component('Tag', Tag)
app.component('InputGroup', InputGroup)
app.component('InputGroupAddon', InputGroupAddon)
app.component('FloatLabel', FloatLabel)
app.component('IconField', IconField)
app.component('InputIcon', InputIcon)
app.component('Password', Password)
app.component('Dialog', Dialog)
app.component('ProgressBar', ProgressBar)
app.component('Select', Select)
app.component('FileUpload', FileUpload)
app.component('ConfirmDialog', ConfirmDialog)
app.component('Menubar', Menubar)
app.component('TieredMenu', TieredMenu)
app.component('DataTable', DataTable)
app.component('Column', Column)

app.mount('#app')
