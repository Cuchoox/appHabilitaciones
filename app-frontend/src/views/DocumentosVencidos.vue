<template>
    <div class="documentos-vencidos-container">
      <h1>📌 Documentos Vencidos</h1>
      
      <input type="text" v-model="busqueda" placeholder="Buscar trabajador..." class="barra-busqueda" />
      
      <div class="lista-trabajadores">
        <div v-for="(trabajador, index) in trabajadoresFiltrados" :key="index" class="trabajador-item">
          <div class="trabajador-header" @click="trabajador.expandido = !trabajador.expandido">
            {{ trabajador.nombre }} - {{ trabajador.documentos.length }} documentos vencidos
          </div>
          <div v-if="trabajador.expandido" class="documentos-lista">
            <ul>
              <li v-for="doc in trabajador.documentos" :key="doc.id">
                📄 {{ doc.nombre }} ({{ doc.fecha_vencimiento }})
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        trabajadores: [],
        busqueda: ""
      };
    },
    computed: {
      trabajadoresFiltrados() {
        return this.trabajadores.filter(trabajador =>
          trabajador.nombre.toLowerCase().includes(this.busqueda.toLowerCase())
        );
      }
    },
    async created() {
      await this.obtenerDocumentosVencidos();
    },
    methods: {
      async obtenerDocumentosVencidos() {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (!token) return;
        try {
          const response = await fetch("http://localhost:5000/documentos-vencidos", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
          });
          const data = await response.json();
          this.trabajadores = this.agruparPorTrabajador(data);
        } catch (err) {
          console.error("❌ Error al obtener documentos vencidos:", err);
        }
      },
      agruparPorTrabajador(documentos) {
        let map = {};
        documentos.forEach(doc => {
          if (!map[doc.trabajador.id]) {
            map[doc.trabajador.id] = { nombre: doc.trabajador.nombre, documentos: [], expandido: false };
          }
          map[doc.trabajador.id].documentos.push(doc);
        });
        return Object.values(map);
      }
    }
  };
  </script>
  
  <style scoped>
  .documentos-vencidos-container {
    padding: 20px;
    text-align: center;
    max-width: 800px;
    margin: auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  .barra-busqueda {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  .lista-trabajadores {
    text-align: left;
  }
  .trabajador-item {
    background: #f9f9f9;
    padding: 10px;
    margin: 10px 0;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
  }
  .trabajador-header {
    font-weight: bold;
    padding: 10px;
    background: #ffcccc;
    border-radius: 8px;
  }
  .documentos-lista {
    padding: 10px;
    background: #fff;
    border-radius: 8px;
    margin-top: 5px;
  }
  </style>
  