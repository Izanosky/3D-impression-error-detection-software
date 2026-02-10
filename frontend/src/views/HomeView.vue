<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <i class="pi pi-shield"></i>
          <span>Detección Inteligente de Errores</span>
        </div>
        <h1 class="hero-title">
          Monitoriza tu impresora 3D
          <span class="gradient-text">en tiempo real</span>
        </h1>
        <p class="hero-subtitle">
          Detecta automáticamente errores de impresión como spaghetti, warping y otros fallos
          mediante inteligencia artificial, protegiendo tus impresiones y tu impresora.
        </p>
        <div class="hero-actions">
          <Button 
            label="Ir al Monitor" 
            icon="pi pi-arrow-right" 
            iconPos="right"
            size="large"
            @click="$router.push('/monitor')"
            class="cta-btn"
          />
          <Button 
            label="Saber más" 
            icon="pi pi-info-circle" 
            severity="secondary" 
            outlined
            size="large"
            @click="$router.push('/about')"
          />
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-glow"></div>
        <div class="hero-icon-container">
          <i class="pi pi-box hero-icon"></i>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <h2 class="section-title">Características principales</h2>
      <div class="features-grid">
        <Card class="feature-card" v-for="feature in features" :key="feature.title">
          <template #content>
            <div class="feature-icon-wrapper" :style="{ background: feature.gradient }">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </template>
        </Card>
      </div>
    </section>

    <!-- How it works -->
    <section class="how-it-works">
      <h2 class="section-title">¿Cómo funciona?</h2>
      <div class="steps">
        <div class="step" v-for="(step, index) in steps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import Card from 'primevue/card'

const features = [
  {
    icon: 'pi pi-camera',
    title: 'Monitorización Visual',
    description: 'Visualiza el estado de tu impresora en tiempo real a través de la cámara conectada.',
    gradient: 'linear-gradient(135deg, #6366f1, #818cf8)'
  },
  {
    icon: 'pi pi-exclamation-triangle',
    title: 'Detección de Errores con IA',
    description: 'Un modelo de IA analiza cada frame buscando errores como spaghetti y warping.',
    gradient: 'linear-gradient(135deg, #a855f7, #c084fc)'
  },
  {
    icon: 'pi pi-pause',
    title: 'Control Remoto',
    description: 'Pausa o reanuda la impresión directamente desde la interfaz web.',
    gradient: 'linear-gradient(135deg, #ec4899, #f472b6)'
  },
  {
    icon: 'pi pi-chart-bar',
    title: 'Estado en Tiempo Real',
    description: 'Monitoriza temperaturas, progreso de impresión y estado de la impresora.',
    gradient: 'linear-gradient(135deg, #14b8a6, #5eead4)'
  }
]

const steps = [
  {
    title: 'Conecta tu impresora',
    description: 'Configura la dirección IP de tu servidor OctoPrint y conecta la cámara web.'
  },
  {
    title: 'La IA analiza en tiempo real',
    description: 'Nuestro modelo de visión por computador analiza cada frame buscando anomalías.'
  },
  {
    title: 'Recibe alertas y actúa',
    description: 'Si se detecta un error, puedes pausar la impresión para evitar daños mayores.'
  }
]
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* ── Hero ── */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
  padding: 4rem 0 5rem;
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1rem;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 100px;
  font-size: 0.85rem;
  color: #818cf8;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 1.25rem;
  color: var(--text-color);
}

.gradient-text {
  background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.15rem;
  line-height: 1.7;
  color: var(--text-color-secondary);
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.cta-btn {
  background: linear-gradient(135deg, #6366f1, #a855f7) !important;
  border: none !important;
}

.cta-btn:hover {
  filter: brightness(1.15);
}

.hero-visual {
  flex-shrink: 0;
  position: relative;
  width: 300px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-glow {
  position: absolute;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%);
  border-radius: 50%;
  animation: glow-pulse 4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.15); opacity: 1; }
}

.hero-icon-container {
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(22, 33, 62, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid var(--surface-border);
  border-radius: 32px;
  z-index: 1;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.hero-icon {
  font-size: 4rem;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ── Features ── */
.features {
  padding: 3rem 0;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2.5rem;
  color: var(--text-color);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: rgba(22, 33, 62, 0.5) !important;
  backdrop-filter: blur(10px);
  border: 1px solid var(--surface-border) !important;
  border-radius: 16px !important;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
}

.feature-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.feature-icon-wrapper i {
  font-size: 1.25rem;
  color: white;
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feature-card p {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

/* ── How it works ── */
.how-it-works {
  padding: 3rem 0 4rem;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  position: relative;
}

.step {
  text-align: center;
  padding: 2rem 1.5rem;
  background: rgba(22, 33, 62, 0.4);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  transition: transform 0.3s ease;
}

.step:hover {
  transform: translateY(-4px);
}

.step-number {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-radius: 50%;
}

.step h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.step p {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 2rem 0;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-visual {
    width: 200px;
    height: 200px;
  }

  .hero-icon-container {
    width: 100px;
    height: 100px;
    border-radius: 24px;
  }

  .hero-icon {
    font-size: 2.5rem;
  }

  .steps {
    grid-template-columns: 1fr;
  }
}
</style>
