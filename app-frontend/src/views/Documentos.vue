<template>
  <div class="app-container">
    <Sidebar />
    <div class="content">
      <div class="header">
        <button class="boton volver" @click="$router.push('/trabajadores')">⬅ Volver</button>
        <h1 class="titulo">📂 Documentos de {{ trabajador ? trabajador.nombre.split(' ')[0] + ' ' + trabajador.apellido.split(' ')[0] : 'Cargando...' }}</h1>
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

      <!-- Botón para abrir modal de subir documento -->
      <button class="boton abrir-modal" @click="mostrarModalSubir = true">📤 Subir Documento</button>

      <!-- Modal Subir Documento -->
      <div v-if="mostrarModalSubir" class="modal-overlay">
        <div class="modal">
          <h2>Subir Documento</h2>
          <h3>Seleccione un tipo de documento:</h3>
          <div class="tipo-documentos-lista">
            <button 
            v-for="tipo in tiposDocumentos" 
            :key="tipo" 
            @click="abrirModalCargarDocumento(tipo)"
            :class="{ 'subido': documentosSubidosEstado[tipo] }"
            class="tipo-documento-boton"
            >
            {{ tipo }} 
            <span v-if="documentosSubidosEstado[tipo]" class="tick-verde">✔</span>
            </button>

          </div>
          <button class="boton cerrar-modal" @click="mostrarModalSubir = false">❌ Cerrar</button>
        </div>
      </div>

      <!-- Modal para Cargar Documento dentro del modal principal -->
      <div v-if="mostrarModalCargar" class="modal-overlay">
        <div class="modal">
          <h2>{{ documentosSubidos.includes(tipoDocumentoSeleccionado) ? 'Reemplazar' : 'Subir' }} Documento - {{ tipoDocumentoSeleccionado }}</h2>
          <input type="file" @change="seleccionarArchivo" class="input-archivo" accept=".jpg, .png, .pdf"/>
          <input type="date" v-model="fechaVencimiento" class="input-fecha" required />
          <select v-model="categoriaSeleccionada" class="select-categoria">
            <option disabled value="">Seleccione una categoría</option>
            <option v-for="categoria in categorias" :key="categoria">{{ categoria }}</option>
          </select>
          <button class="boton subir" @click="subirDocumento">📤 {{ documentosSubidos.includes(tipoDocumentoSeleccionado) ? 'Reemplazar' : 'Subir' }} Documento</button>
          <button class="boton cerrar-modal" @click="cerrarModalCargarDocumento">❌ Cerrar</button>
        </div>
      </div>
      <button class="boton habilitar" @click="mostrarModalHabilitar = true
      "> Habilitar trabajador</button>
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
      trabajadorSeleccionado:"",
      mostrarModalSubir: false,
      mostrarModalHabilitar: false,
      busquedaDocumento: "",
      tiposDocumentos: [],  // Lista de tipos de documentos
      documentosRequeridos: [],
      documentosSubidos: [],
      documentosFaltantes: [],
      mostrarModalCargar: false,
      tipoDocumentoSeleccionado: '',
      documentoSeleccionado: null,
      empresaSeleccionada: "",
    };
  },
  watch: {
    empresaSeleccionada(newEmpresa) {
      if (!newEmpresa) {
        console.log("⚠️ No hay empresa seleccionada.");
        this.tiposDocumentos = [];
        return;
      }

      console.log("🏢 Empresa seleccionada:", newEmpresa);

      // Verificar que la lista de empresas ya está cargada
      if (!this.empresas.length) {
        console.log("⚠️ Empresas aún no cargadas, esperando...");
        return;
      }

      const empresa = this.empresas.find(emp => emp.id === newEmpresa);
      console.log("🔍 Empresa encontrada:", empresa);

      if (empresa) {
        console.log("📋 Requisitos de la empresa:", empresa.requisitos);

        if (empresa.requisitos && empresa.requisitos.length > 0) {
          this.tiposDocumentos = empresa.requisitos.map(req => req.nombre_requisito);
        } else {
          console.log("⚠️ La empresa no tiene requisitos asignados.");
          this.tiposDocumentos = [];
        }
      } else {
        console.log("❌ No se encontró la empresa en la lista.");
        this.tiposDocumentos = [];
      }
    }
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
    },
     
    documentosSubidosEstado() {
    console.log("🔄 Verificando documentos subidos en el modal...", this.documentos);

    return this.tiposDocumentos.reduce((estado, tipo) => {
      const tipoNormalizado = tipo.trim().toLowerCase(); // Normalizamos el tipo de documento

      estado[tipo] = this.documentos.some(doc => {
        if (!doc.nombre_archivo) {
          console.warn("⚠️ Documento sin nombre encontrado:", doc);
          return false;
        }

        // 🔹 Extraer el tipo de documento desde el nombre del archivo
        const tipoExtraido = doc.nombre_archivo.split(" - ")[0]?.trim().toLowerCase();

        return tipoExtraido === tipoNormalizado;
      });

      return estado;
    }, {});
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
      this.trabajadorSeleccionado = this.trabajador; // Guardar el trabajador seleccionado
    },
    async obtenerDocumentos() {
  try {
    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    const response = await fetch(`http://localhost:5000/documentos?trabajador_id=${this.trabajador_id}`, {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) throw new Error("Error obteniendo documentos");

    this.documentos = await response.json(); // 🔄 Se actualiza la lista de documentos
    console.log("📂 Documentos actualizados:", this.documentos);
  } catch (error) {
    console.error("❌ Error al obtener documentos:", error);
  }
},


    async subirDocumento() {
  if (!this.archivoSeleccionado || !this.fechaVencimiento || !this.tipoDocumentoSeleccionado) {
    Swal.fire("⚠️ Error", "Todos los campos son obligatorios.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("archivo", this.archivoSeleccionado);
  formData.append("fecha_vencimiento", this.fechaVencimiento);
  formData.append("tipo", this.tipoDocumentoSeleccionado);
  formData.append("categoria", this.categoriaSeleccionada);

  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  if (!token) {
    Swal.fire("⚠️ Error", "No tienes autorización.", "error");
    return;
  }

  try {
    const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajador.id}/documentos`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Error al subir documento.");
    }

    Swal.fire("✅ Éxito", "Documento subido correctamente.", "success");

    // 🔄 Recargar la lista de documentos para reflejar los cambios
    await this.obtenerDocumentos();
this.$forceUpdate(); // 🔄 Forzar actualización del estado reactivo

    // Cerrar modal después de éxito
    this.mostrarModalCargar = false;

    // Limpiar datos después de subir el documento
    this.archivoSeleccionado = null;
    this.fechaVencimiento = "";
    this.tipoDocumentoSeleccionado = "";

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
  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

  if (!token) {
    console.error("⚠️ No hay token disponible. Asegúrate de iniciar sesión.");
    return;
  }

  try {
    const response = await fetch("http://localhost:5000/empresas", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Error al obtener empresas");
    }

    const data = await response.json();
    console.log("✅ Empresas obtenidas:", data);

    this.empresas = data.map(emp => ({
      ...emp,
      requisitos: emp.requisitos || []
    }));

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
    if (!this.trabajadorSeleccionado || !this.trabajadorSeleccionado.id) {
        Swal.fire("❌ Error", "No hay trabajador seleccionado.", "error");
        return;
    }

    if (!this.empresaSeleccionada) {
        Swal.fire("❌ Error", "Debe seleccionar una empresa antes de continuar.", "error");
        return;
    }

    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    try {
        console.log(`📤 Enviando solicitud para generar .RAR: Trabajador ${this.trabajadorSeleccionado.id}, Empresa ${this.empresaSeleccionada}`);

        const response = await fetch(`http://localhost:5000/trabajadores/${this.trabajadorSeleccionado.id}/generar-rar`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ empresa_id: this.empresaSeleccionada })
        });

        if (!response.ok) {
            const errorData = await response.json();

            console.log("⚠️ Respuesta de error del backend:", errorData);

            // 📌 Verificar si el backend envió la lista de documentos faltantes
            if (errorData.faltantes && Array.isArray(errorData.faltantes) && errorData.faltantes.length > 0) {
                Swal.fire({
                    title: "⚠️ No se ha podido generar el .RAR",
                    html: `<p>Al trabajador le faltan los siguientes documentos para ser habilitado:</p>
                           <ul>${errorData.faltantes.map(doc => `<li>📄 ${doc}</li>`).join('')}</ul>`,
                    icon: "warning"
                });

                // 🔄 Volver a cargar los tipos de documentos para evitar que desaparezcan
                await this.actualizarTiposDocumentos();

                return;
            }

            throw new Error(errorData.error || "Error desconocido al generar el .RAR");
        }

        // 📦 Si todo está bien, proceder a descargar el archivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Documentos_${this.trabajadorSeleccionado.nombre}_${this.trabajadorSeleccionado.apellido}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        Swal.fire("✅ Generado", "El archivo .RAR se generó correctamente.", "success");

    } catch (error) {
        console.error("❌ Error al generar .rar:", error);
        Swal.fire("❌ Error", error.message, "error");

        // 🔄 Asegurar que los tipos de documentos siguen disponibles
        await this.actualizarTiposDocumentos();
    }
},




async obtenerTiposDocumentos() {
    try {
      const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch("http://localhost:5000/documentos/tipos", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) throw new Error("Error al obtener tipos de documentos");

      this.tiposDocumentos = await response.json();
    } catch (error) {
      console.error("❌ Error al obtener tipos de documentos:", error);
    }
  },
  async cargarDocumentosRequeridos() {
    if (!this.empresaSeleccionada) return;
    
    const response = await fetch(`http://localhost:5000/empresas/${this.empresaSeleccionada}/requisitos`);
    const data = await response.json();
    this.documentosRequeridos = data.map(req => req.nombre_requisito);
    
    this.documentosFaltantes = this.documentosRequeridos.filter(doc => !this.documentosSubidos.includes(doc));
  },
  async continuarHabilitacion() {
    if (!this.empresaSeleccionada) return;

    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch(
            `http://localhost:5000/trabajadores/${this.trabajador.id}/documentos-faltantes?empresa_id=${this.empresaSeleccionada}`,
            {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` },
            }
        );

        if (!response.ok) throw new Error("Error al obtener documentos faltantes");

        const data = await response.json();
        console.log("📥 Documentos faltantes recibidos:", data);

        this.documentosFaltantes = data.documentos;
    } catch (error) {
        console.error("❌ Error al obtener documentos faltantes:", error);
    }
},
async actualizarTiposDocumentos() {
    if (!this.empresaSeleccionada) {
        console.error("⚠️ No hay empresa seleccionada");
        return;
    }

    console.log("🔍 Volviendo a obtener requisitos para empresa:", this.empresaSeleccionada);

    const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (!token) {
        console.error("⚠️ No hay token de acceso disponible");
        return;
    }

    try {
        // 🔄 Obtener la empresa correcta
        const empresa = this.empresas.find(emp => emp.nombre === this.empresaSeleccionada);
        if (!empresa) {
            throw new Error("❌ No se encontró la empresa seleccionada en la lista.");
        }

        console.log("📋 Obteniendo requisitos de empresa ID:", empresa.id);

        // 🔄 Hacer la petición correcta con el ID en lugar del nombre
        const response = await fetch(`http://localhost:5000/empresas/${empresa.id}/requisitos`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Error al obtener requisitos");
        }

        const data = await response.json();
        console.log("✅ Requisitos obtenidos del backend:", data);

        this.tiposDocumentos = data.map(req => req.nombre_requisito);

        // 🔄 Forzar actualización de Vue para reflejar los cambios
        this.$nextTick(() => {
            this.$forceUpdate();
        });

    } catch (error) {
        console.error("❌ Error al obtener requisitos:", error);

        Swal.fire("⚠️ Error", "No se pudo obtener los tipos de documentos. Intenta nuevamente.", "error");
    }
},


abrirModalCargarDocumento(tipo) {
  this.tipoDocumentoSeleccionado = tipo;
  this.mostrarModalCargar = true;

  // 🔄 Forzar actualización para que Vue detecte cambios en documentosSubidosEstado
  this.$nextTick(() => {
    console.log("🔄 Actualizando estado de documentos en el modal...");
    this.$forceUpdate();
  });
},
    cargarDocumentosSubidos() {
      const documentosGuardados = JSON.parse(localStorage.getItem('documentosSubidos')) || [];
      this.documentosSubidos = documentosGuardados;
    },

    cerrarModalCargarDocumento() {
      this.mostrarModalCargar = false;
      this.archivoSeleccionado = null;
      this.fechaVencimiento = "";
      this.categoriaSeleccionada = "";
      this.tipoDocumentoSeleccionado = "";
    }
    
  },
  created() {
    this.obtenerTrabajador();
    this.obtenerDocumentos();
    this.obtenerEmpresas();
    this.obtenerTiposDocumentos();
    this.cargarDocumentosSubidos();

 
  },
}
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
  padding: 15px 60px;
  margin-left: 15px;
}

.boton.subir
{
  padding: 15px 25px;
  margin-top: 20px;
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
.select-tipo,
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
.tipo-documentos-container {
  margin: 15px 0;
  text-align: center;
}

.tipo-documentos-lista {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.tipo-documento-boton {
  background: #e9ecef;
  color: #495057;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.tipo-documento-boton.subido {
  background: #28a745;
  color: white;
}

.tipo-documento-boton:hover {
  background: #d6d8db;
}

.tick-verde {
  color: white;
  font-weight: bold;
  margin-left: 5px;
}
</style>