<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-6" elevation="8">
          <!-- 헤더 -->
          <div class="text-center mb-6">
            <v-icon size="64" color="primary" class="mb-4">mdi-lock-reset</v-icon>
            <h1 class="text-h4 font-weight-bold mb-2">비밀번호 찾기</h1>
            <p class="text-subtitle-1 text-grey-darken-1">
              계정 정보를 입력하시면 새로운 비밀번호를 발급해드립니다
            </p>
          </div>

          <!-- 성공 메시지 -->
          <v-alert
            v-if="resetSuccess"
            type="success"
            variant="tonal"
            class="mb-4">
            <div class="text-body-1 font-weight-medium mb-2">
              {{ resetMessage }}
            </div>
            <div v-if="newPassword" class="text-body-2">
              <strong>새 비밀번호: {{ newPassword }}</strong>
              <br>
              <small class="text-grey-darken-1">
                보안을 위해 로그인 후 비밀번호를 변경해주세요
              </small>
            </div>
          </v-alert>

          <!-- 에러 메시지 -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="errorMessage = ''">
            {{ errorMessage }}
          </v-alert>

          <!-- 비밀번호 재설정 폼 -->
          <v-form v-if="!resetSuccess" ref="resetForm" @submit.prevent="resetPassword">
            <v-text-field
              v-model="username"
              label="사용자명"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              :rules="usernameRules"
              required
              class="mb-4">
            </v-text-field>

            <v-text-field
              v-model="email"
              label="이메일"
              prepend-inner-icon="mdi-email"
              variant="outlined"
              type="email"
              :rules="emailRules"
              required
              class="mb-6">
            </v-text-field>

            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="!isFormValid">
              비밀번호 재설정
            </v-btn>
          </v-form>

          <!-- 성공 후 액션 버튼들 -->
          <div v-if="resetSuccess" class="text-center">
            <v-btn
              color="primary"
              size="large"
              class="mr-2"
              @click="goToLogin">
              로그인하기
            </v-btn>
            <v-btn
              variant="outlined"
              color="primary"
              size="large"
              @click="resetForm">
              다른 계정 찾기
            </v-btn>
          </div>

          <!-- 하단 링크 -->
          <div class="text-center mt-6" v-if="!resetSuccess">
            <p class="text-body-2 text-grey-darken-1">
              계정이 기억나셨나요?
              <router-link to="/login" class="text-primary text-decoration-none font-weight-medium">
                로그인하기
              </router-link>
            </p>
            <p class="text-body-2 text-grey-darken-1 mt-2">
              계정이 없으신가요?
              <router-link to="/register" class="text-primary text-decoration-none font-weight-medium">
                회원가입하기
              </router-link>
            </p>
          </div>
        </v-card>
        
        <!-- 도움말 카드 -->
        <v-card class="mt-4 pa-4" elevation="2" v-if="!resetSuccess">
          <div class="d-flex align-start">
            <v-icon color="info" class="mr-3 mt-1">mdi-information</v-icon>
            <div>
              <h3 class="text-h6 mb-2">도움이 필요하신가요?</h3>
              <ul class="text-body-2 text-grey-darken-1">
                <li>가입 시 사용한 정확한 사용자명과 이메일을 입력해주세요</li>
                <li>관리자 계정의 경우: 사용자명 'admin', 이메일 'admin@example.com'</li>
                <li>문제가 지속되면 관리자에게 문의해주세요</li>
              </ul>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PasswordReset',
  data() {
    return {
      username: '',
      email: '',
      loading: false,
      resetSuccess: false,
      errorMessage: '',
      resetMessage: '',
      newPassword: '',
      
      usernameRules: [
        v => !!v || '사용자명을 입력해주세요',
        v => (v && v.length >= 2) || '사용자명은 2자 이상이어야 합니다'
      ],
      emailRules: [
        v => !!v || '이메일을 입력해주세요',
        v => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
      ]
    };
  },
  
  computed: {
    isFormValid() {
      return this.username.length >= 2 && 
             this.email.length > 0 && 
             /.+@.+\..+/.test(this.email);
    }
  },
  
  methods: {
    async resetPassword() {
      if (!this.$refs.resetForm.validate()) return;
      
      this.loading = true;
      this.errorMessage = '';
      
      try {
        const response = await axios.post('http://127.0.0.1:8000/reset-password', {
          username: this.username,
          email: this.email
        });
        
        this.resetSuccess = true;
        this.resetMessage = response.data.message;
        this.newPassword = response.data.new_password;
        
        // 자동으로 새 비밀번호를 클립보드에 복사 (가능한 경우)
        if (this.newPassword && navigator.clipboard) {
          try {
            await navigator.clipboard.writeText(this.newPassword);
            this.$nextTick(() => {
              // 성공 메시지에 복사 완료 알림 추가
              if (this.resetMessage) {
                this.resetMessage += ' (새 비밀번호가 클립보드에 복사되었습니다)';
              }
            });
          } catch (e) {
            console.log('클립보드 복사 실패:', e);
          }
        }
        
      } catch (error) {
        console.error('비밀번호 재설정 오류:', error);
        
        if (error.response) {
          this.errorMessage = error.response.data.detail || '비밀번호 재설정에 실패했습니다.';
        } else if (error.request) {
          this.errorMessage = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
        } else {
          this.errorMessage = '알 수 없는 오류가 발생했습니다.';
        }
      } finally {
        this.loading = false;
      }
    },
    
    goToLogin() {
      this.$router.push('/login');
    },
    
    resetForm() {
      this.resetSuccess = false;
      this.username = '';
      this.email = '';
      this.errorMessage = '';
      this.resetMessage = '';
      this.newPassword = '';
      
      this.$nextTick(() => {
        if (this.$refs.resetForm) {
          this.$refs.resetForm.resetValidation();
        }
      });
    }
  }
};
</script>

<style scoped>
.v-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.v-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.v-icon {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.text-primary {
  transition: all 0.3s ease;
}

.text-primary:hover {
  text-decoration: underline !important;
}

.v-btn {
  border-radius: 8px;
  text-transform: none;
  font-weight: 600;
}

.v-text-field {
  border-radius: 8px;
}

.v-alert {
  border-radius: 8px;
}

/* 애니메이션 효과 */
.v-card {
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-alert {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

ul {
  padding-left: 20px;
}

ul li {
  margin-bottom: 4px;
  line-height: 1.4;
}
</style>