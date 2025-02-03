<template>
    <div class="documentos-container">
      <h1 class="titulo">📂 Documentos de {{ trabajador ? trabajador.nombre : 'Cargando...' }}</h1>
      
      <!-- Categorías de documentos -->
      <div class="categorias">
        <button v-for="categoria in categorias" :key="categoria" @click="filtrarCategoria(categoria)" :class="{ activo: categoriaSeleccionada === categoria }">
          {{ categoria }}
        </button>
      </div>
      
      <!-- Listado de documentos -->
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
            <td>{{ documento.nombre }}</td>
            <td>{{ documento.categoria }}</td>
            <td :class="{ vencido: esVencido(documento.fecha_vencimiento) }">
              {{ documento.fecha_vencimiento }}
            </td>
            <td>
              <button class="boton descargar" @click="descargarDocumento(documento)">⬇ Descargar</button>
              <button class="boton eliminar" @click="eliminarDocumento(documento.id)">🗑 Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Subir nuevo documento -->
      <div class="subir-documento">
        <input type="file" @change="seleccionarArchivo" class="input-archivo" />
        <input type="date" v-model="fechaVencimiento" class="input-fecha" required />
        <select v-model="categoriaSeleccionada" class="select-categoria" required>
          <option disabled value="">Seleccione una categoría</option>
          <option v-for="categoria in categorias" :key="categoria">{{ categoria }}</option>
        </select>
        <button class="boton subir" @click="subirDocumento">📤 Subir Documento</button>
      </div>
      
      <!-- Botón de habilitación -->
      <div class="habilitacion">
        <h3 class="titulo-habilitar">✅ Habilitar Trabajador</h3>
        <select v-model="empresaSeleccionada" class="select-empresa">
          <option disabled value="">Seleccione una empresa</option>
          <option v-for="empresa in empresas" :key="empresa.id">{{ empresa.nombre }}</option>
        </select>
        <button class="boton habilitar" @click="habilitarTrabajador">📦 Generar .rar</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: ["id"],
    data() {
      return {
        documentos: [],
        trabajador: null,
        categorias: ["Personal", "Licencias", "Certificaciones"],
        categoriaSeleccionada: "",
        fechaVencimiento: "",
        archivoSeleccionado: null,
        empresas: [],
        empresaSeleccionada: "",
      };
    },
    computed: {
      documentosFiltrados() {
        return this.documentos.filter(doc => this.categoriaSeleccionada === "" || doc.categoria === this.categoriaSeleccionada);
      }
    },
    methods: {

        async subirDocumento() {
  if (!this.archivoSeleccionado || !this.fechaVencimiento || !this.categoriaSeleccionada) {
    alert("Por favor, completa todos los campos antes de subir el documento.");
    return;
  }

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    alert("No tienes autorización. Inicia sesión nuevamente.");
    this.$router.push("/");
    return;
  }

  const formData = new FormData();
  formData.append("archivo", this.archivoSeleccionado);
  formData.append ("nombre_archivo", this.archivoSeleccionado.name);
  formData.append("trabajador_id", this.trabajador_id);
  formData.append("categoria", this.categoriaSeleccionada);
  formData.append("fecha_vencimiento", this.fechaVencimiento);

  try {
    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}/documentos`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      },
      body: formData,
    });

    if (!response.ok) throw new Error("Error al subir el documento.");

    alert("✅ Documento subido correctamente.");
    this.obtenerDocumentos(); // Recargar la lista de documentos
  } catch (error) {
    console.error("❌ Error al subir documento:", error);
    alert("❌ Hubo un problema al subir el documento.");
  }
},

        async obtenerTrabajador() {
  try {
    this.trabajador_id = sessionStorage.getItem("trabajador_id");
    if (!this.trabajador_id) {
      console.error("⚠ No se encontró trabajador_id en sessionStorage");
      return;
    }

    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) {
      console.error("❌ No se encontró token de autenticación");
      return;
    }

    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,  // ✅ Se agrega el token aquí
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) throw new Error("Error al obtener el trabajador.");
    this.trabajador = await response.json();
  } catch (error) {
    console.error("❌ Error al obtener trabajador:", error);
  }
},

async obtenerDocumentos() {
  try {
    if (!this.trabajador_id) return;

    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) {
      console.error("❌ No se encontró token de autenticación");
      return;
    }

    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador_id}/documentos`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,  // ✅ Se agrega el token aquí
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) throw new Error("Error al obtener documentos.");
    this.documentos = await response.json();
  } catch (error) {
    console.error("❌ Error al obtener documentos:", error);
  }
},

      seleccionarArchivo(event) {
        this.archivoSeleccionado = event.target.files[0];
      },
      esVencido(fecha) {
        return new Date(fecha) < new Date();
      }
    },
    created() {
      this.obtenerTrabajador();
      this.obtenerDocumentos();
    }
  };
  </script>
  
  <style scoped>
  .documentos-container {
    padding: 20px;
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 60%;
    margin: auto;
    text-align: center;
  }
  .titulo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #134b91;
  }
  .categorias button {
    margin: 5px;
    padding: 10px;
    border: none;
    background: #ddd;
    cursor: pointer;
    border-radius: 5px;
  }
  .categorias .activo {
    background: #134b91;
    color: white;
  }
  .tabla-documentos {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  th, td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
  }
  .vencido {
    color: red;
    font-weight: bold;
  }
  .subir-documento, .habilitacion {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
  }
  .boton {
    background: #28a745;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  .boton:hover {
    background: #218838;
  }
  .input-archivo, .input-fecha, .select-categoria, .select-empresa {
    padding: 8px;
    border-radius: 5px;
    border: 1px solid #ddd;
  }
  </style>
