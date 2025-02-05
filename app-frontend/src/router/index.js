import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Dashboard from "../components/Dashboard.vue";
import Trabajadores from "../views/Trabajadores.vue";
import Empresas from "../views/Empresas.vue";
import Documentos from "../views/Documentos.vue";
import DocumentosVencidos from "@/views/DocumentosVencidos.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/inicio", name: "Dashboard", component: Dashboard },
  { path: "/trabajadores", name: "Trabajadores", component: Trabajadores },
  { path: "/empresas", name: "Empresas", component: Empresas },
  // Ruta real con el ID
  { path: "/documentos", name: "Documentos", component: Documentos },
  { path: "/documentos-vencidos", name: "DocumentosVencidos", component: DocumentosVencidos },



];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
