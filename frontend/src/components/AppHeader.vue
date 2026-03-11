<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Brand (Left) -->
      <div class="header-left">
        <router-link to="/" class="header-brand">
          <img :src="logo" alt="PrintErr Logo" class="logo-image" />
          <span class="brand-text">PrintErr</span>
          <span class="header-status-dot" :class="'dot-' + printerStore.connectionStatus" :title="connectionTooltip"></span>
        </router-link>
      </div>

      <!-- Mobile Menu Toggle -->
      <button class="mobile-toggle" @click="toggleMenu" aria-label="Toggle menu">
        <i class="pi" :class="isMenuOpen ? 'pi-times' : 'pi-bars'"></i>
      </button>

      <!-- Desktop Navigation (Center) -->
      <nav class="header-center desktop-only">
        <router-link to="/" class="nav-link" exact-active-class="nav-link--active">
          <i class="pi pi-home nav-icon"></i>
          <span>Inicio</span>
        </router-link>
        <router-link to="/about" class="nav-link" active-class="nav-link--active">
          <i class="pi pi-info-circle nav-icon"></i>
          <span>Sobre Nosotros</span>
        </router-link>
        <router-link to="/monitor" class="nav-link" active-class="nav-link--active">
          <i class="pi pi-desktop nav-icon"></i>
          <span>Monitorización</span>
        </router-link>
        <router-link to="/timelapse" class="nav-link" active-class="nav-link--active">
          <i class="pi pi-video nav-icon"></i>
          <span>Biblioteca</span>
        </router-link>
      </nav>

      <!-- Desktop Auth (Right) -->
      <div class="header-right desktop-only">
        <template v-if="!userStore.currentUser">
          <router-link to="/login" class="btn-login">
            <i class="pi pi-sign-in"></i>
            <span>Login</span>
          </router-link>
        </template>
        <template v-else>
          <div class="user-actions">
            <div class="user-badge">
              <div class="user-avatar">{{ userInitials }}</div>
              <span class="username">{{ userStore.userName }}</span>
            </div>
            <button class="icon-btn" @click="openSettings" title="Ajustes">
              <i class="pi pi-cog"></i>
            </button>
            <button class="btn-logout" @click="handleLogout">
              <i class="pi pi-sign-out"></i>
              <span>Salir</span>
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Mobile Menu (Dropdown) -->
    <Transition name="slide-fade">
      <div v-if="isMenuOpen" class="mobile-menu">
        <router-link to="/" class="mobile-link" @click="closeMenu">
          <i class="pi pi-home"></i> Inicio
        </router-link>
        <router-link to="/about" class="mobile-link" @click="closeMenu">
          <i class="pi pi-info-circle"></i> Sobre Nosotros
        </router-link>
        <router-link to="/monitor" class="mobile-link" @click="closeMenu">
          <i class="pi pi-desktop"></i> Monitorización
        </router-link>
        <router-link to="/timelapse" class="mobile-link" @click="closeMenu">
          <i class="pi pi-video"></i> Timelapses
        </router-link>

        <div class="mobile-divider"></div>

        <template v-if="!userStore.currentUser">
          <router-link to="/login" class="mobile-link" @click="closeMenu">
            <i class="pi pi-sign-in"></i> Login
          </router-link>
        </template>
        <template v-else>
          <div class="mobile-user-info">
            <div class="user-avatar user-avatar--sm">{{ userInitials }}</div>
            {{ userStore.userName }}
          </div>
          <a href="#" class="mobile-link" @click.prevent="openSettingsMobile">
            <i class="pi pi-cog"></i> Ajustes
          </a>
          <a href="#" class="mobile-link" @click.prevent="handleLogoutMobile">
            <i class="pi pi-sign-out"></i> Cerrar sesión
          </a>
        </template>
      </div>
    </Transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'
import { usePrinterStore } from '../stores/printer'
import { signOut } from '../services/authService'
import { useRouter } from 'vue-router'
import logo from '../assets/logo.png'

const userStore = useUserStore()
const printerStore = usePrinterStore()
const router = useRouter()

const isMenuOpen = ref(false)

// Close mobile menu when resizing back to desktop
function handleResize() {
  if (window.innerWidth > 1024 && isMenuOpen.value) {
    isMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const connectionTooltip = computed(() => {
  switch (printerStore.connectionStatus) {
    case 'printer': return 'Conectado a impresora'
    case 'backend': return 'Conectado al backend'
    default: return 'Desconectado'
  }
})

const userInitials = computed(() => {
  const name = userStore.userName || ''
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function closeMenu() {
  isMenuOpen.value = false
}

function openSettings() {
  printerStore.showSettings = true
}

function openSettingsMobile() {
  printerStore.showSettings = true
  closeMenu()
}

async function handleLogout() {
  try {
    await signOut()
    router.push('/login')
  } catch (error) {
    console.error('Error logging out:', error)
  }
}

async function handleLogoutMobile() {
  await handleLogout()
  closeMenu()
}
</script>

<style scoped>
/* ─── Header Shell ─── */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  background: rgba(10, 10, 36, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(99, 102, 241, 0.12);
}

.header-inner {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 64px;
}

/* ─── Brand ─── */
.header-left {
  display: flex;
  align-items: center;
}

.header-brand {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  transition: opacity 0.2s;
}

.header-brand:hover {
  opacity: 0.85;
}

.logo-image {
  height: 36px;
  width: auto;
  object-fit: contain;
}

.brand-text {
  font-size: 1.35rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.25px;
}

/* ─── Status Dot ─── */
.header-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 2px;
  flex-shrink: 0;
  transition: background 0.3s, box-shadow 0.3s;
}

.dot-disconnected {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.dot-backend {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
}

.dot-printer {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

/* ─── Navigation (Center) ─── */
.header-center {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.nav-link {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: color 0.2s, background 0.2s;
  cursor: pointer;
  white-space: nowrap;
}

.nav-icon {
  font-size: 0.9rem;
}

.nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

.nav-link--active {
  color: #fff;
  background: rgba(99, 102, 241, 0.15);
}

/* ─── Right Section ─── */
.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* User Badge */
.user-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.75rem 0.3rem 0.3rem;
  border-radius: 100px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #a78bfa);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.user-avatar--sm {
  width: 26px;
  height: 26px;
  font-size: 0.65rem;
}

.username {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
  font-weight: 500;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Icon Button (Settings) */
.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
  font-size: 1rem;
}

.icon-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

/* Login / Logout Buttons */
.btn-login {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  text-decoration: none;
  background: var(--primary-color);
  transition: background 0.2s, transform 0.15s;
}

.btn-login:hover {
  background: #4f46e5;
  transform: translateY(-1px);
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.btn-logout:hover {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
  background: rgba(248, 113, 113, 0.08);
}

/* ─── Mobile Toggle ─── */
.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: #fff;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.mobile-toggle:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* ─── Mobile Menu ─── */
.mobile-menu {
  position: absolute;
  top: 64px;
  left: 0;
  width: 100%;
  background: rgba(10, 10, 36, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
}

.mobile-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.mobile-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 0.35rem 0;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 0.5rem;
  color: var(--primary-color);
  font-size: 0.95rem;
  font-weight: 600;
}

/* ─── Responsive ─── */
@media (max-width: 1024px) {
  .header-inner {
    display: flex;
    justify-content: space-between;
    padding: 0 1.25rem;
  }

  .desktop-only {
    display: none;
  }

  .mobile-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* ─── Transitions ─── */
.slide-fade-enter-active {
  transition: all 0.25s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.15s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
