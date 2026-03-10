import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
        path: '/timelapse',
        name: 'timelapse',
        component: () => import('../views/TimelapseView.vue'),
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
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

import { auth } from '@/services/firebase'
import { onAuthStateChanged } from 'firebase/auth'

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

router.beforeEach(async (to, from, next) => {
    if (to.meta.requiresAuth) {
        if (await getCurrentUser()) {
            next()
        } else {
            next('/login')
        }
    } else {
        next()
    }
})

export default router
