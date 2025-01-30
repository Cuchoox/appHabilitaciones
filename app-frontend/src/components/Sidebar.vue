
<template>
    <aside class="sidebar">
      <!-- Logo -->
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="MCI Logo" class="logo" />
      </div>
  
      <!-- Menú de navegación -->
      <nav class="menu">
        <router-link to="/inicio" class="menu-item" :class="{ active: $route.path === '/inicio' }"> Dashboard</router-link>
        <router-link to="/trabajadores" class="menu-item" :class="{ active: $route.path === '/trabajadores' }"> Trabajadores</router-link>
        <router-link to="/empresas" class="menu-item" :class="{ active: $route.path === '/empresas' }"> Empresas</router-link>
        <router-link to="/documentos" class="menu-item" :class="{ active: $route.path === '/documentos' }"> Documentos</router-link>
        <router-link to="/historial" class="menu-item" :class="{ active: $route.path === '/historial' }"> Historial</router-link>
      </nav>
  
      <!-- Botón de Cerrar Sesión -->
      <button class="logout-button"> Cerrar Sesión</button>
    </aside>
  </template>
  
  <script>
  export default {
    name: "Sidebar",
  };
  </script>
  
  <style scoped>
  /* --- Estilos Generales de la Sidebar --- */
  .sidebar {
    width: 250px;
    height: 100vh;
    background: linear-gradient(to bottom, #134b91, #0f3b70);
    display: flex;
    flex-direction: column;
    padding: 20px;
    position: fixed; /* Si hay problemas, cambia a absolute */
    left: 0;
    top: 0;
    bottom: 0;
}
  
  /* --- Logo --- */
  .logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .logo {
    width: 80px;
    height: auto;
    border-radius: 50%;
    border: 3px solid white;
  }
  
  /* --- Menú --- */
  .menu {
    display: flex;
    flex-direction: column;
    gap: 15px;
    flex-grow: 1; /* Permite que el botón de cerrar sesión baje */
  }
  
  .menu-item {
    color: white;
    text-decoration: none;
    font-size: 1rem;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: background-color 0.3s, transform 0.2s;
  }
  
  .menu-item:hover {
    background-color: rgba(255, 255, 255, 0.2);
    transform: scale(1.05);
  }
  
  /* --- Resaltar opción activa --- */
  .menu-item.active {
    background-color: rgba(255, 255, 255, 0.3);
    border-left: 5px solid white;
  }
  
  /* --- Botón de Cerrar Sesión --- */
  .logout-button {
    width: 100%;
    padding: 12px;
    background-color: #092448;
    color: white;
    font-size: 1rem;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s, transform 0.2s;
    margin-bottom: 25px;
  }
  
  .logout-button:hover {
    background-color: darkred;
    transform: scale(1.05);
  }
  
  .logout-button:active {
    transform: scale(0.95);
  }
  </style>