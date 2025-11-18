<template>
  <div class="login-page">
    <v-container class="fill-height pa-0" fluid>
      <v-row no-gutters class="fill-height">
        <!-- 왼쪽 브랜드 섹션 -->
        <v-col cols="12" md="7" class="brand-section d-none d-md-flex">
          <div class="brand-content">
            <div class="brand-inner">
              <h1 class="brand-title">
                AI 자격증 학습 플랫폼
              </h1>
              <p class="brand-subtitle">
                인공지능 기반의 맞춤형 학습으로<br>
                효율적인 자격증 준비를 시작하세요
              </p>
              
              <div class="features-grid">
                <div class="feature-card" v-for="feature in features" :key="feature.id">
                  <div class="feature-icon-wrapper">
                    <v-icon :color="feature.color" size="24">{{ feature.icon }}</v-icon>
                  </div>
                  <h3 class="feature-title">{{ feature.title }}</h3>
                  <p class="feature-desc">{{ feature.desc }}</p>
                </div>
              </div>
            </div>
          </div>
        </v-col>

        <!-- 오른쪽 로그인 폼 섹션 -->
        <v-col cols="12" md="5" class="form-section">
          <div class="form-container">
            <div class="form-inner">
              <!-- 로고 -->
              <div class="logo-wrapper mb-8">
                <div class="logo-icon">
                  <v-icon size="32" color="primary">mdi-school</v-icon>
                </div>
              </div>
              
              <div class="form-header mb-8">
                <h2 class="form-title">다시 오신 것을 환영합니다</h2>
                <p class="form-subtitle">계속하려면 계정에 로그인하세요</p>
              </div>

              <v-form @submit.prevent="login" class="login-form">
                <div class="form-group">
                  <label class="form-label">사용자 이름</label>
                  <v-text-field
                    v-model="username"
                    placeholder="사용자 이름을 입력하세요"
                    required
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="custom-input">
                    <template v-slot:prepend-inner>
                      <v-icon size="20" color="grey">mdi-account-outline</v-icon>
                    </template>
                  </v-text-field>
                </div>
                
                <div class="form-group">
                  <label class="form-label">비밀번호</label>
                  <v-text-field
                    v-model="password"
                    placeholder="비밀번호를 입력하세요"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="custom-input">
                    <template v-slot:prepend-inner>
                      <v-icon size="20" color="grey">mdi-lock-outline</v-icon>
                    </template>
                    <template v-slot:append-inner>
                      <v-icon 
                        size="20" 
                        @click="showPassword = !showPassword"
                        style="cursor: pointer;">
                        {{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
                      </v-icon>
                    </template>
                  </v-text-field>
                </div>

                <div class="form-options mb-6">
                  <v-checkbox
                    v-model="rememberMe"
                    label="로그인 상태 유지"
                    density="compact"
                    hide-details
                    class="remember-checkbox">
                  </v-checkbox>
                  <router-link to="/password-reset" class="forgot-link">
                    비밀번호를 잊으셨나요?
                  </router-link>
                </div>

                <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4">
                  {{ errorMessage }}
                </v-alert>

                <v-btn 
                  type="submit" 
                  color="primary" 
                  size="large"
                  block
                  :loading="loading"
                  class="login-btn">
                  로그인
                </v-btn>

                <div class="divider-wrapper">
                  <span class="divider-text">또는</span>
                </div>

                <div class="register-prompt">
                  계정이 없으신가요?
                  <router-link to="/register" class="register-link">
                    회원가입
                  </router-link>
                </div>
              </v-form>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      errorMessage: '',
      loading: false,
      features: [
        {
          id: 1,
          icon: 'mdi-brain',
          color: 'primary',
          title: 'AI 기반 학습',
          desc: '개인 맞춤형 문제 추천'
        },
        {
          id: 2,
          icon: 'mdi-chart-line',
          color: 'success',
          title: '실시간 분석',
          desc: '학습 진도 실시간 추적'
        },
        {
          id: 3,
          icon: 'mdi-file-document-multiple',
          color: 'accent',
          title: '다양한 자료',
          desc: '최신 기출문제 제공'
        },
      ]
    }
  },
  methods: {
    async login() {
      if (!this.username || !this.password) {
        this.errorMessage = '사용자명과 비밀번호를 입력해주세요.';
        return;
      }

      this.loading = true;
      this.errorMessage = '';

      try {
        const response = await fetch('http://127.0.0.1:8000/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: this.username,
            password: this.password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem('access_token', data.access_token);
          
          if (data.is_admin) {
            this.$router.push({ name: 'AdminPanel' });
          } else {
            this.$router.push({ name: 'UserDashboard' });
          }
        } else {
          this.errorMessage = data.detail || '로그인에 실패했습니다.';
        }
      } catch (error) {
        console.error('로그인 요청 중 오류 발생:', error);
        this.errorMessage = '서버에 연결할 수 없습니다.';
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    // 이미 로그인된 경우 대시보드로 리다이렉트
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        
        if (payload.is_admin) {
          this.$router.push({ name: 'AdminPanel' });
        } else {
          this.$router.push({ name: 'UserDashboard' });
        }
      } catch (e) {
        localStorage.removeItem('access_token');
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #FFFFFF;
}

/* 브랜드 섹션 */
.brand-section {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.05" d="M0,32L48,53.3C96,75,192,117,288,122.7C384,128,480,96,576,101.3C672,107,768,149,864,170.7C960,192,1056,192,1152,165.3C1248,139,1344,85,1392,58.7L1440,32L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat center;
  background-size: cover;
  transform: rotate(180deg);
}

.brand-content {
  width: 100%;
  max-width: 600px;
  padding: 48px;
  position: relative;
  z-index: 1;
}

.brand-inner {
  color: white;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 1.25rem;
  font-weight: 300;
  opacity: 0.9;
  margin-bottom: 48px;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  gap: 24px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon-wrapper {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 0.875rem;
  opacity: 0.9;
  line-height: 1.5;
}

/* 폼 섹션 */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FAFAFA;
}

.form-container {
  width: 100%;
  max-width: 480px;
  padding: 48px;
}

.form-inner {
  width: 100%;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: #E3F2FD;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-header {
  text-align: center;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #212121;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 1rem;
  color: #616161;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #424242;
  margin-bottom: 8px;
}

.custom-input :deep(.v-field) {
  border-radius: 8px;
}

.custom-input :deep(.v-field__input) {
  padding-top: 14px;
  padding-bottom: 14px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-checkbox {
  flex: none;
}

.forgot-link {
  color: #2196F3;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  font-weight: 600;
  height: 48px;
  font-size: 1rem;
  letter-spacing: 0.02em;
}

.divider-wrapper {
  position: relative;
  text-align: center;
  margin: 32px 0;
}

.divider-wrapper::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #E0E0E0;
  transform: translateY(-50%);
}

.divider-text {
  background: #FAFAFA;
  padding: 0 16px;
  font-size: 0.875rem;
  color: #9E9E9E;
  position: relative;
}

.register-prompt {
  text-align: center;
  color: #616161;
  font-size: 0.875rem;
}

.register-link {
  color: #2196F3;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.register-link:hover {
  text-decoration: underline;
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-inner {
  animation: fadeIn 0.6s ease-out;
}

.feature-card {
  animation: fadeIn 0.8s ease-out;
  animation-fill-mode: both;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }

/* 모바일 대응 */
@media (max-width: 960px) {
  .form-container {
    padding: 24px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
}
</style>