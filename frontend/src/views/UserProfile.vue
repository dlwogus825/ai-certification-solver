<template>
  <div class="profile-container">
    <!-- 헤더 섹션 -->
    <div class="page-header">
      <v-container class="pa-8">
        <div class="header-content">
          <div class="page-title-section clickable" @click="goToHome">
            <div class="page-icon-wrapper">
              <v-icon size="32" color="primary">mdi-account-edit</v-icon>
            </div>
            <div>
              <h1 class="page-title">프로필 관리</h1>
              <p class="page-subtitle">개인정보를 수정하고 학습 목표를 설정하세요</p>
            </div>
          </div>
        </div>
      </v-container>
    </div>

    <v-container class="pa-8">
      <!-- 프로필 헤더 카드 -->
      <v-card class="profile-header-card mb-8" elevation="2">
        <v-card-text class="pa-8">
          <v-row align="center">
            <v-col cols="12" md="4" class="text-center">
              <div class="profile-avatar-section">
                <v-avatar size="160" class="profile-main-avatar mb-4">
                  <v-img 
                    v-if="user.profile_picture_url" 
                    :src="`http://127.0.0.1:8000${user.profile_picture_url}`"
                    cover>
                  </v-img>
                  <v-icon v-else size="80" color="grey-darken-1">mdi-account-circle</v-icon>
                </v-avatar>
                
                <v-file-input
                  v-model="selectedProfileImage"
                  accept="image/*"
                  show-size
                  hide-details
                  density="comfortable"
                  variant="outlined"
                  class="profile-image-input mb-3"
                  prepend-icon=""
                  append-inner-icon="mdi-camera"
                  rounded="lg">
                  <template v-slot:label>
                    <span class="text-body-2">프로필 사진 변경</span>
                  </template>
                </v-file-input>
                
                <v-btn 
                  color="primary" 
                  :loading="imageUploading" 
                  :disabled="!selectedProfileImage"
                  @click="uploadProfileImage"
                  variant="elevated"
                  size="large"
                  rounded="lg">
                  <v-icon class="mr-2">mdi-upload</v-icon>
                  사진 업로드
                </v-btn>
              </div>
            </v-col>
            
            <v-col cols="12" md="8">
              <div class="profile-info">
                <h2 class="profile-username">{{ user.username }}</h2>
                <p class="profile-email">{{ user.email }}</p>
                <div class="profile-badges mt-4">
                  <v-chip 
                    color="primary" 
                    variant="tonal" 
                    prepend-icon="mdi-account"
                    class="mr-2">
                    {{ user.is_admin ? '관리자' : '학습자' }}
                  </v-chip>
                  <v-chip 
                    color="success" 
                    variant="tonal" 
                    prepend-icon="mdi-calendar-check"
                    class="mr-2">
                    가입일: {{ formatDate(user.created_at) }}
                  </v-chip>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-row>
        <!-- 개인정보 수정 카드 -->
        <v-col cols="12" lg="8">
          <v-card class="info-card mb-6" elevation="2">
            <div class="card-header">
              <div class="card-icon-wrapper">
                <v-icon size="24" color="primary">mdi-account-edit-outline</v-icon>
              </div>
              <div class="card-title-section">
                <h3 class="card-title">개인정보 수정</h3>
                <p class="card-subtitle">프로필 정보를 업데이트하세요</p>
              </div>
            </div>
            
            <v-card-text class="pa-6">
            
            <v-form @submit.prevent="updateProfile">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="user.username"
                    label="사용자 이름"
                    prepend-inner-icon="mdi-account"
                    readonly
                    variant="outlined"
                    density="comfortable">
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="user.email"
                    label="이메일"
                    prepend-inner-icon="mdi-email"
                    type="email"
                    required
                    variant="outlined"
                    density="comfortable">
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileData.real_name"
                    label="실명"
                    prepend-inner-icon="mdi-card-account-details"
                    variant="outlined"
                    density="comfortable"
                    hint="실제 이름을 입력해주세요">
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileData.phone"
                    label="전화번호"
                    prepend-inner-icon="mdi-phone"
                    variant="outlined"
                    density="comfortable"
                    placeholder="010-1234-5678">
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-select
                    v-model="profileData.age_group"
                    :items="ageGroups"
                    label="연령대"
                    prepend-inner-icon="mdi-account-clock"
                    variant="outlined"
                    density="comfortable">
                  </v-select>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-select
                    v-model="profileData.education_level"
                    :items="educationLevels"
                    label="학력"
                    prepend-inner-icon="mdi-school"
                    variant="outlined"
                    density="comfortable">
                  </v-select>
                </v-col>
                
                <v-col cols="12">
                  <v-select
                    v-model="profileData.target_certifications"
                    :items="certificationTypes"
                    label="목표 자격증"
                    prepend-inner-icon="mdi-certificate"
                    variant="outlined"
                    density="comfortable"
                    multiple
                    chips
                    hint="관심있는 자격증을 선택해주세요">
                  </v-select>
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="profileData.bio"
                    label="자기소개"
                    prepend-inner-icon="mdi-text"
                    variant="outlined"
                    rows="3"
                    counter="500"
                    hint="간단한 자기소개를 작성해주세요">
                  </v-textarea>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="newPassword"
                    label="새 비밀번호 (변경 시 입력)"
                    prepend-inner-icon="mdi-lock"
                    type="password"
                    variant="outlined"
                    density="comfortable">
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="confirmPassword"
                    label="새 비밀번호 확인"
                    prepend-inner-icon="mdi-lock-check"
                    type="password"
                    v-if="newPassword"
                    variant="outlined"
                    density="comfortable">
                  </v-text-field>
                </v-col>
              </v-row>
              
              <v-alert v-if="message" :type="messageType" class="mt-4" closable>
                {{ message }}
              </v-alert>
              
              <div class="form-actions pt-4">
                <v-btn 
                  color="primary" 
                  size="large"
                  @click="updateProfile"
                  :loading="updating"
                  variant="elevated"
                  rounded="lg">
                  <v-icon class="mr-2">mdi-content-save</v-icon>
                  정보 저장
                </v-btn>
              </div>
            </v-form>
            </v-card-text>
          </v-card>
        </v-col>
        
        <!-- 학습 통계 및 활동 카드 -->
        <v-col cols="12" lg="4">
          <v-card class="stats-card mb-6" elevation="2">
            <div class="card-header">
              <div class="card-icon-wrapper success-icon">
                <v-icon size="24" color="success">mdi-chart-line</v-icon>
              </div>
              <div class="card-title-section">
                <h3 class="card-title">학습 통계</h3>
                <p class="card-subtitle">나의 학습 현황</p>
              </div>
            </div>
            
            <v-card-text class="pa-6">
              <div class="stat-item mb-3">
                <div class="d-flex justify-space-between mb-1">
                  <span class="text-body-2">해결한 문제</span>
                  <span class="text-h6 font-weight-bold text-primary">{{ learningStats.solved_problems }}</span>
                </div>
              </div>
              
              <div class="stat-item mb-3">
                <div class="d-flex justify-space-between mb-1">
                  <span class="text-body-2">정답률</span>
                  <span class="text-h6 font-weight-bold text-success">{{ learningStats.correct_rate }}%</span>
                </div>
                <v-progress-linear 
                  :model-value="learningStats.correct_rate" 
                  color="success" 
                  height="8" 
                  rounded>
                </v-progress-linear>
              </div>
              
              <div class="stat-item mb-3">
                <div class="d-flex justify-space-between mb-1">
                  <span class="text-body-2">연속 학습일</span>
                  <span class="text-h6 font-weight-bold text-warning">{{ learningStats.streak_days }}일</span>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="d-flex justify-space-between mb-1">
                  <span class="text-body-2">총 학습시간</span>
                  <span class="text-h6 font-weight-bold text-info">{{ learningStats.total_study_time }}시간</span>
                </div>
              </div>
            </v-card-text>
          </v-card>
          
          <!-- 학습 목표 카드 -->
          <v-card class="goals-card mb-6" elevation="2">
            <div class="card-header">
              <div class="card-icon-wrapper warning-icon">
                <v-icon size="24" color="warning">mdi-target</v-icon>
              </div>
              <div class="card-title-section">
                <h3 class="card-title">학습 목표</h3>
                <p class="card-subtitle">나의 목표 설정</p>
              </div>
            </div>
            
            <v-card-text class="pa-6">
              <v-text-field
                v-model="profileData.daily_goal"
                label="일일 문제 풀이 목표"
                type="number"
                min="1"
                max="100"
                prepend-inner-icon="mdi-numeric"
                variant="outlined"
                density="compact"
                suffix="문제">
              </v-text-field>
              
              <v-select
                v-model="profileData.study_time_goal"
                :items="studyTimeOptions"
                label="일일 학습시간 목표"
                prepend-inner-icon="mdi-clock"
                variant="outlined"
                density="compact">
              </v-select>
            </v-card-text>
          </v-card>
          
          <!-- 계정 관리 카드 -->
          <v-card class="account-card" elevation="2">
            <div class="card-header">
              <div class="card-icon-wrapper grey-icon">
                <v-icon size="24" color="grey-darken-1">mdi-cog-outline</v-icon>
              </div>
              <div class="card-title-section">
                <h3 class="card-title">계정 관리</h3>
                <p class="card-subtitle">계정 설정 및 관리</p>
              </div>
            </div>
            
            <v-card-text class="pa-6">
              <v-btn 
                color="grey-darken-1" 
                variant="outlined" 
                block 
                class="mb-3"
                rounded="lg"
                @click="logout">
                <v-icon class="mr-2">mdi-logout</v-icon>
                로그아웃
              </v-btn>
              
              <v-btn 
                color="error" 
                variant="outlined" 
                block
                rounded="lg"
                @click="confirmDeleteAccount">
                <v-icon class="mr-2">mdi-account-remove</v-icon>
                회원 탈퇴
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- 회원 탈퇴 확인 다이얼로그 -->
    <v-dialog v-model="deleteDialog" max-width="480" persistent>
      <v-card class="delete-dialog" rounded="lg">
        <!-- 헤더 -->
        <div class="dialog-header">
          <div class="dialog-icon-wrapper">
            <v-icon size="24" color="error">mdi-alert-circle-outline</v-icon>
          </div>
          <div class="dialog-title-section">
            <h3 class="dialog-title">회원 탈퇴</h3>
            <p class="dialog-subtitle">이 작업은 되돌릴 수 없습니다</p>
          </div>
        </div>
        
        <!-- 내용 -->
        <v-card-text class="pa-6">
          <div class="delete-content">
            <p class="delete-message">
              정말로 계정을 탈퇴하시겠습니까?
            </p>
            <v-alert
              type="warning"
              variant="tonal"
              class="mt-4"
              border="start"
              density="compact">
              <template v-slot:prepend>
                <v-icon size="18">mdi-information-outline</v-icon>
              </template>
              <div class="text-body-2">
                • 모든 학습 기록이 삭제됩니다<br>
                • 프로필 정보가 완전히 제거됩니다<br>
                • 이 작업은 되돌릴 수 없습니다
              </div>
            </v-alert>
          </div>
        </v-card-text>
        
        <!-- 액션 버튼 -->
        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            color="grey-darken-1"
            @click="deleteDialog = false">
            취소
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            class="ml-3"
            @click="deleteAccount">
            <v-icon class="mr-2" size="18">mdi-account-remove</v-icon>
            탈퇴하기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      user: {
        username: '',
        email: '',
        profile_picture_url: null,
        is_admin: false,
        created_at: null
      },
      profileData: {
        real_name: '',
        phone: '',
        age_group: '',
        education_level: '',
        target_certifications: [],
        bio: '',
        daily_goal: 5,
        study_time_goal: '1시간'
      },
      learningStats: {
        solved_problems: 23,
        correct_rate: 85,
        streak_days: 7,
        total_study_time: 45
      },
      selectedProfileImage: null,
      imageUploading: false,
      updating: false,
      newPassword: '',
      confirmPassword: '',
      message: '',
      messageType: 'info',
      deleteDialog: false,
      
      // 선택 옵션들
      ageGroups: [
        '10대', '20대', '30대', '40대', '50대', '60대 이상'
      ],
      educationLevels: [
        '고등학교 졸업', '전문대 재학', '전문대 졸업', '대학교 재학', '대학교 졸업', 
        '대학원 재학', '대학원 졸업', '기타'
      ],
      certificationTypes: [
        '정보처리기사', '정보보안기사', '컴활 1급', '컴활 2급',
        'SQLD', 'SQLP', 'ADsP', 'ADP', '빅데이터분석기사',
        '데이터분석준전문가', 'AWS 자격증', 'CCNA', 'LPIC',
        '토익', '토플', '오픽', '기타'
      ],
      studyTimeOptions: [
        '30분', '1시간', '1시간 30분', '2시간', '2시간 30분', 
        '3시간', '3시간 이상'
      ]
    };
  },
  async created() {
    await this.fetchUserProfile();
    await this.loadProfileData();
  },
  methods: {
    async fetchUserProfile() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push({ name: 'Login' });
        return;
      }
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
        } else {
          localStorage.removeItem('access_token');
          this.$router.push({ name: 'Login' });
        }
      } catch (error) {
        console.error('사용자 정보 가져오기 오류:', error);
        localStorage.removeItem('access_token');
        this.$router.push({ name: 'Login' });
      }
    },
    
    async loadProfileData() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      
      try {
        // 프로필 데이터 API 호출
        const profileResponse = await fetch('http://127.0.0.1:8000/users/me/profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          this.profileData = {
            real_name: profileData.real_name || '',
            phone: profileData.phone || '',
            age_group: profileData.age_group || '',
            education_level: profileData.education_level || '',
            target_certifications: profileData.target_certifications || [],
            bio: profileData.bio || '',
            daily_goal: profileData.daily_goal || 5,
            study_time_goal: profileData.study_time_goal || '1시간'
          };
        }
        
        // 학습 통계 API 호출
        const statsResponse = await fetch('http://127.0.0.1:8000/users/me/profile/stats', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (statsResponse.ok) {
          this.learningStats = await statsResponse.json();
        }
      } catch (error) {
        console.error('프로필 데이터 로드 오류:', error);
        // 로컬스토리지 백업 사용
        const savedProfile = localStorage.getItem('user_profile_data');
        if (savedProfile) {
          this.profileData = { ...this.profileData, ...JSON.parse(savedProfile) };
        }
      }
    },
    
    async updateProfile() {
      this.message = '';
      this.updating = true;
      
      if (this.newPassword && this.newPassword !== this.confirmPassword) {
        this.message = '새 비밀번호와 확인 비밀번호가 일치하지 않습니다.';
        this.messageType = 'error';
        this.updating = false;
        return;
      }

      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push({ name: 'Login' });
        this.updating = false;
        return;
      }

      try {
        // 1. 기본 사용자 정보 업데이트 (이메일, 비밀번호)
        const basicUpdateData = {
          email: this.user.email,
        };
        if (this.newPassword) {
          basicUpdateData.password = this.newPassword;
        }

        const basicResponse = await fetch('http://127.0.0.1:8000/users/me', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(basicUpdateData),
        });

        // 2. 프로필 확장 정보 업데이트
        const profileUpdateData = {
          real_name: this.profileData.real_name,
          phone: this.profileData.phone,
          age_group: this.profileData.age_group,
          education_level: this.profileData.education_level,
          target_certifications: this.profileData.target_certifications,
          bio: this.profileData.bio,
          daily_goal: this.profileData.daily_goal,
          study_time_goal: this.profileData.study_time_goal
        };

        const profileResponse = await fetch('http://127.0.0.1:8000/users/me/profile', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileUpdateData),
        });

        if (basicResponse.ok && profileResponse.ok) {
          this.message = '정보가 성공적으로 업데이트되었습니다.';
          this.messageType = 'success';
          this.newPassword = '';
          this.confirmPassword = '';
          
          // 백업용 로컬 저장
          localStorage.setItem('user_profile_data', JSON.stringify(this.profileData));
        } else {
          const basicData = await basicResponse.json();
          const profileData = await profileResponse.json();
          this.message = basicData.detail || profileData.detail || '정보 업데이트에 실패했습니다.';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('정보 업데이트 요청 중 오류 발생:', error);
        this.message = '네트워크 오류 또는 서버에 연결할 수 없습니다.';
        this.messageType = 'error';
      } finally {
        this.updating = false;
      }
    },
    
    async uploadProfileImage() {
      if (!this.selectedProfileImage) return;

      this.imageUploading = true;
      this.message = '';

      const formData = new FormData();
      formData.append('file', this.selectedProfileImage);

      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push({ name: 'Login' });
        this.imageUploading = false;
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/users/me/profile-picture', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        const data = await response.json();

        if (response.ok) {
          this.message = '프로필 사진이 성공적으로 업로드되었습니다.';
          this.messageType = 'success';
          this.user.profile_picture_url = data.profile_picture_url;
          localStorage.setItem('profile_picture_url', data.profile_picture_url);
          this.selectedProfileImage = null;
        } else {
          this.message = data.detail || '프로필 사진 업로드에 실패했습니다.';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('프로필 사진 업로드 요청 중 오류 발생:', error);
        this.message = '네트워크 오류 또는 서버에 연결할 수 없습니다.';
        this.messageType = 'error';
      } finally {
        this.imageUploading = false;
      }
    },
    
    confirmDeleteAccount() {
      this.deleteDialog = true;
    },
    
    async deleteAccount() {
      this.message = '';
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push({ name: 'Login' });
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/users/me', {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 204) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('profile_picture_url');
          localStorage.removeItem('user_profile_data');
          this.$router.push({ name: 'Home' });
        } else {
          const data = await response.json();
          this.message = data.detail || '계정 삭제에 실패했습니다.';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('계정 삭제 요청 중 오류 발생:', error);
        this.message = '네트워크 오류 또는 서버에 연결할 수 없습니다.';
        this.messageType = 'error';
      } finally {
        this.deleteDialog = false;
      }
    },
    
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('profile_picture_url');
      this.$router.push({ name: 'Login' });
    },
    
    formatDate(dateString) {
      if (!dateString) return '정보 없음';
      return new Date(dateString).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    goToHome() {
      // 홈으로 이동하면 라우터 가드가 적절한 대시보드로 리다이렉트
      this.$router.push('/');
    }
  },
};
</script>

<style scoped>
/* 컨테이너 */
.profile-container {
  background: #F8F9FA;
  min-height: 100vh;
}

/* 페이지 헤더 */
.page-header {
  background: #FFFFFF;
  border-bottom: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.page-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title-section.clickable {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.page-title-section.clickable:hover {
  opacity: 0.8;
}

.page-icon-wrapper {
  width: 56px;
  height: 56px;
  background: #E3F2FD;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1A1D1F;
  margin: 0 0 4px 0;
  line-height: 1.3;
}

.page-subtitle {
  font-size: 1rem;
  color: #6B7280;
  margin: 0;
  font-weight: 400;
}

/* 프로필 헤더 카드 */
.profile-header-card {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
}

.profile-main-avatar {
  border: 4px solid #FFFFFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.profile-username {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1A1D1F;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.profile-email {
  font-size: 1.125rem;
  color: #6B7280;
  margin: 0 0 16px 0;
  font-weight: 400;
}

.profile-image-input {
  max-width: 280px;
}

/* 카드 헤더 */
.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #F3F4F6;
}

.card-icon-wrapper {
  width: 48px;
  height: 48px;
  background: #E3F2FD;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.success-icon {
  background: #E8F5E8;
}

.warning-icon {
  background: #FFF8E1;
}

.grey-icon {
  background: #F5F5F5;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1D1F;
  margin: 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 2px 0 0 0;
}

/* 카드 스타일 */
.v-card {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.v-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

/* 통계 아이템 */
.stat-item {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #F3F4F6;
}

/* 폼 액션 */
.form-actions {
  border-top: 1px solid #F3F4F6;
  margin-top: 16px;
}

/* 삭제 다이얼로그 */
.delete-dialog {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 24px 0;
}

.dialog-icon-wrapper {
  width: 48px;
  height: 48px;
  background: #FEF2F2;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1D1F;
  margin: 0;
}

.dialog-subtitle {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 4px 0 0 0;
}

.delete-content {
  margin-top: 8px;
}

.delete-message {
  font-size: 1rem;
  color: #374151;
  margin: 0 0 16px 0;
}

/* 공통 스타일 */
.v-progress-linear {
  border-radius: 6px !important;
}

.v-btn {
  text-transform: none !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
}

.v-chip {
  border-radius: 8px !important;
  font-weight: 500 !important;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-title-section {
    gap: 12px;
  }
  
  .page-icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .profile-username {
    font-size: 1.5rem;
  }
  
  .card-header {
    padding: 16px 20px 12px;
  }
}

/* 애니메이션 */
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

.v-col {
  animation: fadeInUp 0.5s ease-out;
}

.v-col:nth-child(2) {
  animation-delay: 0.1s;
}
</style>