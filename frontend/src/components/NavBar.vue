<template>
  <nav class="app-nav">
    <div class="nav-container">
      <!-- 브랜드/로고 -->
      <div class="nav-brand" @click="goToHome">
        <div class="brand-logo">
          <v-icon size="28" color="primary">mdi-school</v-icon>
        </div>
        <div class="brand-text">
          <h1 class="brand-title">AI 자격증 플랫폼</h1>
          <p class="brand-subtitle">학습 대시보드</p>
        </div>
      </div>

      <!-- 중앙 네비게이션 -->
      <div class="nav-center">
        <div class="nav-links">
          <div
            v-for="item in navItems"
            :key="item.path"
            @click="navigateTo(item.path)"
            class="nav-link"
            :class="{ 'nav-link--active': isActiveRoute(item.path) }">
            <v-icon size="20">{{ item.icon }}</v-icon>
            <span>{{ item.title }}</span>
          </div>
        </div>
      </div>

      <!-- 우측 사용자 메뉴 -->
      <div class="nav-end">
        <div class="nav-actions">
          <!-- 알림 버튼 -->
          <button class="action-btn">
            <v-badge
              :content="notificationCount"
              :model-value="notificationCount > 0"
              color="error"
              offset-x="-2"
              offset-y="2">
              <v-icon size="20">mdi-bell-outline</v-icon>
            </v-badge>
          </button>

          <!-- 설정 버튼 -->
          <button class="action-btn" @click="navigateTo('/settings')">
            <v-icon size="20">mdi-cog-outline</v-icon>
          </button>

          <!-- 사용자 프로필 -->
          <v-menu offset-y>
            <template v-slot:activator="{ props }">
              <button class="profile-btn" v-bind="props">
                <v-avatar size="36" class="profile-avatar">
                  <v-img 
                    v-if="user.profile_picture_url" 
                    :src="`http://127.0.0.1:8000${user.profile_picture_url}`"
                    cover>
                  </v-img>
                  <v-icon v-else size="20" color="grey-darken-1">mdi-account</v-icon>
                </v-avatar>
                <div class="profile-info">
                  <span class="profile-name">{{ user.username }}</span>
                  <span class="profile-role">{{ user.is_admin ? '관리자' : '학습자' }}</span>
                </div>
                <v-icon size="16" color="grey-darken-2">mdi-chevron-down</v-icon>
              </button>
            </template>

            <v-card class="profile-menu" elevation="8">
              <div class="profile-menu-header">
                <v-avatar size="48">
                  <v-img 
                    v-if="user.profile_picture_url" 
                    :src="`http://127.0.0.1:8000${user.profile_picture_url}`"
                    cover>
                  </v-img>
                  <v-icon v-else size="24" color="grey-darken-1">mdi-account</v-icon>
                </v-avatar>
                <div class="profile-details">
                  <h4 class="profile-menu-name">{{ user.username }}</h4>
                  <p class="profile-menu-email">{{ user.email }}</p>
                </div>
              </div>

              <v-divider></v-divider>

              <div class="profile-menu-items">
                <button
                  v-for="menuItem in profileMenuItems"
                  :key="menuItem.action"
                  class="profile-menu-item"
                  @click="handleMenuAction(menuItem.action)">
                  <v-icon size="20" :color="menuItem.color">{{ menuItem.icon }}</v-icon>
                  <span>{{ menuItem.title }}</span>
                  <v-icon v-if="menuItem.external" size="16" color="grey">mdi-open-in-new</v-icon>
                </button>
              </div>

              <v-divider></v-divider>

              <div class="profile-menu-footer">
                <button class="logout-btn" @click="logout">
                  <v-icon size="20" color="error">mdi-logout</v-icon>
                  <span>로그아웃</span>
                </button>
              </div>
            </v-card>
          </v-menu>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  data() {
    return {
      user: {
        username: '',
        email: '',
        profile_picture_url: null,
        is_admin: false
      },
      notificationCount: 3, // 예시 알림 수
      navItems: [
        {
          title: '대시보드',
          path: '/user-dashboard',
          icon: 'mdi-view-dashboard-outline'
        },
        {
          title: '문제 풀기',
          path: '/pdf-list',
          icon: 'mdi-file-document-multiple-outline'
        },
        {
          title: '공지사항',
          path: '/announcements',
          icon: 'mdi-bulletin-board'
        },
        {
          title: 'AI 문제 생성',
          path: '/ai-problem-generator',
          icon: 'mdi-robot-outline'
        }
      ],
      profileMenuItems: [
        {
          title: '내 프로필',
          action: 'profile',
          icon: 'mdi-account-outline',
          color: 'primary'
        },
        {
          title: '학습 통계',
          action: 'statistics',
          icon: 'mdi-chart-line',
          color: 'success'
        },
        {
          title: '설정',
          action: 'settings',
          icon: 'mdi-cog-outline',
          color: 'grey-darken-1'
        },
        {
          title: '도움말',
          action: 'help',
          icon: 'mdi-help-circle-outline',
          color: 'info',
          external: true
        }
      ]
    }
  },
  computed: {
    // 관리자인 경우 관리자 패널 메뉴 추가
    computedNavItems() {
      let items = [...this.navItems];
      if (this.user.is_admin) {
        items.push({
          title: '관리자 패널',
          path: '/admin-panel',
          icon: 'mdi-shield-crown-outline'
        });
      }
      return items;
    }
  },
  async created() {
    await this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const response = await fetch('http://127.0.0.1:8000/users/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          this.user = await response.json();
          // 네비게이션 아이템 업데이트
          this.updateNavItems();
        }
      } catch (error) {
        console.error('사용자 프로필 가져오기 오류:', error);
      }
    },

    updateNavItems() {
      if (this.user.is_admin) {
        // 관리자인 경우 관리자 패널 추가
        if (!this.navItems.find(item => item.path === '/admin-panel')) {
          this.navItems.push({
            title: '관리자 패널',
            path: '/admin-panel',
            icon: 'mdi-shield-crown-outline'
          });
        }
      }
    },

    isActiveRoute(path) {
      return this.$route.path === path;
    },

    handleMenuAction(action) {
      switch (action) {
        case 'profile':
          this.$router.push({ name: 'UserProfile' });
          break;
        case 'statistics':
          // 통계 페이지 구현 예정
          this.$eventBus.$emit('show-snackbar', {
            text: '통계 페이지가 곧 제공됩니다',
            color: 'info',
            icon: 'mdi-chart-line'
          });
          break;
        case 'settings':
          this.$router.push({ name: 'Settings' });
          break;
        case 'help':
          // 도움말 페이지 구현 예정
          this.$eventBus.$emit('show-snackbar', {
            text: '도움말 페이지가 곧 제공됩니다',
            color: 'info',
            icon: 'mdi-help-circle'
          });
          break;
      }
    },

    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('profile_picture_url');
      this.$router.push({ name: 'Login' });
      
      this.$eventBus.$emit('show-snackbar', {
        text: '성공적으로 로그아웃되었습니다',
        color: 'success',
        icon: 'mdi-check-circle'
      });
    },
    
    goToHome() {
      // 홈으로 이동하면 라우터 가드가 적절한 대시보드로 리다이렉트
      this.$router.push('/');
    },
    
    navigateTo(path) {
      this.$router.push(path);
    }
  }
}
</script>

<style scoped>
.app-nav {
  background: #FFFFFF;
  border-bottom: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

/* 브랜드 */
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.nav-brand:hover {
  opacity: 0.8;
}

.brand-logo {
  width: 40px;
  height: 40px;
  background: #E3F2FD;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-text {
  line-height: 1.2;
}

.brand-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1A1D1F;
  margin: 0;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: #6B7280;
  margin: 0;
}

/* 중앙 네비게이션 */
.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F9FAFB;
  padding: 6px;
  border-radius: 12px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #6B7280;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  min-width: max-content;
}

.nav-link:hover {
  color: #374151;
  background: #F3F4F6;
}

.nav-link--active {
  background: #FFFFFF;
  color: #2196F3;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

/* 우측 액션 */
.nav-end {
  flex-shrink: 0;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: #F9FAFB;
  color: #6B7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #F3F4F6;
  color: #374151;
}

/* 프로필 버튼 */
.profile-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  border: none;
  background: #F9FAFB;
  cursor: pointer;
  transition: all 0.2s;
}

.profile-btn:hover {
  background: #F3F4F6;
}

.profile-avatar {
  border: 2px solid #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.profile-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1A1D1F;
}

.profile-role {
  font-size: 0.75rem;
  color: #6B7280;
}

/* 프로필 메뉴 */
.profile-menu {
  min-width: 280px;
  border-radius: 12px !important;
  border: 1px solid #E5E7EB !important;
  overflow: hidden;
}

.profile-menu-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: #F9FAFB;
}

.profile-details {
  line-height: 1.3;
}

.profile-menu-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1D1F;
  margin: 0 0 2px 0;
}

.profile-menu-email {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

.profile-menu-items {
  padding: 8px 0;
}

.profile-menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
  transition: all 0.2s;
  text-align: left;
}

.profile-menu-item:hover {
  background: #F9FAFB;
}

.profile-menu-footer {
  padding: 8px;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: #FEF2F2;
  color: #DC2626;
  cursor: pointer;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #FECACA;
}

/* 반응형 */
@media (max-width: 1024px) {
  .nav-container {
    padding: 0 16px;
    gap: 16px;
  }
  
  .brand-text {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-center {
    display: none;
  }
  
  .nav-container {
    gap: 12px;
  }
  
  .profile-info {
    display: none;
  }
}
</style>