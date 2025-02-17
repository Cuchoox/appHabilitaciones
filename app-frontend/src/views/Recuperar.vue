<template>
    <div class="recuperar-container">
      <h2>Recuperar Contraseña</h2>
      <p>Ingresa tu correo electrónico y recibirás una nueva contraseña segura.</p>
      <input type="email" v-model="email" placeholder="Ingresa tu correo" />
      <button @click="enviarRecuperacion">Enviar</button>
      <button @click="$router.push('/login')">Cancelar</button>
  
      <p v-if="mensajeExito" class="mensaje-exito">{{ mensajeExito }}</p>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return { 
        email: "",
        mensajeExito: ""
      };
    },
    methods: {
      async enviarRecuperacion() {
        try {
          const response = await fetch("https://apphabilitaciones.onrender.com/recuperar-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: this.email }),
          });
  
          if (!response.ok) throw new Error("Error al recuperar contraseña");
  
          this.mensajeExito = "📧 Correo enviado con la nueva contraseña.";
          setTimeout(() => this.$router.push("/"), 3000);
        } catch (error) {
          console.error("❌ Error:", error);
          alert("Error al enviar la solicitud.");
        }
      },
    },
  };
  </script>
<style scoped>
.recuperar-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: #fff;
    text-align: center;
}

h2 {
    margin-bottom: 20px;
    color: #333;
}

p {
    margin-bottom: 20px;
    color: #666;
}

input[type="email"] {
    width: calc(100% - 20px);
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

button {
    width: calc(50% - 10px);
    padding: 10px;
    margin: 5px;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: #fff;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

button:hover {
    background-color: #0056b3;
}

button:nth-child(2) {
    background-color: #6c757d;
}

button:nth-child(2):hover {
    background-color: #5a6268;
}

.mensaje-exito {
    margin-top: 20px;
    color: #28a745;
}
</style>