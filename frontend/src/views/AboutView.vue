<template>
  <div class="about-view">
    <section class="about-hero">
      <h1 class="about-title">Acerca del Proyecto</h1>
      <p class="about-subtitle">
        Trabajo de Fin de Grado — Detección de errores en impresión 3D
      </p>
    </section>

    <!-- Project Description -->
    <section class="about-section">
      <Card class="about-card">
        <template #content>
          <div class="card-icon-wrapper" style="background: linear-gradient(135deg, #6366f1, #818cf8)">
            <i class="pi pi-book"></i>
          </div>
          <h2>Descripción del proyecto</h2>
          <p>
            Este proyecto implementa un sistema de monitorización en tiempo real para impresoras 3D,
            capaz de detectar errores de impresión de forma automática utilizando modelos de visión por 
            computador e inteligencia artificial.
          </p>
          <p>
            El sistema se conecta a OctoPrint para obtener el estado de la impresora y la imagen de la cámara,
            analiza cada frame con un modelo entrenado en Roboflow, y muestra los resultados en una interfaz
            web moderna. Si se detecta un error, el usuario puede pausar la impresión para evitar daños mayores.
          </p>
        </template>
      </Card>
    </section>

    <!-- Tech Stack -->
    <section class="about-section">
      <h2 class="section-title">Stack Tecnológico</h2>
      <div class="tech-grid">
        <div class="tech-item" v-for="tech in techStack" :key="tech.name">
          <div class="tech-icon-wrapper" :style="{ background: tech.color }">
            <i :class="tech.icon"></i>
          </div>
          <div class="tech-info">
            <h3>{{ tech.name }}</h3>
            <p>{{ tech.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Architecture -->
    <section class="about-section">
      <Card class="about-card">
        <template #content>
          <div class="card-icon-wrapper" style="background: linear-gradient(135deg, #14b8a6, #5eead4)">
            <i class="pi pi-sitemap"></i>
          </div>
          <h2>Arquitectura</h2>
          <div class="architecture-flow">
            <div class="arch-item">
              <i class="pi pi-camera"></i>
              <span>Cámara</span>
            </div>
            <i class="pi pi-arrow-right arch-arrow"></i>
            <div class="arch-item">
              <i class="pi pi-server"></i>
              <span>OctoPrint</span>
            </div>
            <i class="pi pi-arrow-right arch-arrow"></i>
            <div class="arch-item">
              <i class="pi pi-cog"></i>
              <span>Backend (FastAPI)</span>
            </div>
            <i class="pi pi-arrow-right arch-arrow"></i>
            <div class="arch-item">
              <i class="pi pi-desktop"></i>
              <span>Frontend (Vue.js)</span>
            </div>
          </div>
        </template>
      </Card>
    </section>

    <!-- Author -->
    <section class="about-section">
      <Card class="about-card author-card">
        <template #content>
          <div class="card-icon-wrapper" style="background: linear-gradient(135deg, #ec4899, #f472b6)">
            <i class="pi pi-user"></i>
          </div>
          <h2>Autor</h2>
          <p>
            Proyecto desarrollado como Trabajo de Fin de Grado (TFG).
          </p>
        </template>
      </Card>
    </section>
  </div>
</template>

<script setup>
import Card from 'primevue/card'

const techStack = [
  {
    name: 'Vue.js 3',
    description: 'Framework frontend con Composition API',
    icon: 'pi pi-globe',
    color: 'linear-gradient(135deg, #42b883, #35495e)'
  },
  {
    name: 'FastAPI',
    description: 'Backend Python de alto rendimiento',
    icon: 'pi pi-bolt',
    color: 'linear-gradient(135deg, #009688, #00bcd4)'
  },
  {
    name: 'Roboflow',
    description: 'Modelo de detección de errores',
    icon: 'pi pi-eye',
    color: 'linear-gradient(135deg, #6366f1, #8b5cf6)'
  },
  {
    name: 'OctoPrint',
    description: 'Control de impresora 3D',
    icon: 'pi pi-print',
    color: 'linear-gradient(135deg, #2ecc71, #27ae60)'
  },
  {
    name: 'WebSocket',
    description: 'Comunicación en tiempo real',
    icon: 'pi pi-arrows-h',
    color: 'linear-gradient(135deg, #e74c3c, #c0392b)'
  },
  {
    name: 'PrimeVue',
    description: 'Librería de componentes UI',
    icon: 'pi pi-palette',
    color: 'linear-gradient(135deg, #3b82f6, #2563eb)'
  }
]
</script>

<style scoped>
.about-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.about-hero {
  text-align: center;
  padding: 3rem 0 2rem;
}

.about-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.75rem;
}

.about-subtitle {
  font-size: 1.15rem;
  color: var(--text-color-secondary);
}

.about-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-color);
}

.about-card {
  background: rgba(22, 33, 62, 0.5) !important;
  backdrop-filter: blur(10px);
  border: 1px solid var(--surface-border) !important;
  border-radius: 16px !important;
}

.card-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.card-icon-wrapper i {
  font-size: 1.25rem;
  color: white;
}

.about-card h2 {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.about-card p {
  color: var(--text-color-secondary);
  line-height: 1.7;
  margin-bottom: 0.75rem;
}

.about-card p:last-child {
  margin-bottom: 0;
}

/* ── Tech Grid ── */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.tech-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(22, 33, 62, 0.5);
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.tech-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.tech-icon-wrapper {
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tech-icon-wrapper i {
  font-size: 1.15rem;
  color: white;
}

.tech-info h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.tech-info p {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

/* ── Architecture ── */
.architecture-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1.5rem 0;
  flex-wrap: wrap;
}

.arch-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.arch-item i {
  font-size: 1.25rem;
  color: #818cf8;
}

.arch-arrow {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .about-title {
    font-size: 1.75rem;
  }

  .architecture-flow {
    flex-direction: column;
  }

  .arch-arrow {
    transform: rotate(90deg);
  }
}
</style>
