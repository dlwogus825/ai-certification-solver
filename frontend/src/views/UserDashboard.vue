<template>
  <div class="dashboard-container">
    <!-- 헤더 섹션 -->
    <div class="welcome-header">
      <v-container class="pa-8">
        <v-row align="center">
          <v-col cols="12" md="8">
            <div class="welcome-content">
              <h1 class="display-1 font-weight-bold mb-2">
                안녕하세요, {{ user.username }}님! 👋
              </h1>
              <p class="text-h6 text-grey-darken-1 mb-4">
                오늘도 학습에 도전해보세요
              </p>
              <div class="user-info">
                <v-chip 
                  prepend-icon="mdi-email" 
                  color="primary" 
                  variant="tonal" 
                  class="mr-2">
                  {{ user.email }}
                </v-chip>
                <v-chip 
                  prepend-icon="mdi-calendar" 
                  color="success" 
                  variant="tonal">
                  {{ formatDate(new Date()) }}
                </v-chip>
              </div>
            </div>
          </v-col>
          <v-col cols="12" md="4" class="text-center">
            <div class="profile-section">
              <v-avatar size="120" class="mb-4 profile-avatar">
                <v-img 
                  v-if="profilePictureUrl" 
                  :src="`http://127.0.0.1:8000${profilePictureUrl}`"
                  cover>
                </v-img>
                <v-icon v-else size="60" color="grey-lighten-1">mdi-account-circle</v-icon>
              </v-avatar>
              <div class="text-h6 font-weight-medium">{{ user.username }}</div>
              <div class="text-body-2 text-grey-darken-1">학습자</div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- 통계 카드 섹션 -->
    <v-container class="pa-8">
      <v-row class="mb-8">
        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4 text-center stat-card" color="primary" variant="tonal" elevation="2">
            <v-icon size="48" color="primary" class="mb-2">mdi-book-open-page-variant</v-icon>
            <div class="text-h4 font-weight-bold text-primary">{{ stats.solvedProblems }}</div>
            <div class="text-body-2">해결한 문제</div>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4 text-center stat-card" color="success" variant="tonal" elevation="2">
            <v-icon size="48" color="success" class="mb-2">mdi-trophy</v-icon>
            <div class="text-h4 font-weight-bold text-success">{{ stats.correctRate }}%</div>
            <div class="text-body-2">정답률</div>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4 text-center stat-card" color="warning" variant="tonal" elevation="2">
            <v-icon size="48" color="warning" class="mb-2">mdi-fire</v-icon>
            <div class="text-h4 font-weight-bold text-warning">{{ stats.streak }}</div>
            <div class="text-body-2">연속 학습일</div>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4 text-center stat-card" color="info" variant="tonal" elevation="2">
            <v-icon size="48" color="info" class="mb-2">mdi-clock-outline</v-icon>
            <div class="text-h4 font-weight-bold text-info">{{ stats.studyTime }}h</div>
            <div class="text-body-2">총 학습시간</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- 빠른 액션 카드들 -->
      <div class="mb-6">
        <h2 class="text-h5 font-weight-bold mb-4">
          <v-icon size="28" color="primary" class="mr-2">mdi-lightning-bolt</v-icon>
          빠른 시작
        </h2>
        
        <v-row>
          <v-col cols="12" md="4">
            <v-card 
              class="action-card pa-6 text-center" 
              elevation="3"
              @click="goToPdfList"
              hover>
              <div class="action-icon-wrapper mb-4">
                <v-icon size="64" color="primary">mdi-file-document-multiple</v-icon>
              </div>
              <v-card-title class="justify-center text-h6 font-weight-bold mb-2">
                문제 풀기
              </v-card-title>
              <v-card-text class="text-body-2 text-grey-darken-1">
                업로드된 PDF에서 추출된 문제들을 풀어보세요
              </v-card-text>
              <v-btn 
                color="primary" 
                variant="flat" 
                size="large"
                class="mt-3">
                시작하기
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card 
              class="action-card pa-6 text-center" 
              elevation="3"
              @click="goToProfile"
              hover>
              <div class="action-icon-wrapper mb-4">
                <v-icon size="64" color="success">mdi-account-cog</v-icon>
              </div>
              <v-card-title class="justify-center text-h6 font-weight-bold mb-2">
                프로필 관리
              </v-card-title>
              <v-card-text class="text-body-2 text-grey-darken-1">
                개인정보를 수정하고 프로필 사진을 업데이트하세요
              </v-card-text>
              <v-btn 
                color="success" 
                variant="flat" 
                size="large"
                class="mt-3">
                설정하기
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card 
              class="action-card pa-6 text-center" 
              elevation="3"
              @click="goToAnnouncements"
              hover>
              <div class="action-icon-wrapper mb-4">
                <v-icon size="64" color="warning">mdi-bulletin-board</v-icon>
              </div>
              <v-card-title class="justify-center text-h6 font-weight-bold mb-2">
                공지사항
              </v-card-title>
              <v-card-text class="text-body-2 text-grey-darken-1">
                최신 소식과 중요한 공지사항을 확인하세요
              </v-card-text>
              <v-btn 
                color="warning" 
                variant="flat" 
                size="large"
                class="mt-3">
                확인하기
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- 최근 활동 섹션 -->
      <div class="mb-6">
        <h2 class="text-h5 font-weight-bold mb-4">
          <v-icon size="28" color="primary" class="mr-2">mdi-history</v-icon>
          최근 활동
        </h2>
        
        <v-row>
          <v-col cols="12" md="6">
            <v-card class="pa-4" elevation="2">
              <v-card-title class="text-h6 mb-3">
                <v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
                학습 진도
              </v-card-title>
              <v-card-text>
                <div class="mb-4">
                  <div class="d-flex justify-space-between mb-2">
                    <span class="text-body-2">전체 진도</span>
                    <span class="text-body-2 font-weight-bold">{{ stats.overallProgress }}%</span>
                  </div>
                  <v-progress-linear 
                    :model-value="stats.overallProgress" 
                    color="primary" 
                    height="8" 
                    rounded>
                  </v-progress-linear>
                </div>
                
                <div class="mb-4">
                  <div class="d-flex justify-space-between mb-2">
                    <span class="text-body-2">이번 주 목표</span>
                    <span class="text-body-2 font-weight-bold">{{ stats.weeklyProgress }}%</span>
                  </div>
                  <v-progress-linear 
                    :model-value="stats.weeklyProgress" 
                    color="success" 
                    height="8" 
                    rounded>
                  </v-progress-linear>
                </div>
                
                <v-btn 
                  color="primary" 
                  variant="outlined" 
                  size="small"
                  @click="viewDetailedProgress">
                  자세히 보기
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-card class="pa-4" elevation="2">
              <v-card-title class="text-h6 mb-3">
                <v-icon class="mr-2" color="success">mdi-bookmark</v-icon>
                최근 학습 기록
              </v-card-title>
              <v-card-text>
                <v-list density="compact">
                  <v-list-item 
                    v-for="activity in recentActivities" 
                    :key="activity.id"
                    class="pa-2">
                    <template v-slot:prepend>
                      <v-icon :color="activity.color">{{ activity.icon }}</v-icon>
                    </template>
                    <v-list-item-title class="text-body-2">
                      {{ activity.title }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="text-caption">
                      {{ activity.time }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                
                <v-btn 
                  color="success" 
                  variant="outlined" 
                  size="small"
                  class="mt-2"
                  @click="viewAllActivities">
                  전체 기록 보기
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- 학습 목표 섹션 -->
      <div>
        <h2 class="text-h5 font-weight-bold mb-4">
          <v-icon size="28" color="primary" class="mr-2">mdi-target</v-icon>
          오늘의 학습 목표
        </h2>
        
        <v-card class="pa-6" elevation="2">
          <v-row>
            <v-col cols="12" md="8">
              <div class="mb-4">
                <h3 class="text-h6 font-weight-medium mb-2">일일 문제 풀이 목표</h3>
                <p class="text-body-2 text-grey-darken-1 mb-3">
                  오늘 {{ stats.dailyGoal }}문제 중 {{ stats.dailyCompleted }}문제를 완료했습니다!
                </p>
                <v-progress-linear 
                  :model-value="(stats.dailyCompleted / stats.dailyGoal) * 100" 
                  color="primary" 
                  height="12" 
                  rounded>
                </v-progress-linear>
              </div>
              
              <div class="d-flex gap-3">
                <v-btn 
                  color="primary" 
                  variant="flat"
                  @click="startDailyChallenege">
                  오늘의 도전 시작
                  <v-icon end>mdi-rocket-launch</v-icon>
                </v-btn>
                <v-btn 
                  color="primary" 
                  variant="outlined"
                  @click="setGoals">
                  목표 설정
                </v-btn>
              </div>
            </v-col>
            
            <v-col cols="12" md="4" class="text-center">
              <div class="goal-visual">
                <v-progress-circular
                  :model-value="(stats.dailyCompleted / stats.dailyGoal) * 100"
                  :size="120"
                  :width="8"
                  color="primary"
                  class="mb-2">
                  <span class="text-h5 font-weight-bold">
                    {{ Math.round((stats.dailyCompleted / stats.dailyGoal) * 100) }}%
                  </span>
                </v-progress-circular>
                <div class="text-body-2 text-grey-darken-1">
                  {{ stats.dailyCompleted }} / {{ stats.dailyGoal }} 완료
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card>
      </div>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
      user: {
        username: '',
        email: '',
      },
      profilePictureUrl: '',
      stats: {
        solvedProblems: 0,
        correctRate: 0,
        streak: 0,
        studyTime: 0,
        overallProgress: 0,
        weeklyProgress: 0,
        dailyGoal: 5,
        dailyCompleted: 0
      },
      recentActivities: [
        {
          id: 1,
          title: '정보처리기사 문제 5개 완료',
          time: '2시간 전',
          icon: 'mdi-check-circle',
          color: 'success'
        },
        {
          id: 2,
          title: '프로필 정보 업데이트',
          time: '1일 전',
          icon: 'mdi-account-edit',
          color: 'primary'
        },
        {
          id: 3,
          title: '새로운 문제집 추가됨',
          time: '2일 전',
          icon: 'mdi-book-plus',
          color: 'info'
        },
        {
          id: 4,
          title: '7일 연속 학습 달성',
          time: '3일 전',
          icon: 'mdi-trophy',
          color: 'warning'
        }
      ]
    };
  },
  computed: {
    
  },
  async created() {
    await this.fetchUserProfile();
    await this.fetchStats();
    // loadProfilePicture는 이미 fetchUserProfile에서 처리됨
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
          console.log('User data:', this.user); // 디버깅용
          // 프로필 이미지 URL 설정
          if (this.user.profile_picture_url) {
            this.profilePictureUrl = this.user.profile_picture_url;
            localStorage.setItem('profile_picture_url', this.user.profile_picture_url);
          }
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
    
    async fetchStats() {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const response = await fetch('http://127.0.0.1:8000/users/me/profile/stats', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const statsData = await response.json();
          this.stats = {
            solvedProblems: statsData.total_problems_solved,
            correctRate: Math.round(statsData.accuracy_rate),
            streak: statsData.study_streak,
            studyTime: Math.round(parseFloat(statsData.total_study_time.split('시간')[0]) || 0),
            overallProgress: Math.round(statsData.accuracy_rate),
            weeklyProgress: Math.round(statsData.target_achievement_rate),
            dailyGoal: 5, // TODO: 사용자 프로필에서 가져오기
            dailyCompleted: Math.round(statsData.target_achievement_rate / 100 * 5)
          };
        }
      } catch (error) {
        console.error('통계 데이터 가져오기 오류:', error);
      }
    },

    loadProfilePicture() {
      this.profilePictureUrl = localStorage.getItem('profile_picture_url') || '';
    },
    
    // 빠른 액션 메서드들
    goToPdfList() {
      this.$router.push({ name: 'PdfList' });
    },
    
    goToProfile() {
      this.$router.push({ name: 'UserProfile' });
    },
    
    goToAnnouncements() {
      this.$router.push({ name: 'Announcements' });
    },
    
    // 진도 관련 메서드들
    viewDetailedProgress() {
      alert('상세 진도 보기 기능 (개발 예정)');
    },
    
    viewAllActivities() {
      alert('전체 활동 기록 보기 기능 (개발 예정)');
    },
    
    // 목표 관련 메서드들
    startDailyChallenege() {
      alert('오늘의 도전 시작! (개발 예정)');
    },
    
    setGoals() {
      alert('목표 설정 기능 (개발 예정)');
    },
    
    // 유틸리티 메서드들
    formatDate(date) {
      return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      });
    }
  },
};
</script>

<style scoped>
.dashboard-container {
  background: #F8F9FA;
  min-height: 100vh;
}

.welcome-header {
  background: #FFFFFF;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  border-bottom: 1px solid #E8E8E8;
}

.welcome-content h1 {
  color: #212121;
  font-weight: 700;
  font-size: 2rem;
  line-height: 1.2;
}

.welcome-content p {
  color: #616161;
  font-weight: 400;
  font-size: 1.125rem;
}

.profile-section {
  color: #212121;
}

.profile-avatar {
  border: 4px solid #FFFFFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-card {
  transition: all 0.2s ease;
  cursor: pointer;
  border-radius: 12px !important;
  background: #FFFFFF !important;
  border: 1px solid #E8E8E8;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #E0E0E0;
}

.action-card {
  transition: all 0.2s ease;
  cursor: pointer;
  border-radius: 16px !important;
  background: #FFFFFF;
  border: 1px solid #E8E8E8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border-color: #E0E0E0;
}

.action-icon-wrapper {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  background: #F5F5F5;
  border-radius: 16px;
}

.goal-visual {
  background: #F8F9FA;
  border-radius: 12px;
  padding: 24px;
}

.v-progress-linear {
  border-radius: 10px !important;
}

.v-progress-circular {
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

.v-card {
  border-radius: 12px !important;
  background: #FFFFFF !important;
  border: 1px solid #E8E8E8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

.v-list-item {
  border-radius: 12px;
  margin: 2px 0;
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background: #F5F5F5;
  transform: translateX(2px);
}

.v-chip {
  border-radius: 8px !important;
  font-weight: 500;
  font-size: 0.875rem;
}

.v-btn {
  border-radius: 8px !important;
  text-transform: none;
  font-weight: 500;
  letter-spacing: 0.02em;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-container > .v-row > .v-col {
  animation: fadeInUp 0.6s ease-out;
}

.v-container > .v-row:nth-child(2) > .v-col {
  animation-delay: 0.1s;
}

.v-container > .v-row:nth-child(3) > .v-col {
  animation-delay: 0.2s;
}

.v-container > .v-row:nth-child(4) > .v-col {
  animation-delay: 0.3s;
}

/* 모던 스크롤바 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #F5F5F5;
}

::-webkit-scrollbar-thumb {
  background: #BDBDBD;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9E9E9E;
}

/* 프로페셔널 디자인 시스템 */
.text-h4 {
  font-weight: 600;
  color: #212121;
}

.text-h5 {
  font-weight: 600;
  color: #212121;
}

.text-h6 {
  font-weight: 500;
  color: #424242;
}

.text-body-2 {
  color: #616161;
}
</style>