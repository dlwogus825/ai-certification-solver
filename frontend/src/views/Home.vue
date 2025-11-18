<template>
  <div class="home-container">
    <!-- 히어로 섹션 -->
    <section class="hero-section">
      <v-container>
        <v-row align="center" class="hero-row">
          <v-col cols="12" md="6" class="hero-content">
            <v-chip color="primary" variant="tonal" size="small" class="mb-4">
              <v-icon start size="14">mdi-new-box</v-icon>
              AI 기반 학습 플랫폼
            </v-chip>
            
            <h1 class="hero-title">
              자격증 합격을 위한<br>
              <span class="gradient-text">가장 스마트한 선택</span>
            </h1>
            
            <p class="hero-subtitle">
              PDF 기출문제를 업로드하면 AI가 자동으로 문제를 분석하고,
              맞춤형 학습 경험을 제공합니다. 효율적인 학습으로 합격률을 높이세요.
            </p>

            <div class="hero-actions">
              <v-btn 
                color="primary" 
                size="large" 
                elevation="0"
                to="/register" 
                class="mr-4 px-8">
                무료로 시작하기
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>
              <v-btn 
                variant="outlined"
                color="grey-darken-3"
                size="large" 
                to="/login">
                로그인
              </v-btn>
            </div>

            <div class="hero-stats">
              <div class="stat-item">
                <v-icon color="primary">mdi-file-document-check</v-icon>
                <span>1,000+ 문제 분석</span>
              </div>
              <div class="stat-item">
                <v-icon color="primary">mdi-account-group</v-icon>
                <span>500+ 활성 사용자</span>
              </div>
              <div class="stat-item">
                <v-icon color="primary">mdi-star</v-icon>
                <span>95% 만족도</span>
              </div>
            </div>
          </v-col>

          <v-col cols="12" md="6" class="hero-image">
            <div class="hero-visual">
              <div class="floating-card card-1">
                <v-icon size="24" color="primary">mdi-file-pdf-box</v-icon>
                <span>PDF 업로드</span>
              </div>
              <div class="floating-card card-2">
                <v-icon size="24" color="success">mdi-robot</v-icon>
                <span>AI 분석</span>
              </div>
              <div class="floating-card card-3">
                <v-icon size="24" color="warning">mdi-lightbulb</v-icon>
                <span>맞춤 학습</span>
              </div>
              <div class="main-visual">
                <v-icon size="200" color="primary" class="opacity-10">mdi-school</v-icon>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- 특징 섹션 -->
    <section class="features-section">
      <v-container>
        <div class="section-header">
          <h2 class="section-title">왜 우리 플랫폼을 선택해야 할까요?</h2>
          <p class="section-subtitle">
            최신 AI 기술로 당신의 학습 효율을 극대화합니다
          </p>
        </div>

        <v-row>
          <v-col cols="12" md="4" v-for="feature in mainFeatures" :key="feature.id">
            <v-card class="feature-card" elevation="0">
              <v-card-text class="text-center">
                <v-avatar :color="feature.color" size="64" class="mb-4">
                  <v-icon color="white" size="32">{{ feature.icon }}</v-icon>
                </v-avatar>
                <h3 class="feature-title">{{ feature.title }}</h3>
                <p class="feature-description">{{ feature.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- 작동 방식 섹션 -->
    <section class="how-it-works">
      <v-container>
        <div class="section-header">
          <h2 class="section-title">간단한 3단계로 시작하세요</h2>
          <p class="section-subtitle">복잡한 설정 없이 바로 학습을 시작할 수 있습니다</p>
        </div>

        <v-row>
          <v-col cols="12" md="4" v-for="(step, index) in steps" :key="index">
            <div class="step-card">
              <div class="step-number">{{ index + 1 }}</div>
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-description">{{ step.description }}</p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- 통계 섹션 -->
    <section class="stats-section">
      <v-container>
        <v-row>
          <v-col cols="6" md="3" v-for="stat in stats" :key="stat.label" class="text-center">
            <div class="stat-card">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- CTA 섹션 -->
    <section class="cta-section">
      <v-container>
        <v-card class="cta-card" elevation="0">
          <v-card-text class="text-center">
            <h2 class="cta-title">지금 시작하고 합격에 한 걸음 더 가까워지세요</h2>
            <p class="cta-subtitle">
              신용카드 없이 무료로 시작할 수 있습니다
            </p>
            <v-btn 
              color="white" 
              size="x-large" 
              to="/register"
              class="mt-6">
              무료 체험 시작하기
              <v-icon end>mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-text>
        </v-card>
      </v-container>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      mainFeatures: [
        {
          id: 1,
          icon: 'mdi-brain',
          title: 'AI 기반 문제 분석',
          description: '최신 AI 기술로 PDF에서 문제를 자동 추출하고 구조화합니다',
          color: 'primary'
        },
        {
          id: 2,
          icon: 'mdi-chart-line',
          title: '개인 맞춤 학습',
          description: '학습 패턴을 분석하여 최적화된 학습 경로를 제공합니다',
          color: 'success'
        },
        {
          id: 3,
          icon: 'mdi-comment-text',
          title: '상세한 해설 제공',
          description: 'AI가 생성한 상세한 해설로 완벽한 이해를 도와드립니다',
          color: 'warning'
        }
      ],
      steps: [
        {
          title: 'PDF 업로드',
          description: '기출문제 PDF를 간단히 드래그 앤 드롭으로 업로드하세요'
        },
        {
          title: 'AI 분석',
          description: 'AI가 문제를 자동으로 추출하고 카테고리별로 정리합니다'
        },
        {
          title: '학습 시작',
          description: '체계적으로 정리된 문제로 효율적인 학습을 시작하세요'
        }
      ],
      stats: [
        { value: '1,000+', label: '분석된 문제' },
        { value: '95%', label: '사용자 만족도' },
        { value: '500+', label: '활성 사용자' },
        { value: '24/7', label: 'AI 지원' }
      ]
    };
  }
};
</script>

<style scoped>
.home-container {
  background-color: #ffffff;
  min-height: 100vh;
}

/* 히어로 섹션 */
.hero-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 100px 0 80px;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.hero-row {
  min-height: calc(100vh - 180px);
}

.hero-content {
  padding-right: 48px;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.2;
  color: #1a1a1a;
  margin-bottom: 24px;
}

.gradient-text {
  background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.125rem;
  line-height: 1.7;
  color: #616161;
  margin-bottom: 32px;
  max-width: 500px;
}

.hero-actions {
  margin-bottom: 48px;
}

.hero-stats {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #616161;
}

/* 히어로 비주얼 */
.hero-visual {
  position: relative;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-card {
  position: absolute;
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  transition: transform 0.3s ease;
}

.floating-card:hover {
  transform: translateY(-4px);
}

.card-1 {
  top: 20%;
  left: 10%;
  animation: float 3s ease-in-out infinite;
}

.card-2 {
  top: 50%;
  right: 15%;
  animation: float 3s ease-in-out infinite 1s;
}

.card-3 {
  bottom: 20%;
  left: 20%;
  animation: float 3s ease-in-out infinite 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 특징 섹션 */
.features-section {
  padding: 80px 0;
  background-color: #fafafa;
}

.section-header {
  text-align: center;
  margin-bottom: 56px;
}

.section-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.section-subtitle {
  font-size: 1.125rem;
  color: #616161;
  max-width: 600px;
  margin: 0 auto;
}

.feature-card {
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: white;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.feature-description {
  font-size: 0.95rem;
  color: #616161;
  line-height: 1.6;
}

/* 작동 방식 섹션 */
.how-it-works {
  padding: 80px 0;
  background: white;
}

.step-card {
  text-align: center;
  padding: 32px;
  position: relative;
}

.step-number {
  width: 48px;
  height: 48px;
  background: #E3F2FD;
  color: #1976D2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto 24px;
}

.step-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.step-description {
  font-size: 0.95rem;
  color: #616161;
  line-height: 1.6;
}

/* 통계 섹션 */
.stats-section {
  padding: 60px 0;
  background: #f8f9fa;
}

.stat-card {
  padding: 24px;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1976D2;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 1rem;
  color: #616161;
}

/* CTA 섹션 */
.cta-section {
  padding: 80px 0;
  background: white;
}

.cta-card {
  background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
  border-radius: 16px;
  padding: 48px;
}

.cta-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
}

.cta-subtitle {
  font-size: 1.125rem;
  color: rgba(255,255,255,0.9);
  margin-bottom: 32px;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .hero-content {
    padding-right: 0;
    text-align: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    margin: 0 auto 32px;
  }
  
  .hero-stats {
    justify-content: center;
  }
  
  .hero-visual {
    margin-top: 48px;
    height: 300px;
  }
  
  .floating-card {
    font-size: 0.875rem;
    padding: 12px 16px;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .hero-section {
    padding: 60px 0 40px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions .v-btn {
    display: block;
    width: 100%;
    margin-right: 0 !important;
    margin-bottom: 12px;
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .cta-title {
    font-size: 1.5rem;
  }
}
</style>