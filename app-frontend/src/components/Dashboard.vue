
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
                    <p>{{ documentosVencidos.length }} documentos han expirado</p>
                    <button class="view-btn" @click="cargarDetalles('vencidos')">Ver detalles</button>
                </div>
  
                <div class="alert-card warning">
                    <h3>⚠️ Próximos a Vencer</h3>
                    <p>{{ documentosProximos.length }} documentos vencen en los próximos 30 días</p>
                    <button class="view-btn" @click="cargarDetalles('proximos')">Ver documentos</button>
                </div>
            </section>
        </main>
  
        <div v-if="mostrarModal" class="modal-overlay">
    <div class="modal">
        <h2>{{ tituloModal }}</h2>
        
        <!-- 🔹 Mostrar mensaje si hay demasiados documentos -->
        <p v-if="trabajadoresFiltrados.length > 15" class="alerta">
            ⚠️ Hay demasiados documentos para mostrar aquí. Abre la vista completa.
        </p>

        <button v-if="trabajadoresFiltrados.length > 15" class="boton-ver-mas" @click="$router.push('/documentos-vencidos')">
            🔍 Ver en pantalla completa
        </button>

        <button v-if="trabajadoresFiltrados.length <= 15" class="refresh-btn" @click="refrescarDocumentos">🔄 Refrescar</button>

        <ul v-if="trabajadoresFiltrados.length <= 15">
            <li v-for="(trabajador, index) in trabajadoresFiltrados" :key="index">
                <div class="trabajador" @click="trabajador.expandido = !trabajador.expandido">
                    {{ trabajador.nombre }} - {{ trabajador.documentos.length }} documentos
                </div>
                <ul v-if="trabajador.expandido" class="documentos-lista">
                    <li v-for="doc in trabajador.documentos" :key="doc.id">
                        📄 {{ doc.tipo_documento }} - {{ new Date(doc.fecha_vencimiento).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' }) }}
                    </li>
                </ul>
            </li>
        </ul>
        <button class="cerrar-modal" @click="cerrarModal">❌ Cerrar</button>
    </div>
</div>

    </div>
  </template>
  
  <script>
  import Sidebar from "./Sidebar.vue";
  
  export default {
    name: "Dashboard",
    components: { Sidebar },
    data() {
        return {
            workersCount: 0,
            documentsCount: 0,
            companiesCount: 0,
            documentosVencidos: [],
            documentosProximos: [],
            trabajadoresFiltrados: [],
            mostrarModal: false,
            tituloModal: ""
        };
    },
    created() {
        this.verificarAutenticacion();
        this.obtenerConteos();
        this.obtenerDocumentos();
    },
    methods: {
        verificarAutenticacion() {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (!token) this.$router.push("/");
    },
    async obtenerConteos() {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (!token) return;
        try {
            const [trabajadoresRes, empresasRes, documentosRes] = await Promise.all([
                fetch("http://localhost:5000/trabajadores/count", { headers: { "Authorization": `Bearer ${token}` } }),
                fetch("http://localhost:5000/empresas/count", { headers: { "Authorization": `Bearer ${token}` } }),
                fetch("http://localhost:5000/documentos/count", { headers: { "Authorization": `Bearer ${token}` } })
            ]);
            this.workersCount = (await trabajadoresRes.json()).count;
            this.companiesCount = (await empresasRes.json()).count;
            this.documentsCount = (await documentosRes.json()).count;
        } catch (err) {
            console.error("❌ Error al obtener conteos:", err);
        }
    },
    async obtenerDocumentos() {  // 🔹 Reagregada la función
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (!token) return;
        try {
            const response = await fetch("http://localhost:5000/documentos-general", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

            const data = await response.json();
            if (!Array.isArray(data)) {
                throw new Error(`❌ La respuesta del backend no es una lista de documentos: ${JSON.stringify(data)}`);
            }

            console.log("📥 Documentos obtenidos:", data);

            const hoy = new Date();
            this.documentosVencidos = data.filter(doc => new Date(doc.fecha_vencimiento) < hoy);
            this.documentosProximos = data.filter(doc => {
                const fechaDoc = new Date(doc.fecha_vencimiento);
                return fechaDoc >= hoy && fechaDoc <= new Date(hoy.setDate(hoy.getDate() + 30));
            });

        } catch (err) {
            console.error("❌ Error al obtener documentos:", err);
        }
    },
    
    refrescarDocumentos() {
        this.obtenerDocumentos();
    },
    cerrarModal() {
        this.mostrarModal = false;
    },
    agruparPorTrabajador(documentos) {
    let map = {};
    documentos.forEach(doc => {
        if (!doc.trabajador_id) {
            console.warn("⚠️ Documento sin trabajador asociado:", doc);
            return;
        }

        if (!map[doc.trabajador_id]) {
            map[doc.trabajador_id] = { 
                id: doc.trabajador_id,
                nombre: doc.nombre_trabajador || "Desconocido", // Asegúrate de que el backend lo envíe
                documentos: [],
                expandido: false
            };
        }
        map[doc.trabajador_id].documentos.push(doc);
    });
    return Object.values(map);
},



        cargarDetalles(tipo) {
    if (tipo === "vencidos") {
        this.trabajadoresFiltrados = this.agruparPorTrabajador(this.documentosVencidos);
        this.tituloModal = "📌 Documentos Vencidos";
    } else {
        this.trabajadoresFiltrados = this.agruparPorTrabajador(this.documentosProximos);
        this.tituloModal = "⏳ Documentos Próximos a Vencer";
    }

    // 🔹 Límite de 15 trabajadores en el modal
    if (this.trabajadoresFiltrados.length > 15) {
        this.mostrarModal = false; // Ocultar el modal si se supera el límite
        this.$router.push('/documentos-vencidos'); // Redirigir a nueva pantalla
    } else {
        this.mostrarModal = true;
    }
},
    },
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
    width: calc(100% - 250px);
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
    margin-left: 190px;
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
    margin-right: 265px;
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
    background-color: #ee0000;
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

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 600px; /* Agrandado el modal */
    max-width: 90%;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    text-align: left;
    position: relative;
}

.modal h2 {
    margin-top: 0;
    font-size: 1.5rem;
    color: #113c70;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 10px;
}

.modal .alerta {
    background-color: #ffcc00;
    color: black;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 15px;
    font-weight: bold;
}

.modal .boton-ver-mas,
.modal .refresh-btn,
.modal .cerrar-modal {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s ease-in-out;
}

.modal .boton-ver-mas {
    background-color: #134b91;
    color: white;
}

.modal .refresh-btn {
    background-color: #ffcc00;
    color: black;
}

.modal .cerrar-modal {
    background-color: #ff4d4d;
    color: white;
    position: absolute;
    top: 10px;
    right: 10px;
}

.modal .boton-ver-mas:hover,
.modal .refresh-btn:hover,
.modal .cerrar-modal:hover {
    opacity: 0.8;
}

.modal ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
}

.modal ul li {
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.modal ul li:last-child {
    border-bottom: none;
}

.modal .trabajador {
    font-weight: bold;
    cursor: pointer;
    font-size: 1.1rem; /* Agrandado el tamaño de la letra */
    color: #113c70; /* Cambiado el color de la letra */
}

.modal .documentos-lista {
    margin-top: 10px;
    padding-left: 20px;
}

.modal .documentos-lista li {
    color: black; /* Color del nombre del documento */
}


</style>
