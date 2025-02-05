<template>
  <div v-if="mostrar" class="modal-overlay" @click.self="cerrarFormulario">
    <div class="modal">
      <h2>{{ modoEdicion ? "Editar Trabajador" : "Agregar Trabajador" }}</h2>

      <!-- Campos del formulario -->
      <div class="form-group">
        <label>Nombres:</label>
        <input type="text" v-model="nuevoTrabajador.nombre" placeholder="Ingrese nombres" required />
      </div>

      <div class="form-group">
        <label>Apellidos:</label>
        <input type="text" v-model="nuevoTrabajador.apellido" placeholder="Ingrese apellidos" required />
      </div>

      <div class="form-group">
        <label>RUT:</label>
        <input type="text" 
       v-model="nuevoTrabajador.rut" 
       placeholder="12.345.678-9" 
       @input="formatearRut"
       maxlength="12" />

      </div>

      <div class="form-group">
        <label>Cargo:</label>
        <input type="text" v-model="nuevoTrabajador.cargo" placeholder="Ej: Supervisor" required />
      </div>

      <div class="form-group">
        <label>Localidad:</label>
        <input type="text" v-model="nuevoTrabajador.localidad" placeholder="Ingrese localidad" required />
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
        <button class="cancelar" @click="cerrarFormulario">Cancelar</button>
        <button class="guardar" @click="guardarTrabajador">
          {{ modoEdicion ? "Actualizar" : "Guardar" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
props: {
  mostrar: Boolean,
  trabajador: Object, // Recibe el trabajador a editar (puede ser null)
},
data() {
  return {
    nuevoTrabajador: {
      nombre: "",
      apellido: "",
      rut: "",
      cargo: "",
      localidad: "",
      tipo: "",
    },
  };
},
computed: {
  modoEdicion() {
    return this.trabajador && Object.keys(this.trabajador).length > 0;
  }
},
watch: {
  trabajador: {
    handler(nuevoValor) {
      if (nuevoValor) {
        this.nuevoTrabajador = { ...nuevoValor }; // Clonamos para evitar modificar el original
      } else {
        this.resetFormulario();
      }
    },
    deep: true,
    immediate: true
  },
},
methods: {
  cerrarFormulario() {
    this.$emit("cerrar"); // Cierra el modal
  },
  guardarTrabajador() {
    if (!this.nuevoTrabajador.nombre || !this.nuevoTrabajador.rut || !this.nuevoTrabajador.cargo || !this.nuevoTrabajador.localidad || !this.nuevoTrabajador.tipo) {
      alert("Por favor, complete todos los campos.");
      return;
    }
    
    if (this.modoEdicion) {
      this.$emit("editar", { ...this.nuevoTrabajador }); // Emite evento de edición
    } else {
      this.$emit("agregar", { ...this.nuevoTrabajador }); // Emite evento de creación
    }
    
    this.cerrarFormulario(); // Cierra el modal
  },
  resetFormulario() {
    this.nuevoTrabajador = {
      nombre: "",
      apellido:"",
      rut: "",
      cargo: "",
      localidad: "",
      tipo: "",
    };
  },

  
  formatearRut() {
    let rut = this.nuevoTrabajador.rut;
    
    // Remueve todo lo que no sea número o 'k' (último dígito verificador)
    rut = rut.replace(/[^0-9kK]/g, '');
    
    // Si tiene más de 9 caracteres (RUT chileno), corta el exceso
    if (rut.length > 9) rut = rut.slice(0, 9);
    
    // Separa el dígito verificador
    let cuerpo = rut.slice(0, -1);
    let dv = rut.slice(-1);
    
    // Aplica el formato con puntos y guión
    cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    
    // Reasigna el valor formateado
    this.nuevoTrabajador.rut = cuerpo + (dv ? `-${dv}` : '');
  }

},

};
</script>

<style scoped>
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

.modal {
background: white;
padding: 20px;
width: 400px;
border-radius: 10px;
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
text-align: center;
}

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
