import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Dashboard from "../components/Dashboard.vue";
import Trabajadores from "../views/Trabajadores.vue";
import Empresas from "../views/Empresas.vue";
import Documentos from "../views/Documentos.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/inicio", name: "Dashboard", component: Dashboard },
  { path: "/trabajadores", name: "Trabajadores", component: Trabajadores },
  { path: "/empresas", name: "Empresas", component: Empresas },
  // Ruta real con el ID
  { path: "/trabajadores/:id/documentos", name: "DocumentosDetalle", component: Documentos },

  // Alias para mostrar solo "/documentos"
  { path: "/documentos", redirect: "/trabajadores/:id/documentos" },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
