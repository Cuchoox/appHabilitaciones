import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Dashboard from "../components/Dashboard.vue"; // Asegúrate de que este archivo existe
import Trabajadores from "../views/Trabajadores.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/inicio", name: "Dashboard", component: Dashboard }, // Verifica el path
  { path: "/trabajadores", name: "Trabajadores", component: Trabajadores },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
