<template>
    <div v-if="mostrar" class="modal-overlay" @click.self="cerrarFormulario">
      <div class="modal">
        <h2> Agregar Trabajador</h2>
  
        <!-- Campos del formulario -->
        <div class="form-group">
          <label>Nombre:</label>
          <input type="text" v-model="nuevoTrabajador.nombre" placeholder="Ingrese nombre" required />
        </div>
  
        <div class="form-group">
          <label>RUT:</label>
          <input type="text" v-model="nuevoTrabajador.rut" placeholder="12.345.678-9" required />
        </div>
  
        <div class="form-group">
          <label>Cargo:</label>
          <input type="text" v-model="nuevoTrabajador.cargo" placeholder="Ej: Supervisor" required />
        </div>
  
        <div class="form-group">
          <label>Localidad:</label>
          <select v-model="nuevoTrabajador.localidad">
            <option disabled value="">Seleccione una localidad</option>
            <option>Laja</option>
            <option>Los Ángeles</option>
            <option>Navidad</option>
          </select>
        </div>
  
        <div class="form-group">
          <label>Tipo:</label>
          <select v-model="nuevoTrabajador.tipo">
            <option disabled value="">Seleccione un tipo</option>
            <option>Planta</option>
            <option>Eventual</option>
          </select>
        </div>
  
        <!-- Botones de acción -->
        <div class="form-actions">
          <button class="cancelar" @click="cerrarFormulario"> Cancelar</button>
          <button class="guardar" @click="guardarTrabajador"> Guardar</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: ["mostrar"],
    data() {
      return {
        nuevoTrabajador: {
          nombre: "",
          rut: "",
          cargo: "",
          localidad: "",
          tipo: "",
        },
      };
    },
    methods: {
      cerrarFormulario() {
        this.$emit("cerrar"); // Emite evento para cerrar el modal
      },
      guardarTrabajador() {
        if (
          !this.nuevoTrabajador.nombre ||
          !this.nuevoTrabajador.rut ||
          !this.nuevoTrabajador.cargo ||
          !this.nuevoTrabajador.localidad ||
          !this.nuevoTrabajador.tipo
        ) {
          alert("Por favor, complete todos los campos.");
          return;
        }
  
        this.$emit("agregar", { ...this.nuevoTrabajador }); // Envía el trabajador al componente padre
        this.cerrarFormulario(); // Cierra el modal
      },
    },
  };
  </script>
  
  <style scoped>
  /* 📌 Fondo oscuro detrás del modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    color: black;
  }
  
  /* 📌 Estilo del modal */
  .modal {
    background: white;
    padding: 20px;
    width: 400px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    text-align: center;
  }
  
  /* 📌 Campos del formulario */
  .form-group {
    margin-bottom: 15px;
    text-align: left;
  }
  
  label {
    font-weight: bold;
    display: block;
    margin-bottom: 5px;
    color: black;
  }
  
  input, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  /* 📌 Botones */
  .form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  
  button {
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .cancelar {
    background: #d9534f;
    color: white;
  }
  
  .cancelar:hover {
    background: #c9302c;
  }
  
  .guardar {
    background: #5cb85c;
    color: white;
  }
  
  .guardar:hover {
    background: #4cae4c;
  }
  </style>
  