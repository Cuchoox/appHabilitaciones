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
                      <th>Apellidos</th>
                      <th>RUT</th>
                      <th>Cargo</th>
                      <th>Acciones</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="trabajador in filteredTrabajadores" :key="trabajador.id">
                      <td style="color: black;">{{ trabajador.nombre }}</td>
                      <td style="color: black;">{{trabajador.apellido}}</td>
                      <td style="color: black;">{{ trabajador.rut }}</td>
                      <td style="color: black;">{{ trabajador.cargo }}</td>
                      <td>
                          <button class="editar" @click="editarTrabajador(trabajador)">✏ Editar</button>
                          <button class="eliminar" @click="eliminarTrabajador(trabajador.id)">🗑 Eliminar</button>
                          <button class="documentos" @click="verDocumentos(trabajador.id)">📂 Documentos</button>

                          
                      </td>
                  </tr>
              </tbody>
          </table>

          <!-- Botón flotante para agregar trabajador -->
          <button class="boton-flotante" @click="mostrarFormulario = true">➕ Agregar Trabajador</button>
          <FormularioTrabajador 
  :mostrar="mostrarFormulario" 
  :trabajador="trabajadorEditado"
  @cerrar="cerrarFormulario"
  @agregar="agregarTrabajador"
  @editar="guardarEdicionTrabajador"
/>

        </main>
  </div>
</template>

<script>
import Sidebar from "../components/Sidebar.vue";
import FormularioTrabajador from "../components/FormularioTrabajador.vue"; // Importar el componente
import Swal from "sweetalert2"; // Importamos SweetAlert2


export default {
  components: { Sidebar, FormularioTrabajador }, // Registrar el componente
  data() {
      return {
          trabajadorEditado: null,
          mostrarFormulario: false, // Controla la visibilidad del formulario
          selectedTab: "Planta", // Controla la pestaña activa
          searchQuery: "",
          selectedEmpresa: "",
          trabajadores: [],
         
      };
  },
  computed: {
    filteredTrabajadores() {
  return this.trabajadores.filter(trabajador => {
    // Verificamos si trabajador.nombre está definido antes de usar toLowerCase()
    const nombre = trabajador.nombre ? trabajador.nombre.toLowerCase() : "";

    return (
      nombre.includes(this.searchQuery.toLowerCase()) &&
      (this.selectedEmpresa === "" || trabajador.empresaId == this.selectedEmpresa) &&
      trabajador.tipo === this.selectedTab
    );
  });
}

  },
  methods: {
    verTrabajador(trabajador) {
      alert(`👁️ ${trabajador.nombre} - ${trabajador.rut} - ${trabajador.cargo}`);
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
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                nombre: nuevoTrabajador.nombre,
                rut: nuevoTrabajador.rut,
                apellido: nuevoTrabajador.apellido,
                cargo: nuevoTrabajador.cargo,
                tipo: nuevoTrabajador.tipo,
                localidad: nuevoTrabajador.localidad,
                empresaId: nuevoTrabajador.empresaId
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error al agregar trabajador: ${errorData.message || "Desconocido"}`);
        }

        const trabajadorGuardado = await response.json();
        console.log("✅ Trabajador agregado correctamente", trabajadorGuardado);

        // ✅ Llamamos a obtenerTrabajadores para actualizar la lista
        await this.obtenerTrabajadores();

        // ✅ Cerramos el formulario después de agregar
        this.mostrarFormulario = false;

    } catch (error) {
        console.error("❌ Error al agregar trabajador:", error);
    }
},


async eliminarTrabajador(id) {
  const resultado = await Swal.fire({
    title: "¿Estás seguro?",
    text: "Esta acción eliminará permanentemente al trabajador.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar"
  });

  if (!resultado.isConfirmed) {
    return; // Si el usuario cancela, no hacemos nada
  }

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

  if (!token) {
    Swal.fire("Error", "No tienes autorización. Inicia sesión nuevamente.", "error");
    this.$router.push("/"); // Redirige al login si no hay token
    return;
  }

  try {
    const response = await fetch(`http://localhost:5000/trabajadores/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Error al eliminar trabajador: ${errorData.message || "Desconocido"}`);
    }

    console.log("✅ Trabajador eliminado correctamente");

    // Mostrar mensaje de éxito
    Swal.fire("Eliminado", "El trabajador ha sido eliminado correctamente.", "success");

    // ✅ Actualizamos la lista de trabajadores
    await this.obtenerTrabajadores();

  } catch (error) {
    console.error("❌ Error al eliminar trabajador:", error);
    Swal.fire("Error", "Hubo un problema al eliminar el trabajador.", "error");
  }
},


editarTrabajador(trabajador) {
    this.trabajadorEditado = { ...trabajador }; // Pasamos el trabajador al formulario
    this.mostrarFormulario = true;
  },
  cerrarFormulario() {
    this.trabajadorEditado = null; // Resetea el formulario cuando se cierra
    this.mostrarFormulario = false;
  },


async guardarEdicionTrabajador(trabajadorEditado) {
  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

  if (!token) {
    alert("No tienes autorización. Inicia sesión nuevamente.");
    this.$router.push("/"); // Redirige al login si no hay token
    return;
  }

  try {
    const response = await fetch(`http://localhost:5000/trabajadores/${trabajadorEditado.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        nombre: trabajadorEditado.nombre,
        apellido: trabajadorEditado.apellido,
        rut: trabajadorEditado.rut,
        cargo: trabajadorEditado.cargo,
        tipo: trabajadorEditado.tipo,
        localidad: trabajadorEditado.localidad,
        empresaId: trabajadorEditado.empresaId
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Error al editar trabajador: ${errorData.message || "Desconocido"}`);
    }

    const trabajadorActualizado = await response.json();
    console.log("✅ Trabajador editado correctamente", trabajadorActualizado);

    // ✅ Llamamos a obtenerTrabajadores para actualizar la lista
    await this.obtenerTrabajadores();

    // ✅ Cerramos el formulario después de editar
    this.mostrarFormulario = false;

  } catch (error) {
    console.error("❌ Error al editar trabajador:", error);
  }
},

async obtenerTrabajadores() {
    this.error = null;
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

    if (!token) {
        console.error("❌ No se encontró token de autenticación");
        return;
    }

    console.log("📌 Token enviado:", token);

    try {
        const response = await fetch("http://localhost:5000/trabajadores", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`❌ Error en la solicitud: ${response.status} - ${errorData.error || "Error desconocido"}`);
        }

        const data = await response.json();
        console.log("✅ Trabajadores obtenidos:", data);
        this.trabajadores = data;

    } catch (err) {
        console.error("❌ Error al obtener trabajadores:", err);
        this.error = err.message;
    }
},
verDocumentos(id) {
    sessionStorage.setItem("trabajador_id", id); // Guarda el ID temporalmente
    this.$router.push("/documentos");
  },
async obtenerEmpresas() {
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

    if (!token) {
        console.error("❌ No se encontró token de autenticación");
        return;
    }

    try {
        const response = await fetch("http://localhost:5000/empresas", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`❌ Error en la solicitud: ${response.status} - ${errorData.error || "Error desconocido"}`);
        }

        const data = await response.json();
        console.log("✅ Empresas obtenidas:", data);
        this.empresas = data; // Asigna las empresas a la variable en data()

    } catch (err) {
        console.error("❌ Error al obtener empresas:", err);
    }
    
},

},

// Cuando el componente carga, obtiene los trabajadores


created() {
    this.obtenerTrabajadores();
    this.obtenerEmpresas();
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


.editar { background-color: #ffc107; color: black; }
.eliminar { background-color: #ee0000; color: white; }

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
