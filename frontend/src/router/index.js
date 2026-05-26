// Definición del router
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

// Definmos las rutas junto con sus respectivas vistas y si requieren autenticación
const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/monitor',
        name: 'monitor',
        component: () => import('../views/MonitorView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/about',
        name: 'about',
        component: () => import('../views/AboutView.vue')
    },
    {
        path: '/history',
        name: 'history',
        component: () => import('../views/HistoryView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/LoginView.vue')
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('../views/RegisterView.vue')
    },
    {
        path: '/settings',
        name: 'settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { requiresAuth: true }
    }
]

// Instanciamos el router
const router = createRouter({
    history: createWebHistory(), // Nos permite tener URLs limpias (sin #) y navegar sin recargar la página
    routes
})

import { auth } from '@/services/firebase'
import { onAuthStateChanged } from 'firebase/auth'

// Este método lo usamos para confirmar si había una sesión activa cuando recargamos la página
// Con esto evitamos que el usuario sea redirigido al login cuando recarga
function getCurrentUser() {
    return new Promise((resolve, reject) => {
        const removeListener = onAuthStateChanged(
            auth,
            (user) => {
                removeListener()
                resolve(user)
            },
            reject
        )
    })
}

// Y con esto evitamos que un usuario no logueado acceda a rutas que requieren autenticación
router.beforeEach(async (to, from, next) => {
    if (to.meta.requiresAuth) {
        const user = await getCurrentUser()
        if (user) {
            // Comprobamos que el usuario haya verificado su correo electrónico
            if (!user.emailVerified) {
                next('/login')
            } else {
                next()
            }
        } else {
            next('/login')
        }
    } else {
        next()
    }
})

export default router
