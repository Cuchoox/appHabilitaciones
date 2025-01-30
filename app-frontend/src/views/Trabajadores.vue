<template>
  <div class="trabajadores-container">
      <div class="sidebar-container">
          <Sidebar />
      </div>
      <main class="content">
          <h1>Lista de Trabajadores</h1>

          <!-- Pestañas de Tipo de Trabajador -->
          <div class="tabs">
              <button 
                  :class="{ active: selectedTab === 'Planta' }"
                  @click="selectedTab = 'Planta'">
                   De Planta
              </button>
              <button 
                  :class="{ active: selectedTab === 'Eventual' }"
                  @click="selectedTab = 'Eventual'">
                   Eventuales
              </button>
          </div>

          <!-- Barra de búsqueda y filtro por empresa -->
          <div class="filtros">
              <input v-model="searchQuery" type="text" placeholder="🔍 Buscar trabajador..." />
              <select v-model="selectedEmpresa">
                  <option value="">📌 Filtrar por empresa</option>
                  <option v-for="empresa in empresas" :key="empresa.id" :value="empresa.id">
                      {{ empresa.nombre }}
                  </option>
              </select>
          </div>

          <!-- Tabla de trabajadores -->
          <table class="tabla-trabajadores">
              <thead>
                  <tr>
                      <th>Nombre</th>
                      <th>RUT</th>
                      <th>Cargo</th>
                      <th>Acciones</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="trabajador in filteredTrabajadores" :key="trabajador.id">
                      <td style="color: black;">{{ trabajador.nombre }}</td>
                      <td style="color: black;">{{ trabajador.rut }}</td>
                      <td style="color: black;">{{ trabajador.cargo }}</td>
                      <td>
                          <button class="ver" @click="verTrabajador(trabajador)">👁 Ver</button>
                          <button class="editar" @click="editarTrabajador(trabajador)">✏ Editar</button>
                          <button class="eliminar" @click="eliminarTrabajador(trabajador.id)">🗑 Eliminar</button>
                      </td>
                  </tr>
              </tbody>
          </table>

          <!-- Botón flotante para agregar trabajador -->
          <button class="boton-flotante" @click="mostrarFormulario = true">➕ Agregar Trabajador</button>
          <FormularioTrabajador 
                :mostrar="mostrarFormulario" 
                @cerrar="mostrarFormulario = false" 
                @agregar="agregarTrabajador"
            />
        </main>
  </div>
</template>

<script>
import Sidebar from "../components/Sidebar.vue";
import FormularioTrabajador from "../components/FormularioTrabajador.vue"; // Importar el componente

export default {
  components: { Sidebar, FormularioTrabajador }, // Registrar el componente
  data() {
      return {
          mostrarFormulario: false, // Controla la visibilidad del formulario
          selectedTab: "Planta", // Controla la pestaña activa
          searchQuery: "",
          selectedEmpresa: "",
          trabajadores: [
              { id: 1, nombre: "Juan Pérez", rut: "12.345.678-9", cargo: "Supervisor", tipo: "Planta", empresaId: 1 },
              { id: 2, nombre: "Pedro Gómez", rut: "9.876.543-2", cargo: "Técnico", tipo: "Eventual", empresaId: 2 },
              { id: 3, nombre: "María González", rut: "11.654.321-5", cargo: "Administrativa", tipo: "Planta", empresaId: 1 },
              { id: 4, nombre: "Carlos Rodríguez", rut: "14.789.654-3", cargo: "Operario", tipo: "Eventual", empresaId: 2 }
          ],
          empresas: [
              { id: 1, nombre: "Empresa A" },
              { id: 2, nombre: "Empresa B" }
          ]
      };
  },
  computed: {
      filteredTrabajadores() {
          return this.trabajadores.filter(trabajador =>
              trabajador.nombre.toLowerCase().includes(this.searchQuery.toLowerCase()) &&
              (this.selectedEmpresa === "" || trabajador.empresaId == this.selectedEmpresa) &&
              trabajador.tipo === this.selectedTab
          );
      }
  },
  methods: {
      verTrabajador(trabajador) {
          alert(`Ver detalles de ${trabajador.nombre}`);
      },
      editarTrabajador(trabajador) {
          alert(`Editar ${trabajador.nombre}`);
      },
      eliminarTrabajador(id) {
          this.trabajadores = this.trabajadores.filter(t => t.id !== id);
      },
      async agregarTrabajador(nuevoTrabajador) {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

        if (!token) {
            alert("No tienes autorización. Inicia sesión nuevamente.");
            this.$router.push("/"); // Redirige al login si no hay token
            return;
        }

        try {
            const response = await fetch("http://localhost:5000/trabajadores", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`  // Enviar el token JWT
                },
                body: JSON.stringify(nuevoTrabajador),
            });

            if (!response.ok) {
                throw new Error("Error al agregar el trabajador");
            }

            const trabajadorGuardado = await response.json();
            this.trabajadores.push(trabajadorGuardado);
        } catch (error) {
            console.error("Error:", error);
            alert("No se pudo agregar el trabajador. Inténtelo de nuevo.");
        }
    },

    async obtenerTrabajadores() {
    try {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        const response = await fetch("http://localhost:5000/trabajadores", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`, // 🔹 Asegúrate de enviar el token
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Error al obtener trabajadores");
        }

        this.trabajadores = await response.json();
    } catch (error) {
        console.error("Error:", error);
    }
}

},

// Cuando el componente carga, obtiene los trabajadores


created() {
    this.obtenerTrabajadores();
}
};
</script>

<style scoped>
/* 📌 Contenedor Principal */
.trabajadores-container {
  display: flex;
  height: 100vh;
  width: 85.5vw;
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
  background-color: #f0f0f0;
  z-index: 1000;
}

/* 📌 Contenido */
.content {
  flex-grow: 1;
  padding: 20px;
  background-color: #f9f9f9;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 🔹 Encabezado */
h1 {
  text-align: center;
  color: #134b91;
  margin-bottom: 20px;
}

/* 🔹 Pestañas */
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.tabs button {
  background: #ccc;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 5px;
  margin: 0 5px;
  transition: 0.3s;
}

.tabs button.active {
  background: #134b91;
  color: white;
}

/* 🔹 Filtros */
.filtros {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 10px;
}

input, select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 48%;
  box-sizing: border-box;
}

/* 🔹 Tabla de trabajadores */
.tabla-trabajadores {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 10px;
  table-layout: fixed;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  word-wrap: break-word;
}

th {
  background-color: #134b91;
  color: white;
}

/* 🔹 Botones */
button {
  border: none;
  padding: 8px;
  margin: 5px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.ver { background-color: #007bff; color: white; }
.editar { background-color: #ffc107; color: black; }
.eliminar { background-color: #dc3545; color: white; }

/* 🔹 Botón Flotante */
.boton-flotante {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #28a745;
  color: white;
  padding: 15px 20px;
  border-radius: 50px;
  font-size: 1rem;
  cursor: pointer;
  z-index: 1000;
}
</style>
