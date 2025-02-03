<template>
    <div class="dashboard">
      <div class="sidebar-container">
        <Sidebar />
      </div>
      <main class="content">
        <header class="header">
          <h1 style="text-align: center; width: 100%;"></h1>
        </header>
        <section class="stats">
  <div class="stat-card">
    <h3>Trabajadores</h3>
    <p>{{ workersCount }}</p>
  </div>
  <div class="stat-card">
    <h3>Empresas</h3>
    <p>{{ companiesCount }}</p>
  </div>
  <div class="stat-card">
    <h3>Documentos</h3>
    <p>{{ documentsCount }}</p>
  </div>
</section>

        <!-- Nueva Sección: Documentos Próximos a Vencer -->
        <section class="alerts">
          <div class="alert-card danger">
            <h3>🚨 Documentos Vencidos</h3>
            <p>5 documentos han expirado</p>
            <button class="view-btn">Ver detalles</button>
          </div>
  
          <div class="alert-card warning">
            <h3>⚠️ Próximos a Vencer</h3>
            <p>10 documentos vencen en los próximos 30 días</p>
            <button class="view-btn">Ver documentos</button>
          </div>
        </section>
      </main>
    </div>
  </template>
  
  <script>
  import Sidebar from "./Sidebar.vue";
  
  export default {
    name: "Dashboard",
    components: {
      Sidebar,
    },
    data() {
      return {
        workersCount: 0,
        documentsCount: 0,
        companiesCount: 0,
      };
    },
    created() {
      console.log("Cargando Dashboard...");
      
      // Verificar si hay un token de sesión
      const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
      
      if (!token) {
        console.log("No se encontró un token. Redirigiendo a login...");
        this.$router.push("/");
      } else {
        console.log("Token detectado:", token);
        this.obtenerConteos();
      }
    },
    methods: {
      async obtenerConteos() {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  
        if (!token) {
          console.error("❌ No se encontró token de autenticación");
          return;
        }
  
        try {
          const [trabajadoresRes, empresasRes, documentosRes] = await Promise.all([
            fetch("http://localhost:5000/trabajadores/count", {
              headers: { "Authorization": `Bearer ${token}` }
            }),
            fetch("http://localhost:5000/empresas/count", {
              headers: { "Authorization": `Bearer ${token}` }
            }),
            fetch("http://localhost:5000/documentos/count", {
              headers: { "Authorization": `Bearer ${token}` }
            })
          ]);
  
          if (!trabajadoresRes.ok || !empresasRes.ok || !documentosRes.ok) {
            throw new Error("Error obteniendo conteos desde la API");
          }
  
          const trabajadoresData = await trabajadoresRes.json();
          const empresasData = await empresasRes.json();
          const documentosData = await documentosRes.json();
  
          this.workersCount = trabajadoresData.count;
          this.companiesCount = empresasData.count;
          this.documentsCount = documentosData.count;
  
          console.log("✅ Conteos obtenidos:", this.workersCount, this.companiesCount, this.documentsCount);
          
        } catch (err) {
          console.error("❌ Error al obtener conteos:", err);
        }
      }
    }
  };
  </script>
  
  
  <style scoped>
/* 🔹 Ajustes generales para evitar scroll horizontal */
html, body {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 📌 Contenedor Principal */
.dashboard {
    display: flex;
    height: 100vh;
    width: 100vw; /* Ajusta para que ocupe toda la pantalla */
    overflow: hidden;
}

/* 📌 Sidebar */
.sidebar-container {
    width: 250px;
    flex-shrink: 0;
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
}

/* 📌 Contenido */
.content {
    flex-grow: 1;
    width: calc(100vw - 250px);
    padding: 20px;
    background-color: #f3f3f3;
    overflow-y: auto;
    overflow-x: hidden; /* Evita desplazamiento lateral */
}

/* 🔹 Sección de estadísticas */
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    justify-content: center;
    max-width: 1000px;
    margin: 0 auto;
}

/* 🔹 Tarjetas */
.stat-card {
    margin-top: 30px;
    background-color: #ffffff;
    border: 1px solid #113c70;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    color: black;
    transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
    transform: translateY(-5px);
}

/* 🔹 Ajuste de textos dentro de las tarjetas */
.stat-card h3 {
    font-size: 1.3rem;
    color: #134b91;
}

.stat-card p {
    font-size: 1rem;
    color: #1c1c1c;
}

.alerts {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 20px;
}

/* Tarjetas de alertas */
.alert-card {
    margin-top: 30px;
    flex: 1;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-weight: bold;
    max-width: 400px;
}

.danger {
    background-color: #ff1616;
    color: white;
}

.warning {
    background-color: #ffcc00;
    color: black;
}

/* Botón de Ver Documentos */
.view-btn {
    margin-top: 8px;
    padding: 6px 12px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: bold;
    transition: background 0.3s ease-in-out;
}

.danger .view-btn {
    background-color: white;
    color: #ff4d4d;
}

.warning .view-btn {
    background-color: black;
    color: yellow;
}

.view-btn:hover {
    opacity: 0.8;
}
</style>
