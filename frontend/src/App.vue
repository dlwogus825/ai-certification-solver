<template>
  <v-app>
    <NavBar v-if="isAuthenticated" />
    <v-main class="app-main">
      <router-view />
    </v-main>
    
    <!-- Global Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :timeout="snackbar.timeout"
      :color="snackbar.color"
      location="top"
      variant="flat"
      rounded="lg"
      class="global-snackbar">
      <div class="d-flex align-center">
        <v-icon class="mr-3">{{ snackbar.icon }}</v-icon>
        <span>{{ snackbar.text }}</span>
      </div>
    </v-snackbar>
  </v-app>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    NavBar,
  },
  data() {
    return {
      snackbar: {
        show: false,
        text: '',
        color: 'info',
        icon: 'mdi-information',
        timeout: 3000
      }
    };
  },
  computed: {
    isAuthenticated() {
      // 현재 라우트가 로그인, 회원가입, 비밀번호 재설정, 홈이 아닌 경우에만 NavBar 표시
      const publicRoutes = ['Login', 'Register', 'PasswordReset', 'Home'];
      return !publicRoutes.includes(this.$route.name);
    },
  },
  mounted() {
    // 글로벌 이벤트 리스너
    this.$eventBus.$on('show-snackbar', (data) => {
      this.snackbar = {
        show: true,
        text: data.text,
        color: data.color || 'info',
        icon: data.icon || 'mdi-information',
        timeout: data.timeout || 3000
      };
    });
  },
  beforeUnmount() {
    this.$eventBus.$off('show-snackbar');
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #F8FAFB;
  color: #1A1D1F;
  line-height: 1.6;
}

.app-main {
  background: #F8FAFB;
  min-height: 100vh;
}


/* Enhanced Vuetify Overrides */
.v-application {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.v-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
  border: 1px solid rgba(0, 0, 0, 0.06) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.v-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.v-btn {
  font-weight: 500 !important;
  letter-spacing: 0.01em !important;
  box-shadow: none !important;
}

.v-btn--elevated {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
}

.v-btn--elevated:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12) !important;
}

.v-text-field .v-field {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
}

.v-text-field .v-field:hover {
  border-color: #D1D5DB !important;
}

.v-text-field .v-field--focused {
  border-color: #2196F3 !important;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.08) !important;
}

/* Typography Scale */
h1, .text-h1 {
  font-size: 2.5rem !important;
  font-weight: 700 !important;
  line-height: 1.2 !important;
  letter-spacing: -0.02em !important;
}

h2, .text-h2 {
  font-size: 2rem !important;
  font-weight: 600 !important;
  line-height: 1.3 !important;
  letter-spacing: -0.01em !important;
}

h3, .text-h3 {
  font-size: 1.5rem !important;
  font-weight: 600 !important;
  line-height: 1.4 !important;
}

h4, .text-h4 {
  font-size: 1.25rem !important;
  font-weight: 600 !important;
  line-height: 1.5 !important;
}

h5, .text-h5 {
  font-size: 1.125rem !important;
  font-weight: 600 !important;
  line-height: 1.5 !important;
}

h6, .text-h6 {
  font-size: 1rem !important;
  font-weight: 600 !important;
  line-height: 1.5 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

::-webkit-scrollbar-track {
  background: #F3F4F6;
  border-radius: 6px;
}

::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 6px;
  border: 3px solid #F3F4F6;
}

::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}

/* Global Snackbar */
.global-snackbar {
  font-family: 'Inter', sans-serif !important;
}

.global-snackbar .v-snackbar__wrapper {
  min-width: 344px !important;
}

/* Loading States */
.skeleton-loader {
  background: linear-gradient(
    90deg,
    #F3F4F6 0%,
    #E5E7EB 50%,
    #F3F4F6 100%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Focus Styles */
*:focus-visible {
  outline: 2px solid #2196F3;
  outline-offset: 2px;
}

/* Selection */
::selection {
  background: rgba(33, 150, 243, 0.2);
  color: #1976D2;
}

/* Print Styles */
@media print {
  .v-navigation-drawer,
  .v-app-bar,
  .v-footer {
    display: none !important;
  }
}
</style>