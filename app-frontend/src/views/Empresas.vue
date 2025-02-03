<template>
    <div class="empresas-container">
      <h1>Lista de Empresas</h1>
  
      <table class="tabla-empresas">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Trabajadores Activos</th>
            <th>Documentos Requeridos</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="empresa in empresas" :key="empresa.id">
            <td>{{ empresa.nombre }}</td>
            <td>{{ empresa.trabajadores_activos }}</td>
            <td>
              <button class="config-docs" @click="configurarDocumentos(empresa)">📄 Configurar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        empresas: []
      };
    },
    methods: {
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
            throw new Error("Error al obtener empresas");
          }
  
          this.empresas = await response.json();
        } catch (error) {
          console.error("❌ Error al obtener empresas:", error);
        }
      },
      configurarDocumentos(empresa) {
        alert(`Configurar documentos para ${empresa.nombre}`);
        // Aquí más adelante puedes hacer un modal para tipificar los documentos requeridos
      }
    },
    created() {
      this.obtenerEmpresas();
    }
  };
  </script>
  
  <style scoped>
  .empresas-container {
    padding: 20px;
    background-color: #f9f9f9;
  }
  
  h1 {
    text-align: center;
    color: #134b91;
  }
  
  .tabla-empresas {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 10px;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    color: black;
  }
  
  th {
    background-color: #134b91;
    color: white;
  }
  
  .config-docs {
    background-color: #007bff;
    color: white;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  </style>
  