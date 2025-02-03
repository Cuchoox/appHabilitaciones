<template>
    <div class="container">
        <div class="login-container">
            <div class="login-graphic">
                <img src="../assets/logo.png" alt="Logo"
                    style="max-width: 100%; max-height: 100%;" />
            </div>
            <div class="login-form">
                <h1>Bienvenido</h1>
                <p>Ingresa tus datos para iniciar sesión.</p>
                <input type="text" v-model="username" placeholder="Usuario" />
                <input type="password" v-model="password" placeholder="Contraseña" />
                <div class="options">
                    <label>
                        <input type="checkbox" v-model="rememberMe" /> Recuérdame
                    </label>
                    <a href="#">Recuperar contraseña</a>
                </div>
                <button @click="handleLogin">Iniciar Sesión</button>
                <p v-if="error" class="error">{{ error }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            username: "",
            password: "",
            rememberMe: false,
            error: null,
        };
    },
    methods: {
        async handleLogin() {
            this.error = null; // Limpiar el error antes de iniciar
            console.log("Intentando iniciar sesión...");

            try {
                const response = await fetch("http://localhost:5000/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password,
                    }),
                });

                // Verificar si la respuesta no es exitosa
                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error("Credenciales incorrectas");
                    }
                    throw new Error("Ocurrió un error inesperado");
                }

                // Si es exitosa, procesar el token
                const { access_token } = await response.json();
                console.log("Token recibido:", access_token);

                // Guardar el token en localStorage o sessionStorage
                if (this.rememberMe) {
                    localStorage.setItem("access_token", access_token);
                } else {
                    sessionStorage.setItem("access_token", access_token);
                }

                // Verificar que Vue Router está disponible
                if (!this.$router) {
                    console.error("Vue Router no está disponible.");
                    return;
                }

                console.log("Redirigiendo a /inicio...");
                this.$router.replace("/inicio"); // Evita guardar en el historial

            } catch (err) {
                // Mostrar el error en el frontend
                this.error = err.message;
                console.error("Error en el login:", err);
            }
        },
        
    },
};
</script>

<style scoped>
body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: #2c2f33;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 10vh;
    width: 100%;
    margin-left: 102px;
}

.login-container {
    display: flex;
    width: 900px;
    height: 500px;
    background-color: #23272a;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.login-graphic {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #1b1e22;
}

.login-graphic img {
    max-width: 80%;
    max-height: 80%;
}

.login-form {
    flex: 1;
    padding: 50px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.login-form h1 {
    font-size: 2rem;
    margin-bottom: 15px;
    color: #ffffff;
}

.login-form p {
    margin-bottom: 20px;
    color: #dddddd;
}

.login-form input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid #444;
    border-radius: 5px;
    background-color: #2c2f33;
    color: #ffffff;
}

.login-form input::placeholder {
    color: #aaaaaa;
}

.login-form button {
    background-color: #1a73e8;
    color: white;
    border: none;
    padding: 14px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1.1rem;
}

.login-form button:hover {
    background-color: #1558b0;
}

.login-form .options {
    display: flex;
    justify-content: space-between;
    font-size: 1rem;
    color: #dddddd;
    align-items: center;
}

.login-form .options a {
    color: #1a73e8;
    text-decoration: none;
}

.login-form .options a:hover {
    text-decoration: underline;
}

.login-form .options label {
    display: flex;
    align-items: center;
}

.login-form .options label input {
    margin-right: 5px;
}

.error {
    color: red;
    font-size: 0.9rem;
    margin-top: 10px;
}
</style>
