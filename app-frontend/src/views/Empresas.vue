<template>
    <div class="app-container">
        <Sidebar />
        <div class="empresas-container">
            <h1>Lista de Empresas</h1>

            <!-- Barra de búsqueda -->
            <input type="text" v-model="busqueda" placeholder="Buscar empresa..." class="barra-busqueda" />

            <button class="boton agregar" @click="mostrarModalAgregar = true">➕ Agregar Empresa</button>

            <table class="tabla-empresas">
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Trabajadores Activos</th>
                        <th>Documentos Requeridos</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="empresa in empresasFiltradas" :key="empresa.id">
                        <td>{{ empresa.nombre }}</td>
                        <td @click="verTrabajadores(empresa)">{{ empresa.trabajadores_activos }}</td>
                        <td>
                            <button class="config-docs" @click="configurarDocumentos(empresa)">📄 Configurar</button>
                        </td>
                        <td>
                            <button class="eliminar" @click="eliminarEmpresa(empresa)">❌ Eliminar</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal Agregar Empresa -->
        <div v-if="mostrarModalAgregar" class="modal-overlay">
            <div class="modal">
                <h2>Agregar Empresa</h2>
                <input type="text" v-model="nuevaEmpresa" placeholder="Nombre de la empresa" />
                <button class="boton guardar" @click="agregarEmpresa">✅ Guardar</button>
                <button class="cerrar-modal" @click="mostrarModalAgregar = false">❌ Cerrar</button>
            </div>
        </div>

        <!-- Modal Configurar Documentos -->
        <div v-if="mostrarModalConfigurar" class="modal-overlay">
            <div class="modal">
                <h2>Configurar Documentos para {{ empresaSeleccionada.nombre }}</h2>

                <!-- Botones para Editar y Agregar Requisitos -->
                <button class="editar" @click="editarDocumentos = !editarDocumentos">✏️ Editar</button>
                <button class="boton agregar-requisito" @click="mostrarFormularioAgregar = true">➕ Agregar Requisito</button>

                <!-- Formulario de Agregar Requisito -->
                <div v-if="mostrarFormularioAgregar">
                    <input type="text" v-model="nuevoDocumento.nombre" placeholder="Nombre del documento" />
                    <select v-model="nuevoDocumento.categoria">
                        <option disabled value="">Seleccione una categoría</option>
                        <option>Personal</option>
                        <option>Licencias</option>
                        <option>Certificaciones</option>
                    </select>
                    <button class="boton agregar-doc" @click="agregarRequisito">➕ Guardar</button>
                </div>

                <!-- Lista de Requisitos -->
                <ul v-if="empresaSeleccionada.requisitos && empresaSeleccionada.requisitos.length > 0">
    <li v-for="(doc, index) in empresaSeleccionada.requisitos" :key="index">
        📄 {{ doc.nombre_requisito }} - {{ doc.categoria }}
        <button v-if="editarDocumentos" class="eliminar" @click="eliminarRequisito(index)">❌</button>
    </li>
</ul>

<!-- 🔹 Mensaje cuando no hay requisitos -->
<p v-else>No hay requisitos configurados aún.</p>


                <button class="boton guardar-cambios" @click="guardarCambios">💾 Guardar Cambios</button>
                <button class="cerrar-modal" @click="mostrarModalConfigurar = false">❌ Cerrar</button>
            </div>
        </div>
    </div>
</template>
  

<script>
import Sidebar from "@/components/Sidebar.vue";
import Swal from "sweetalert2";

export default {
  components: { Sidebar },
  data() {
      return {
        empresas: [],
        busqueda: "",
        mostrarModalAgregar: false,
        nuevaEmpresa: "",
        mostrarModalConfigurar: false,
        empresaSeleccionada: {},
        editarDocumentos: false,  // 🔹 Solo controla botones de edición y eliminación
        mostrarFormularioAgregar: false,  // 🔹 Solo controla el formulario
        nuevoDocumento: { nombre: "", categoria: "" }
      };
  },
  computed: {
      empresasFiltradas() {
          return this.empresas.filter(empresa =>
              empresa.nombre.toLowerCase().includes(this.busqueda.toLowerCase())
          );
      }
  },
  methods: {
      async obtenerEmpresas() {
          const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
          if (!token) return;
          try {
              const response = await fetch("http://localhost:5000/empresas", {
                  method: "GET",
                  headers: { "Authorization": `Bearer ${token}` }
              });
              if (!response.ok) throw new Error("Error al obtener empresas");
              this.empresas = await response.json();
          } catch (error) {
              console.error("❌ Error al obtener empresas:", error);
          }
      },
      async obtenerRequisitos(empresa) {
    this.empresaSeleccionada = { ...empresa };
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch(`http://localhost:5000/empresas/${empresa.id}/requisitos`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Error al obtener requisitos");

        const data = await response.json();
        console.log("📥 Requisitos recibidos:", data);  // Debugging

        // 🔹 Asegurar que `requisitos` siempre sea un array válido
        this.empresaSeleccionada.requisitos = Array.isArray(data) ? data : [];

        this.mostrarModalConfigurar = true;
    } catch (error) {
        console.error("❌ Error al obtener requisitos:", error);
    }
},




async agregarRequisito() {
    if (!this.nuevoDocumento.nombre.trim() || !this.nuevoDocumento.categoria) return;
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch(`http://localhost:5000/empresas/${this.empresaSeleccionada.id}/requisitos`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nombre_requisito: this.nuevoDocumento.nombre,
                categoria: this.nuevoDocumento.categoria
            })
        });

        if (!response.ok) throw new Error("Error al agregar requisito");

        // ✅ Volver a obtener los requisitos desde el backend para actualizar la lista en la UI
        await this.obtenerRequisitos(this.empresaSeleccionada);

        Swal.fire("✅ Agregado", "Requisito agregado correctamente", "success");

        // ✅ Limpiar el formulario
        this.nuevoDocumento = { nombre: "", categoria: "" };

    } catch (error) {
        console.error("❌ Error al agregar requisito:", error);
        Swal.fire("❌ Error", "No se pudo agregar el requisito", "error");
    }
},



    async eliminarRequisito(id, index) {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (!token) return;

        try {
            const response = await fetch(`http://localhost:5000/requisitos/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("Error al eliminar requisito");

            this.empresaSeleccionada.requisitos.splice(index, 1);
            Swal.fire("✅ Eliminado", "Requisito eliminado correctamente", "success");

        } catch (error) {
            console.error("❌ Error al eliminar requisito:", error);
        }
    },

    async configurarDocumentos(empresa) {
    await this.obtenerRequisitos(empresa);
    this.mostrarModalConfigurar = true;
},


      agregarDocumento() {
    if (!this.nuevoDocumento.nombre.trim() || !this.nuevoDocumento.categoria) return;

    // 🔹 Verificamos que `requisitos` esté definido
    if (!this.empresaSeleccionada.requisitos) {
        this.empresaSeleccionada.requisitos = []; // Inicializar si no existe
    }

    this.empresaSeleccionada.requisitos.push({ ...this.nuevoDocumento });
    this.nuevoDocumento = { nombre: "", categoria: "" };
    this.mostrarFormularioAgregar = false; // Oculta el formulario después de agregar
},


      eliminarDocumento(index) {
          this.empresaSeleccionada.documentos.splice(index, 1);
      },
      async eliminarEmpresa(empresa) {
          if (empresa.trabajadores_activos > 0) {
              Swal.fire("Error", "No puedes eliminar una empresa con trabajadores activos", "error");
              return;
          }
          const confirmacion = await Swal.fire({
              title: "¿Eliminar empresa?",
              text: "Esta acción es irreversible",
              icon: "warning",
              showCancelButton: true,
              confirmButtonText: "Sí, eliminar",
              cancelButtonText: "Cancelar"
          });
          if (confirmacion.isConfirmed) {
              this.empresas = this.empresas.filter(e => e !== empresa);
              Swal.fire("Eliminado", "La empresa ha sido eliminada", "success");
          }
      },
      async guardarCambios() {
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch(`http://localhost:5000/empresas/${this.empresaSeleccionada.id}/requisitos`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ requisitos: this.empresaSeleccionada.requisitos })
        });

        if (!response.ok) throw new Error("Error al guardar requisitos");

        Swal.fire("✅ Guardado", "Todos los requisitos se han guardado correctamente", "success");

        // 🔹 Volver a obtener los requisitos desde el backend para asegurarse de que están actualizados
        await this.obtenerRequisitos(this.empresaSeleccionada);

        this.mostrarModalConfigurar = false;

    } catch (error) {
        console.error("❌ Error al guardar requisitos:", error);
        Swal.fire("❌ Error", "No se pudieron guardar los requisitos", "error");
    }
}


  },
  created() {
      this.obtenerEmpresas();
  }
};
</script>

<style scoped>
/* Estilo base */
.app-container {
    display: flex;
    height: 100vh;
    background: #f3f3f3;
}
.empresas-container {
  flex: 1;
  padding: 40px;
  text-align: center;
  color: black;
  width: 1462px;
  margin: 20px;
}

.titulo {
  margin-bottom: 20px;
}
/* Estilo de la barra de búsqueda */
.barra-busqueda {
    padding: 10px;
    width: 50%;
    margin-top: 20px;
    margin-bottom: 35px;
    border: 1px solid #ccc;
    border-radius: 8px;
}

/* Diseño mejorado de botones */
.boton {
    padding: 10px 15px;
    margin: 5px;
    border: none;
    cursor: pointer;
    border-radius: 8px;
    font-weight: bold;
    transition: background 0.3s ease, transform 0.2s ease;
    box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.15);
}

.boton:hover {
    transform: scale(1.05);
}

.tabla-empresas {
    width: 100%;
    border-collapse: collapse;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tabla-empresas th, 
.tabla-empresas td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

.agregar { background: #28a745; color: white; }
.eliminar { 
  background: #ff6961; 
  color: white; 
  border-radius: 8px; 
  border: none; 
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.15); 
  padding: 5px 10px; 
  margin-right: 10px; /* Agrega distancia entre botones */
  margin-top: 5px;
}

.config-docs { 
  background: #134b91; 
  color: white; 
  border-radius: 8px; 
  border: none; 
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.15); 
  padding: 5px 10px; 
  margin-top: 5px;
}
.editar { background: white; color: black; }

/* Modales mejorados */
.modal {
    background: rgb(255, 255, 255);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    max-width: 500px;
    width: 100%;
    color:black;
}

.modal input,
.modal select {
    width: 90%;
    padding: 10px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
}

/* Mejor estilo para la lista de documentos */
ul {
    list-style: none;
    padding: 0;
}

ul li {
    padding: 10px;
    background: #f9f9f9;
    border-radius: 8px;
    margin: 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

ul li button {
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
}

/* Modal de fondo */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
