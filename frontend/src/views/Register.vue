<template>
  <div class="register-page">
    <v-container class="fill-height pa-0" fluid>
      <v-row no-gutters class="fill-height">
        <!-- 왼쪽 브랜드 섹션 -->
        <v-col cols="12" md="6" class="brand-section d-none d-md-flex">
          <div class="brand-content">
            <div class="brand-header">
              <v-icon size="48" color="primary" class="mb-4">mdi-account-plus</v-icon>
              <h1 class="brand-title">AI 자격증 학습 플랫폼</h1>
              <p class="brand-subtitle">
                지금 가입하고 맞춤형 학습을 시작하세요
              </p>
            </div>
            
            <div class="benefits-list">
              <div class="benefit-item" v-for="benefit in benefits" :key="benefit.id">
                <v-icon :color="benefit.color" size="20" class="mr-3">{{ benefit.icon }}</v-icon>
                <span>{{ benefit.text }}</span>
              </div>
            </div>
            
            <div class="stats-section">
              <div class="stat-item" v-for="stat in stats" :key="stat.label">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>
        </v-col>

        <!-- 오른쪽 회원가입 폼 섹션 -->
        <v-col cols="12" md="6" class="form-section">
          <div class="form-container">
            <div class="form-header">
              <!-- 모바일에서만 보이는 로고 -->
              <div class="mobile-brand d-md-none mb-6">
                <v-icon size="40" color="primary" class="mb-2">mdi-account-plus</v-icon>
                <h2 class="mobile-title">AI 자격증 학습 플랫폼</h2>
              </div>
              
              <h1 class="page-title">회원가입</h1>
              <p class="page-subtitle">무료 계정을 만들고 효율적인 학습을 시작하세요</p>
            </div>

            <v-form @submit.prevent="registerUser" class="register-form">
              <v-text-field
                v-model="username"
                label="사용자 이름"
                name="username"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :loading="loading"
                :error-messages="usernameError"
                required
              ></v-text-field>

              <v-text-field
                v-model="email"
                label="이메일 주소"
                name="email"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :loading="loading"
                :error-messages="emailError"
                required
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="비밀번호"
                name="password"
                prepend-inner-icon="mdi-lock-outline"
                type="password"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :loading="loading"
                :error-messages="passwordError"
                @keyup.enter="registerUser"
                required
              ></v-text-field>

              <v-text-field
                v-model="confirmPassword"
                label="비밀번호 확인"
                name="confirmPassword"
                prepend-inner-icon="mdi-lock-check-outline"
                type="password"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :loading="loading"
                :error-messages="confirmPasswordError"
                @keyup.enter="registerUser"
                required
              ></v-text-field>

              <div class="terms-section mb-4">
                <v-checkbox
                  v-model="agreeTerms"
                  :error-messages="termsError"
                  density="compact"
                  hide-details="auto"
                >
                  <template v-slot:label>
                    <span class="terms-text">
                      <a href="#" class="terms-link">이용약관</a>과 
                      <a href="#" class="terms-link">개인정보처리방침</a>에 동의합니다
                    </span>
                  </template>
                </v-checkbox>
              </div>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="loading"
                :disabled="!username || !email || !password || !confirmPassword || !agreeTerms"
                block
                class="register-btn mb-4">
                무료 계정 만들기
              </v-btn>

              <v-divider class="my-6">
                <span class="divider-text">또는</span>
              </v-divider>

              <div class="login-section" v-if="!showEmailVerification">
                <p class="login-text">이미 계정이 있으신가요?</p>
                <v-btn
                  variant="outlined"
                  color="primary"
                  size="large"
                  to="/login"
                  block
                  class="login-btn">
                  로그인
                </v-btn>
              </div>
            </v-form>

            <!-- 이메일 인증 안내 섹션 -->
            <div v-if="showEmailVerification" class="email-verification-section">
              <div class="verification-header">
                <v-icon size="64" color="success" class="mb-4">mdi-email-check</v-icon>
                <h2 class="verification-title">이메일 인증이 필요합니다</h2>
                <p class="verification-subtitle">{{ registeredEmail }}로 인증 메일을 발송했습니다</p>
              </div>
              
              <div class="verification-content">
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mb-4">
                  <template v-slot:prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  <div>
                    <strong>이메일을 확인하여 인증을 완료해주세요</strong>
                    <ul class="verification-steps mt-2">
                      <li>이메일 받은편지함을 확인하세요</li>
                      <li>스팸 폴더도 확인해보세요</li>
                      <li>이메일의 인증 링크를 클릭하세요</li>
                      <li>인증 완료 후 로그인할 수 있습니다</li>
                    </ul>
                  </div>
                </v-alert>
                
                <div class="verification-actions">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    size="large"
                    :loading="resendLoading"
                    @click="resendVerificationEmail"
                    block
                    class="mb-3">
                    <v-icon left>mdi-email-send</v-icon>
                    인증 메일 재발송
                  </v-btn>
                  
                  <v-btn
                    color="success"
                    size="large"
                    to="/login"
                    block
                    class="mb-3">
                    <v-icon left>mdi-login</v-icon>
                    로그인 페이지로 이동
                  </v-btn>
                  
                  <v-btn
                    variant="text"
                    color="primary"
                    size="small"
                    @click="goBackToRegister"
                    block>
                    <v-icon left>mdi-arrow-left</v-icon>
                    다시 회원가입하기
                  </v-btn>
                </div>
              </div>
            </div>

            <!-- 메시지 표시 -->
            <v-alert
              v-if="message && !showEmailVerification"
              :type="messageType"
              class="mt-4"
              variant="tonal"
              closable
              @click:close="message = ''">
              {{ message }}
            </v-alert>
            
            <!-- 이메일 인증 섹션에서의 메시지 표시 -->
            <v-alert
              v-if="message && showEmailVerification"
              :type="messageType"
              class="mt-4"
              variant="tonal"
              closable
              @click:close="message = ''">
              {{ message }}
            </v-alert>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeTerms: false,
      loading: false,
      message: '',
      messageType: 'info',
      showEmailVerification: false,
      registeredEmail: '',
      registeredUsername: '',
      resendLoading: false,
      usernameError: '',
      emailError: '',
      passwordError: '',
      confirmPasswordError: '',
      termsError: '',
      benefits: [
        {
          id: 1,
          icon: 'mdi-account-check',
          text: '개인 맞춤 학습 경로',
          color: 'primary'
        },
        {
          id: 2,
          icon: 'mdi-chart-timeline-variant',
          text: '실시간 학습 진도 추적',
          color: 'success'
        },
        {
          id: 3,
          icon: 'mdi-brain',
          text: 'AI 기반 문제 추천',
          color: 'warning'
        },
        {
          id: 4,
          icon: 'mdi-certificate',
          text: '다양한 자격증 대비',
          color: 'info'
        },
        {
          id: 5,
          icon: 'mdi-forum',
          text: '학습자 커뮤니티 참여',
          color: 'purple'
        },
        {
          id: 6,
          icon: 'mdi-cloud-download',
          text: '무제한 학습 자료 접근',
          color: 'teal'
        }
      ],
      stats: [
        { value: '무료', label: '회원가입' },
        { value: '1,000+', label: '학습 문제' },
        { value: '24/7', label: '언제든 학습' }
      ]
    };
  },
  methods: {
    validateForm() {
      // 초기화
      this.usernameError = '';
      this.emailError = '';
      this.passwordError = '';
      this.confirmPasswordError = '';
      this.termsError = '';
      
      let isValid = true;
      
      // 사용자 이름 검증
      if (!this.username.trim()) {
        this.usernameError = '사용자 이름을 입력해주세요';
        isValid = false;
      } else if (this.username.length < 3) {
        this.usernameError = '사용자 이름은 3자 이상이어야 합니다';
        isValid = false;
      }
      
      // 이메일 검증
      if (!this.email.trim()) {
        this.emailError = '이메일을 입력해주세요';
        isValid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {
        this.emailError = '올바른 이메일 형식을 입력해주세요';
        isValid = false;
      }
      
      // 비밀번호 검증
      if (!this.password.trim()) {
        this.passwordError = '비밀번호를 입력해주세요';
        isValid = false;
      } else if (this.password.length < 6) {
        this.passwordError = '비밀번호는 6자 이상이어야 합니다';
        isValid = false;
      }
      
      // 비밀번호 확인 검증
      if (!this.confirmPassword.trim()) {
        this.confirmPasswordError = '비밀번호 확인을 입력해주세요';
        isValid = false;
      } else if (this.password !== this.confirmPassword) {
        this.confirmPasswordError = '비밀번호가 일치하지 않습니다';
        isValid = false;
      }
      
      // 약관 동의 검증
      if (!this.agreeTerms) {
        this.termsError = '이용약관에 동의해주세요';
        isValid = false;
      }
      
      return isValid;
    },
    
    async registerUser() {
      this.message = '';
      
      if (!this.validateForm()) {
        return;
      }
      
      this.loading = true;
      
      try {
        const response = await fetch('http://127.0.0.1:8000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            email: this.email,
            password: this.password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          // 이메일 인증이 필요한 경우
          if (data.email_verification_sent) {
            this.registeredEmail = data.email || this.email;
            this.registeredUsername = data.username || this.username;
            this.showEmailVerification = true;
            this.message = '';
            
            // 폼 초기화
            this.username = '';
            this.email = '';
            this.password = '';
            this.confirmPassword = '';
            this.agreeTerms = false;
          } else {
            // 이메일 인증이 필요없는 경우 (기존 로직)
            this.message = '회원가입이 완료되었습니다! 로그인 페이지로 이동합니다...';
            this.messageType = 'success';
            
            // 폼 초기화
            this.username = '';
            this.email = '';
            this.password = '';
            this.confirmPassword = '';
            this.agreeTerms = false;
            
            // 2초 후 로그인 페이지로 이동
            setTimeout(() => {
              this.$router.push({ name: 'Login' });
            }, 2000);
          }
        } else {
          if (data.detail && data.detail.includes('username')) {
            this.usernameError = '이미 사용 중인 사용자 이름입니다';
          } else if (data.detail && data.detail.includes('email')) {
            this.emailError = '이미 등록된 이메일 주소입니다';
          } else {
            this.message = data.detail || '회원가입에 실패했습니다. 다시 시도해주세요.';
            this.messageType = 'error';
          }
        }
      } catch (error) {
        console.error('회원가입 요청 중 오류 발생:', error);
        this.message = '네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },
    
    async resendVerificationEmail() {
      this.resendLoading = true;
      this.message = '';
      
      try {
        const response = await fetch('http://127.0.0.1:8000/resend-verification', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: this.registeredEmail
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.message = '인증 메일이 다시 발송되었습니다. 이메일을 확인해주세요.';
          this.messageType = 'success';
        } else {
          this.message = data.detail || '인증 메일 발송에 실패했습니다. 다시 시도해주세요.';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('인증 메일 재발송 요청 중 오류 발생:', error);
        this.message = '네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        this.messageType = 'error';
      } finally {
        this.resendLoading = false;
      }
    },
    
    goBackToRegister() {
      this.showEmailVerification = false;
      this.registeredEmail = '';
      this.registeredUsername = '';
      this.message = '';
    }
  }
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: #ffffff;
}

/* 브랜드 섹션 */
.brand-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.brand-content {
  max-width: 500px;
  width: 100%;
}

.brand-header {
  text-align: center;
  margin-bottom: 3rem;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 1.125rem;
  color: #616161;
  margin-bottom: 0;
}

.benefits-list {
  margin-bottom: 3rem;
}

.benefit-item {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #424242;
  transition: transform 0.2s ease;
}

.benefit-item:hover {
  transform: translateX(5px);
}

.stats-section {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  padding: 0 1rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1976D2;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #616161;
}

/* 폼 섹션 */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: #ffffff;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 2rem;
}

.mobile-brand {
  text-align: center;
}

.mobile-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1rem;
  color: #616161;
  margin-bottom: 0;
}

.register-form {
  margin-bottom: 1rem;
  animation: fadeInUp 0.6s ease-out;
}

.terms-section {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.terms-text {
  font-size: 0.875rem;
  color: #424242;
  line-height: 1.5;
}

.terms-link {
  color: #1976D2;
  text-decoration: underline;
  font-weight: 500;
}

.terms-link:hover {
  color: #1565C0;
}

.register-btn {
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.02em;
}

.divider-text {
  background: #ffffff;
  padding: 0 1rem;
  color: #9e9e9e;
  font-size: 0.875rem;
}

.login-section {
  text-align: center;
}

.login-text {
  color: #616161;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.login-btn {
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.02em;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .brand-title {
    font-size: 2rem;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
  
  .form-section {
    padding: 1.5rem;
  }
}

@media (max-width: 600px) {
  .brand-title {
    font-size: 1.75rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .form-section {
    padding: 1rem;
  }
  
  .stats-section {
    flex-direction: column;
    gap: 1rem;
  }
}

/* 애니메이션 효과 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-btn {
  transition: all 0.2s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
}

/* 폼 필드 애니메이션 */
.v-text-field {
  transition: all 0.3s ease;
}

.v-text-field:focus-within {
  transform: scale(1.01);
}

/* 체크박스 애니메이션 */
.v-checkbox {
  transition: all 0.2s ease;
}

.v-checkbox:hover {
  transform: scale(1.02);
}

/* 브랜드 섹션 애니메이션 */
.brand-content {
  animation: fadeInLeft 0.8s ease-out;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 통계 섹션 애니메이션 */
.stat-item {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.stat-item:nth-child(1) { animation-delay: 0.1s; }
.stat-item:nth-child(2) { animation-delay: 0.2s; }
.stat-item:nth-child(3) { animation-delay: 0.3s; }

/* 혜택 리스트 애니메이션 */
.benefit-item {
  animation: fadeInUp 0.5s ease-out;
  animation-fill-mode: both;
}

.benefit-item:nth-child(1) { animation-delay: 0.1s; }
.benefit-item:nth-child(2) { animation-delay: 0.15s; }
.benefit-item:nth-child(3) { animation-delay: 0.2s; }
.benefit-item:nth-child(4) { animation-delay: 0.25s; }
.benefit-item:nth-child(5) { animation-delay: 0.3s; }
.benefit-item:nth-child(6) { animation-delay: 0.35s; }

/* 로딩 상태 스타일 */
.v-btn.v-btn--loading {
  pointer-events: none;
}

/* 에러 상태 애니메이션 */
.v-text-field.v-input--error {
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 성공 메시지 애니메이션 */
.v-alert.v-alert--variant-tonal.v-alert--type-success {
  animation: slideInDown 0.5s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 이메일 인증 섹션 스타일 */
.email-verification-section {
  text-align: center;
  padding: 2rem 0;
  animation: fadeInUp 0.6s ease-out;
}

.verification-header {
  margin-bottom: 2rem;
}

.verification-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.verification-subtitle {
  font-size: 1rem;
  color: #616161;
  margin-bottom: 0;
}

.verification-content {
  text-align: left;
}

.verification-steps {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.verification-steps li {
  padding: 0.25rem 0;
  position: relative;
  padding-left: 1.5rem;
}

.verification-steps li:before {
  content: '•';
  color: #1976D2;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.verification-actions {
  margin-top: 1.5rem;
}

/* 이메일 인증 섹션 애니메이션 */
.email-verification-section {
  animation: fadeInScale 0.6s ease-out;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 재발송 버튼 호버 효과 */
.verification-actions .v-btn {
  transition: all 0.3s ease;
}

.verification-actions .v-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>