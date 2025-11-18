import { createApp } from 'vue'

// Vue feature flags
if (typeof window !== 'undefined') {
  window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false
}
import App from './App.vue'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // MDI 아이콘 CSS
import { aliases, mdi } from 'vuetify/iconsets/mdi' // MDI 아이콘셋 임포트
import './styles/global.css' // 글로벌 스타일 임포트

// Vue Router 임포트
import { createRouter, createWebHistory } from 'vue-router'
import eventBus from './eventBus'; // eventBus 임포트

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#2196F3', // Professional Blue
          secondary: '#9C27B0', // Elegant Purple
          accent: '#009688', // Vibrant Teal
          error: '#F44336',
          info: '#00B0FF',
          success: '#00C853',
          warning: '#FF6D00',
          background: '#F8F9FA',
          surface: '#FFFFFF',
          'on-surface': '#212121',
          'surface-variant': '#F5F5F5',
          'primary-darken-1': '#1976D2',
          'secondary-darken-1': '#7B1FA2',
        },
      },
      dark: {
        colors: {
          primary: '#42A5F5',
          secondary: '#BA68C8',
          accent: '#26A69A',
          error: '#EF5350',
          info: '#29B6F6',
          success: '#66BB6A',
          warning: '#FFA726',
          background: '#121212',
          surface: '#1E1E1E',
          'surface-variant': '#2E2E2E',
        },
      },
    },
  },
  defaults: {
    VCard: {
      elevation: 2,
      rounded: 'lg',
    },
    VBtn: {
      rounded: 'lg',
      elevation: 0,
      style: 'text-transform: none; font-weight: 500;'
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
  },
})

// 라우트 정의
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('./views/Home.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/Register.vue'),
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: () => import('./views/PasswordReset.vue'),
  },
  {
    path: '/user-dashboard',
    name: 'UserDashboard',
    component: () => import('./views/UserDashboard.vue'),
    meta: { requiresAuth: true, requiresUser: true } // 사용자 권한 필요
  },
  {
    path: '/admin-panel',
    name: 'AdminPanel',
    component: () => import('./views/AdminPanel.vue'),
    meta: { requiresAuth: true, requiresAdmin: true } // 관리자 권한 필요
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('./views/UserProfile.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
  {
    path: '/solve-pdf/:documentId?',
    name: 'PdfProblemSolver',
    component: () => import('./views/PdfProblemSolver.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
  {
    path: '/pdf-list',
    name: 'PdfList',
    component: () => import('./views/PdfListView.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: () => import('./views/Announcements.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/SettingsPage.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
  {
    path: '/ai-problem-generator',
    name: 'AIProblemGenerator',
    component: () => import('./views/AIProblemGenerator.vue'),
    meta: { requiresAuth: true } // 인증이 필요한 경로임을 표시
  },
]

// 라우터 인스턴스 생성
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 전역 네비게이션 가드 (인증 및 권한 확인)
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  let isAdmin = false;
  if (isAuthenticated) {
    try {
      const token = localStorage.getItem('access_token');
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      isAdmin = payload.is_admin === true;
    } catch (e) {
      console.error("토큰 파싱 오류:", e);
      // 토큰이 유효하지 않으면 로그인 페이지로 리다이렉트
      localStorage.removeItem('access_token');
      next({ name: 'Login' });
      return;
    }
  }

  if (to.path === '/' && isAuthenticated) {
    if (isAdmin) {
      next({ name: 'AdminPanel' });
    } else {
      next({ name: 'UserDashboard' });
    }
  } else if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' }); // 인증 필요하지만 로그인 안 됨
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: 'UserDashboard' }); // 관리자 권한 필요하지만 관리자 아님
  } else if (to.meta.requiresUser && isAdmin) {
    next({ name: 'AdminPanel' }); // 사용자 권한 필요하지만 관리자임 (관리자는 사용자 대시보드 접근 불가)
  } else {
    next(); // 모든 조건 통과
  }
});

const app = createApp(App)

app.use(vuetify).use(router)

// eventBus를 전역 속성으로 등록
app.config.globalProperties.$eventBus = eventBus;

app.mount('#app')