<template>
  <div class="app-container">
    <Sidebar />
    <div class="content">
      <div class="header">
        <button class="boton volver" @click="$router.push('/trabajadores')">⬅ Volver</button>
        <h1 class="titulo">📂 Documentos de {{ trabajador ? trabajador.nombre : 'Cargando...' }}</h1>
      </div>
      
      <!-- Categorías de documentos -->
      <div class="categorias">
  <button
    v-for="categoria in categorias"
    :key="categoria"
    @click="seleccionarCategoria(categoria)"
    :class="{ activo: categoriaSeleccionada === categoria }"
    class="boton-categoria"
  >
    {{ categoria }}
  </button>
</div>


<input type="text" v-model="busqueda" @input="filtrarDocumentos" placeholder="Buscar documento..." class="barra-busqueda" />

<!-- Listado de documentos -->
      <div class="tabla-container">
        <table class="tabla-documentos">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Fecha de Vencimiento</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="documento in documentosFiltrados" :key="documento.id">
              <td>{{ documento.nombre_archivo }}</td>
              <td>{{ documento.categoria }}</td>
              <td>{{ formatearFecha(documento.fecha_vencimiento) }}</td>

              <td>
                  <button class="boton-descargar" @click="descargarDocumento(documento)">⬇ Descargar</button>
                  <button class="boton-eliminar" @click="eliminarDocumento(documento.id)">🗑 Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Botones para abrir modales -->
      <div class="acciones">
        <button class="boton abrir-modal" @click="mostrarModalSubir = true">📤 Subir Documento</button>
        <button class="boton abrir-modal" @click="mostrarModalHabilitar = true">✅ Habilitar Trabajador</button>
      </div>

      <!-- Modal Subir Documento -->
      <div v-if="mostrarModalSubir" class="modal-overlay">
        <div class="modal">
          <h2>Subir Documento</h2>
          <input type="file" @change="seleccionarArchivo" class="input-archivo" accept=".jpg, .png, .pdf"/>
          <input type="date" v-model="fechaVencimiento" class="input-fecha" required />
          <select v-model="categoriaSeleccionada" class="select-categoria" required>
            <option disabled value="">Seleccione una categoría</option>
            <option v-for="categoria in categorias" :key="categoria">{{ categoria }}</option>
          </select>
          <button class="boton subir" @click="subirDocumento">📤 Subir Documento</button>
          <button class="boton cerrar-modal" @click="mostrarModalSubir = false">❌ Cerrar</button>
        </div>
      </div>
      
      <!-- Modal Habilitar Trabajador -->
      <div v-if="mostrarModalHabilitar" class="modal-overlay">
        <div class="modal">
          <h2>Habilitar Trabajador</h2>
          <select v-model="empresaSeleccionada" class="select-empresa">
            <option disabled value="">Seleccione una empresa</option>
            <option v-for="empresa in empresas" :key="empresa.id">{{ empresa.nombre }}</option>
          </select>
          <button class="boton habilitar" @click="habilitarTrabajador">📦 Generar .rar</button>
          <button class="boton cerrar-modal" @click="mostrarModalHabilitar = false">❌ Cerrar</button>
        </div>
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
      documentos: [],
      busqueda: "",
      trabajador: null,
      categorias: ["Personal", "Licencias", "Certificaciones"],
      categoriaSeleccionada: "",
      fechaVencimiento: "",
      archivoSeleccionado: null,
      empresas: [],
      empresaSeleccionada: "",
      mostrarModalSubir: false,
      mostrarModalHabilitar: false,
      busquedaDocumento: "",
    };
  },
  computed: {


    documentosFiltrados() {
        return this.documentos.filter(doc => {
            const coincideCategoria =
                !this.categoriaSeleccionada || doc.categoria === this.categoriaSeleccionada;
            const coincideBusqueda =
                !this.busqueda || doc.nombre_archivo.toLowerCase().includes(this.busqueda.toLowerCase());

            return coincideCategoria && coincideBusqueda;
        });
    }


  },
  methods: {
    async obtenerTrabajador() {
      this.trabajador_id = sessionStorage.getItem("trabajador_id");
      if (!this.trabajador_id) return;
      
      const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) return;
      this.trabajador = await response.json();
    },
    async obtenerDocumentos() {
      const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch(`http://localhost:5000/documentos?trabajador_id=${this.trabajador_id}`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) return;
      this.documentos = await response.json();
    },

    async subirDocumento() {
  if (!this.archivoSeleccionado || !this.fechaVencimiento || !this.categoriaSeleccionada) {
    Swal.fire("⚠️ Error", "Todos los campos son obligatorios.", "error");
    return;
  }

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    Swal.fire("⚠️ Error", "No tienes autorización. Inicia sesión nuevamente.", "error");
    this.$router.push("/login");
    return;
  }

  const formData = new FormData();
  formData.append("archivo", this.archivoSeleccionado);
  formData.append("nombre_archivo", this.archivoSeleccionado.name);
  formData.append("categoria", this.categoriaSeleccionada);
  formData.append("fecha_vencimiento", this.fechaVencimiento);

  try {
    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}/documentos`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`  // 🔹 Importante: Sin `Content-Type` porque es FormData
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Error al subir el documento.");
    }

    Swal.fire("✅ Éxito", "Documento subido correctamente.", "success");
    this.obtenerDocumentos();
    this.mostrarModalSubir = false; // 🔹 Cerrar modal después de subir el documento
  } catch (error) {
    console.error("❌ Error al subir documento:", error);
    Swal.fire("⚠️ Error", error.message, "error");
  }
},

seleccionarArchivo(event) {
    this.archivoSeleccionado = event.target.files[0];
    console.log("📂 Archivo seleccionado:", this.archivoSeleccionado);
  },

    esVencido(fecha) {
    if (!fecha) return false; // Si no hay fecha, no se considera vencido
    const fechaVencimiento = new Date(fecha);
    const hoy = new Date();
    return fechaVencimiento < hoy;
  },
  async descargarDocumento(documento) {
  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    alert("No tienes autorización. Inicia sesión nuevamente.");
    this.$router.push("/");
    return;
  }

  try {
    const response = await fetch(`http://localhost:5000/documentos/${documento.id}/descargar`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error("Error al descargar el documento.");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = documento.nombre_archivo;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("❌ Error al descargar documento:", error);
    alert("❌ Hubo un problema al descargar el documento.");
  }
},
async eliminarDocumento(documentoId) {
  const confirmacion = await Swal.fire({
    title: "¿Estás seguro?",
    text: "Esta eliminación es irreversible, no se podrá recuperar el documento.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar"
  });

  if (!confirmacion.isConfirmed) return;

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    alert("No tienes autorización. Inicia sesión nuevamente.");
    this.$router.push("/");
    return;
  }

  try {
    const response = await fetch(`http://localhost:5000/documentos/${documentoId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error("Error al eliminar el documento.");

    Swal.fire("Eliminado", "El documento ha sido eliminado con éxito.", "success");
    this.obtenerDocumentos(); // Recargar la lista de documentos
  } catch (error) {
    console.error("❌ Error al eliminar documento:", error);
    Swal.fire("Error", "Hubo un problema al eliminar el documento.", "error");
  }
},
seleccionarCategoria(categoria) {
    if (this.categoriaSeleccionada === categoria) {
      this.categoriaSeleccionada = ""; // 🔄 Si ya está seleccionada, la deselecciona
    } else {
      this.categoriaSeleccionada = categoria; // ✅ Selecciona la nueva categoría
    }
  },
  async obtenerEmpresas() {
    try {
      const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
      if (!token) {
        console.error("❌ No se encontró token de autenticación");
        return;
      }

      const response = await fetch("http://localhost:5000/empresas", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) throw new Error("Error al obtener empresas.");

      this.empresas = await response.json();
    } catch (error) {
      console.error("❌ Error al obtener empresas:", error);
    }
  },
  filtrarDocumentos() {
          this.documentosFiltrados = this.documentos.filter(doc =>
              doc.nombre_archivo.toLowerCase().includes(this.busqueda.toLowerCase())
          );
      },
      formatearFecha(fecha) {
          const fechaObj = new Date(fecha);
          return fechaObj.toLocaleDateString("es-ES", {
              day: "2-digit",
              month: "2-digit",
              year: "numeric"
          });
      },
      async habilitarTrabajador() {
  if (!this.empresaSeleccionada) {
    Swal.fire("⚠️ Error", "Debes seleccionar una empresa.", "error");
    return;
  }

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    Swal.fire("⚠️ Error", "No tienes autorización. Inicia sesión nuevamente.", "error");
    this.$router.push("/login");
    return;
  }

  try {
    console.log("📦 Enviando petición para generar .rar...");
    
    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}/generar-rar`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ empresa_id: this.empresaSeleccionada })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Error al generar el .rar.");
    }

    // Descargar el archivo .rar generado
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Trabajador_${this.trabajador_id}.rar`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    Swal.fire("✅ Éxito", "El archivo .rar se ha generado correctamente.", "success");
    this.mostrarModalHabilitar = false; // Cerrar modal después de la acción
  } catch (error) {
    console.error("❌ Error al generar .rar:", error);
    Swal.fire("⚠️ Error", error.message, "error");
  }
}


  },
  created() {
    this.obtenerTrabajador();
    this.obtenerDocumentos();
    this.obtenerEmpresas();
  }
};
</script>


<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5; /* Fondo gris claro para el contenedor principal */
  font-family: 'Roboto', sans-serif; /* Tipografía moderna */
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  border-radius: 12px; /* Bordes redondeados */
  margin: 20px;
  overflow-y: auto;
  width: 1422px
  ;}

.header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px; /* Más espacio debajo del header */
}

.titulo {
  font-size: 2rem;
  font-weight: bold;
  color: #134b91; /* Color azul oscuro para el título */
  margin: 0; /* Eliminar margen predeterminado */
  text-align: center; /* Centrar el texto */
  width: 100%; /* Asegurar que el título ocupe todo el ancho disponible */
  margin-right: 90px;
}

.categorias {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.categorias button {
  background: #e9ecef; /* Fondo gris claro */
  color: #495057; /* Texto oscuro */
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
  font-size: 1rem;
  font-weight: bold;
}

.categorias button.activo {
  background: #134b91; /* Azul oscuro cuando está activo */
  color: white;
  transform: scale(1.05);
}

.boton-categoria:hover {
  background: #d6d8db; /* Un tono más oscuro al pasar el mouse */
}
.tabla-container {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 20px;
}

.tabla-documentos {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  color: black
}

.tabla-documentos th,
.tabla-documentos td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.tabla-documentos th {
  background: #134b91;
  color: white;
  font-weight: bold;
}

.tabla-documentos td.vencido {
  color: #dc3545; /* Color rojo para fechas vencidas */
}

.acciones {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.boton {
  background: #28a745; /* Color verde para botones principales */
  color: white;
  padding: 12px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.boton-descargar {
  background: #28a745; /* Color verde para botones principales */
  color: white;
  padding: 11px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.boton-eliminar {
  background: #28a745; /* Color verde para botones principales */
  color: white;
  padding: 11px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
  margin-left: 10px;
}

.boton.volver {
  background: #007bff; /* Color azul para botón "Volver" */
  padding: 8px 12px; /* Tamaño más pequeño */
  font-size: 0.875rem; /* Tamaño de fuente más pequeño */
  width: 90px; /* Ancho automático */
}

.boton.cerrar-modal {
  background: #dc3545; /* Color rojo para botón "Cerrar" */
}

.boton:hover {
  opacity: 0.9; /* Efecto hover sutil */
}

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

.modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.input-archivo,
.input-fecha,
.select-categoria,
.select-empresa {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
}

.documentos-container {
    padding: 20px;
    text-align: center;
}

.barra-busqueda {
    width: 50%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
}

.tabla-container {
    width: 100%;
    overflow-x: auto;
}

.tabla-documentos {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.tabla-documentos th,
.tabla-documentos td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
    color: black;
}

.tabla-documentos th {
    background: #134b91;
    color: white;
}

.nombre-documento {
    font-size: 1.1rem;
    font-weight: bold;
    color: #134b91;
}

</style>