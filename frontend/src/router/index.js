import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ExploreView from '@/views/ExploreView.vue'
import GamedetailView from '@/views/GameDetailView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/explore',
      name: 'explore',
      component: ExploreView,
    },
    {
    path: '/games/:id',
    name: 'game-detail',
    component: GamedetailView,  // ← 이미 연결됨
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { title: '로그인 · IndieGate' },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { title: '회원가입 · IndieGate' },
  },
  ],
})

export default router
