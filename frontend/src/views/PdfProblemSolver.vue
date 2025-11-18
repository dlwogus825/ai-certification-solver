<template>
  <div class="problem-solver-container">
    <!-- 헤더 -->
    <div class="hero-header">
      <v-container class="px-6 py-8">
        <div class="d-flex justify-space-between align-center flex-wrap gap-4">
          <div class="hero-content">
            <div class="d-flex align-center mb-4">
              <div class="hero-icon-wrapper">
                <v-icon size="48" color="white">mdi-brain</v-icon>
              </div>
              <div class="ml-4">
                <h1 class="hero-title">문제 풀이 세션</h1>
                <p class="hero-subtitle mb-0">AI가 추출한 문제로 당신의 실력을 측정해보세요</p>
              </div>
            </div>
          </div>
          <div class="progress-section">
            <v-card v-if="questions.length > 0" class="progress-card" elevation="0">
              <v-card-text class="pa-4">
                <div class="text-center mb-2">
                  <div class="progress-number">{{ currentQuestionIndex + 1 }}</div>
                  <div class="progress-total">총 {{ questions.length }}문제</div>
                </div>
                <v-progress-linear
                  :model-value="((currentQuestionIndex + 1) / questions.length) * 100"
                  color="primary"
                  height="8"
                  rounded
                  class="mb-2">
                </v-progress-linear>
                <div class="text-caption text-center">
                  {{ Math.round(((currentQuestionIndex + 1) / questions.length) * 100) }}% 완료
                </div>
              </v-card-text>
            </v-card>
          </div>
        </div>
      </v-container>
    </div>

    <!-- 메인 컨텐츠 -->
    <v-container class="px-6 pb-8">
      <v-row justify="center">
        <v-col cols="12" lg="10" xl="8">
          <v-card class="main-content-card" elevation="0" rounded="20">
            <v-card-text class="pa-0">
              <!-- 로딩 및 에러 상태 -->
              <div v-if="loading" class="loading-state">
                <div class="loading-content">
                  <div class="loading-icon-wrapper">
                    <v-progress-circular size="80" color="primary" indeterminate width="6"></v-progress-circular>
                  </div>
                  <h3 class="loading-title">문제를 불러오고 있습니다</h3>
                  <p class="loading-description">잠시만 기다려주세요</p>
                </div>
              </div>
              
              <div v-else-if="error" class="error-state">
                <div class="error-content">
                  <div class="error-icon-wrapper">
                    <v-icon size="72" color="error">mdi-alert-circle-outline</v-icon>
                  </div>
                  <h3 class="error-title">문제를 불러올 수 없습니다</h3>
                  <p class="error-description">{{ error }}</p>
                  <v-btn color="primary" variant="flat" @click="$router.go(-1)" class="mt-4">
                    <v-icon start>mdi-arrow-left</v-icon>
                    뒤로 가기
                  </v-btn>
                </div>
              </div>
              
              <div v-else-if="!loading && !error && questions.length === 0" class="empty-state">
                <div class="empty-content">
                  <div class="empty-icon-wrapper">
                    <v-icon size="72" color="grey-lighten-1">mdi-file-question-outline</v-icon>
                  </div>
                  <h3 class="empty-title">문제가 준비되지 않았습니다</h3>
                  <p class="empty-description">이 문서에서 추출된 문제가 아직 없습니다</p>
                  <v-btn color="primary" variant="outlined" @click="$router.push('/pdf-list')" class="mt-4">
                    <v-icon start>mdi-file-multiple</v-icon>
                    다른 문서 보기
                  </v-btn>
                </div>
              </div>

              <!-- 문제 섹션 -->
              <div v-if="currentQuestion" class="question-section">
                <!-- 문제 제목 -->
                <div class="question-wrapper">
                  <div class="question-header">
                    <div class="question-badge">
                      <v-icon size="20" color="primary">mdi-help-circle</v-icon>
                      <span class="question-label">Question</span>
                    </div>
                  </div>
                  <div class="question-content">
                    <p class="question-text">{{ currentQuestion.question_text }}</p>
                  </div>
                </div>

                <!-- 선택지 섹션 -->
                <div class="options-wrapper" v-if="currentQuestion.options && currentQuestion.options.length > 0">
                  <div class="options-header">
                    <div class="options-badge">
                      <v-icon size="20" color="success">mdi-format-list-bulleted</v-icon>
                      <span class="options-label">Options</span>
                    </div>
                    <div class="options-count">{{ currentQuestion.options.length }}개 선택지</div>
                  </div>
                  <div class="options-grid">
                    <div 
                      v-for="(option, index) in currentQuestion.options" 
                      :key="index"
                      class="option-item"
                      :class="{ 'option-selected': selectedOption === option.id }"
                      @click="selectedOption = option.id">
                      <div class="option-indicator">
                        <div class="option-letter">{{ String.fromCharCode(65 + index) }}</div>
                        <v-icon 
                          v-if="selectedOption === option.id" 
                          color="primary" 
                          size="20"
                          class="option-check">
                          mdi-check-circle
                        </v-icon>
                      </div>
                      <div class="option-content">
                        <p class="option-text">{{ option.option_text || '선택지 내용 없음' }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 액션 버튼 섹션 -->
                <div class="actions-wrapper">
                  <div class="primary-actions">
                    <v-btn
                      color="primary"
                      size="x-large"
                      variant="flat"
                      :disabled="!selectedOption"
                      @click="submitAnswer"
                      class="submit-btn"
                      rounded="12">
                      <v-icon start size="24">mdi-send</v-icon>
                      정답 제출
                    </v-btn>
                    <v-btn
                      color="orange-darken-2"
                      size="x-large"
                      variant="flat"
                      @click="showExplanation"
                      class="explanation-btn"
                      rounded="12">
                      <v-icon start size="24">mdi-lightbulb</v-icon>
                      AI 해설
                    </v-btn>
                  </div>
                  
                  <!-- 네비게이션 -->
                  <div class="navigation-actions">
                    <v-btn
                      :disabled="currentQuestionIndex === 0"
                      @click="prevQuestion"
                      variant="outlined"
                      color="grey-darken-1"
                      size="large"
                      class="nav-btn"
                      rounded="12">
                      <v-icon start>mdi-chevron-left</v-icon>
                      이전
                    </v-btn>
                    
                    <div class="question-navigator">
                      <span class="current-question">{{ currentQuestionIndex + 1 }}</span>
                      <span class="question-separator">/</span>
                      <span class="total-questions">{{ questions.length }}</span>
                    </div>
                    
                    <v-btn
                      :disabled="currentQuestionIndex === questions.length - 1"
                      @click="nextQuestion"
                      variant="outlined"
                      color="grey-darken-1"
                      size="large"
                      class="nav-btn"
                      rounded="12">
                      다음
                      <v-icon end>mdi-chevron-right</v-icon>
                    </v-btn>
                  </div>
                </div>
              </div>

            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- 피드백 스낙바 -->
      <v-snackbar
        v-model="showMessage"
        :color="messageType"
        location="top"
        timeout="4000"
        variant="flat"
        rounded="lg"
        class="feedback-snackbar">
        <div class="d-flex align-center">
          <v-icon class="mr-3" size="24">
            {{ messageType === 'success' ? 'mdi-check-circle' : messageType === 'error' ? 'mdi-close-circle' : 'mdi-information' }}
          </v-icon>
          <span class="text-body-1 font-weight-medium">{{ message }}</span>
        </div>
      </v-snackbar>
    </v-container>
  </div>

  <!-- AI 해설 다이얼로그 -->
  <v-dialog v-model="explanationDialog" max-width="900" scrollable persistent>
    <v-card class="explanation-dialog" rounded="20">
      <div class="explanation-header">
        <div class="explanation-header-content">
          <div class="explanation-icon-wrapper">
            <v-icon size="28" color="white">mdi-lightbulb</v-icon>
          </div>
          <div class="explanation-title-section">
            <h2 class="explanation-title">AI 해설</h2>
            <p class="explanation-subtitle">Claude AI가 생성한 상세 해설입니다</p>
          </div>
        </div>
        <v-btn 
          icon="mdi-close" 
          variant="text" 
          size="large"
          color="white"
          @click="explanationDialog = false"
          class="close-btn">
        </v-btn>
      </div>
      
      <v-divider />
      
      <v-card-text class="explanation-body">
        <div v-if="explanationLoading" class="explanation-loading">
          <div class="loading-animation">
            <v-progress-circular size="80" color="orange-darken-2" indeterminate width="6"></v-progress-circular>
            <div class="loading-dots">
              <span class="dot dot-1"></span>
              <span class="dot dot-2"></span>
              <span class="dot dot-3"></span>
            </div>
          </div>
          <h3 class="loading-title">AI가 해설을 생성하고 있습니다</h3>
          <p class="loading-subtitle">잠시만 기다려주세요</p>
        </div>
        <div v-else class="explanation-content">
          <div v-html="renderedExplanation" class="markdown-content"></div>
        </div>
      </v-card-text>
      
      <v-divider />
      
      <v-card-actions class="explanation-footer">
        <v-spacer></v-spacer>
        <v-btn 
          color="orange-darken-2" 
          variant="flat"
          size="large"
          @click="explanationDialog = false"
          rounded="12"
          class="confirm-btn">
          <v-icon start>mdi-check</v-icon>
          이해했습니다
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
export default {
  name: 'PdfProblemSolver',
  data() {
    return {
      documentId: null,
      questions: [],
      currentQuestionIndex: 0,
      selectedOption: null, // 사용자가 선택한 보기 ID
      loading: false,
      error: null,
      message: '',
      messageType: 'info',
      showMessage: false,
      explanationDialog: false,
      explanationLoading: false,
      explanationText: '',
      explanationCache: {}, // 해설 캐시 저장용
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex];
    },
    renderedExplanation() {
      if (!this.explanationText) return '';
      // 마크다운을 HTML로 변환하고 XSS 공격 방지
      const html = marked(this.explanationText);
      return DOMPurify.sanitize(html);
    }
  },
  async created() {
    this.documentId = this.$route.params.documentId;
    if (this.documentId) {
      await this.fetchQuestionsForDocument(this.documentId);
    } else {
      this.error = '문서 ID가 제공되지 않았습니다. 관리자 페이지를 통해 접근해주세요.';
    }
  },
  methods: {
    async fetchQuestionsForDocument(documentId) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.$router.push({ name: 'Login' });
          return;
        }

        const response = await axios.get(`http://127.0.0.1:8000/ocr-documents/${documentId}/questions`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        this.questions = response.data;
        if (this.questions.length > 0) {
          this.myAnswer = ''; // 첫 문제 로드 시 답변 초기화
          this.selectedOption = null; // 첫 문제 로드 시 선택 초기화
        }
        // 로딩 성공 메시지는 제거 (스낙바 중복 방지)
      } catch (error) {
        console.error('문제 요청 중 오류 발생:', error);
        this.error = '네트워크 오류 또는 서버에 연결할 수 없습니다.';
      } finally {
        this.loading = false;
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
        this.myAnswer = ''; // 문제 변경 시 답변 초기화
        this.selectedOption = null; // 문제 변경 시 선택 초기화
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
        this.myAnswer = ''; // 문제 변경 시 답변 초기화
        this.selectedOption = null; // 문제 변경 시 선택 초기화
      }
    },
    async submitAnswer() {
      if (this.selectedOption === null) {
        this.message = '답을 선택해주세요.';
        this.messageType = 'warning';
        this.showMessage = true;
        return;
      }

      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post('http://localhost:8000/api/v1/problems/submit-answer', {
          question_id: this.currentQuestion.id,
          submitted_answer: this.selectedOption, // 선택된 보기의 ID를 제출
        }, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.data.is_correct) {
          this.message = '정답입니다! 훌륭해요!';
          this.messageType = 'success';
        } else {
          this.message = `아쉭다요. 정답은 ${response.data.correct_answer}번입니다.`;
          this.messageType = 'error';
        }
        this.showMessage = true;
      } catch (error) {
        console.error('답안 제출 오류:', error);
        this.message = '답안 제출 중 오류가 발생했습니다.';
        this.messageType = 'error';
        this.showMessage = true;
      }
    },
    async showExplanation() {
      this.explanationDialog = true;
      
      // 캐시에 해설이 있으면 즉시 표시
      const questionId = this.currentQuestion.id;
      if (this.explanationCache[questionId]) {
        this.explanationText = this.explanationCache[questionId];
        return;
      }
      
      // 캐시에 없으면 API 호출
      this.explanationLoading = true;
      this.explanationText = '';

      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post(`http://localhost:8000/explain/${questionId}`, {}, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        // 해설을 캐시에 저장
        this.explanationText = response.data.explanation;
        this.explanationCache[questionId] = response.data.explanation;
      } catch (error) {
        console.error('해설 요청 오류:', error);
        this.explanationText = '해설을 불러오는 중 오류가 발생했습니다.';
      } finally {
        this.explanationLoading = false;
      }
    },
  },
};
</script>

<style scoped>
/* 컴테이너 및 기본 레이아웃 */
.problem-solver-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.problem-solver-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* 헤더 스타일 */
.hero-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 2;
}

.hero-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
  margin-top: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.progress-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.progress-number {
  font-size: 2rem;
  font-weight: 800;
  color: #667eea;
  line-height: 1;
}

.progress-total {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
}

/* 메인 컨텐츠 카드 */
.main-content-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 1px 3px rgba(0, 0, 0, 0.05) !important;
  position: relative;
  z-index: 2;
  overflow: hidden;
}

.main-content-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

/* 로딩 및 상태 스타일 */
.loading-state,
.error-state,
.empty-state {
  padding: 80px 40px;
  text-align: center;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content,
.error-content,
.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.loading-icon-wrapper,
.error-icon-wrapper,
.empty-icon-wrapper {
  margin-bottom: 24px;
}

.loading-title,
.error-title,
.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1A1D1F;
  margin-bottom: 12px;
}

.loading-description,
.error-description,
.empty-description {
  font-size: 1rem;
  color: #6B7280;
  line-height: 1.6;
}

/* 문제 섹션 스타일 */
.question-section {
  padding: 40px;
}

.question-wrapper {
  margin-bottom: 40px;
}

.question-header {
  margin-bottom: 16px;
}

.question-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.question-label {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.question-content {
  background: #F8FAFB;
  border: 2px solid #E5E7EB;
  border-radius: 16px;
  padding: 32px;
  position: relative;
}

.question-content::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 18px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.question-content:hover::before {
  opacity: 1;
}

.question-text {
  font-size: 1.25rem;
  font-weight: 500;
  line-height: 1.8;
  color: #1A1D1F;
  margin: 0;
  word-break: keep-all;
}

/* 선택지 섹션 스타일 */
.options-wrapper {
  margin-bottom: 48px;
}

.options-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.options-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.options-label {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.options-count {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
}

.options-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .options-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.option-item {
  background: #FFFFFF;
  border: 2px solid #E5E7EB;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.option-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.option-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

.option-item:hover::before {
  transform: scaleY(1);
}

.option-item.option-selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
}

.option-item.option-selected::before {
  transform: scaleY(1);
}

.option-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.option-letter {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  color: #374151;
  transition: all 0.3s ease;
}

.option-selected .option-letter {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.option-check {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #667eea;
  border-radius: 50%;
  padding: 2px;
}

.option-content {
  flex: 1;
}

.option-text {
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.6;
  color: #374151;
  margin: 0;
  word-break: keep-all;
}

.option-selected .option-text {
  color: #1A1D1F;
  font-weight: 600;
}

/* 액션 버튼 섹션 */
.actions-wrapper {
  padding: 32px;
  background: #F9FAFB;
  border-radius: 20px;
  border: 1px solid #E5E7EB;
}

.primary-actions {
  display: grid;
  gap: 16px;
  margin-bottom: 32px;
  grid-template-columns: 1fr 1fr;
}

@media (max-width: 768px) {
  .primary-actions {
    grid-template-columns: 1fr;
  }
}

.submit-btn,
.explanation-btn {
  height: 64px !important;
  font-size: 1.125rem !important;
  font-weight: 700 !important;
  text-transform: none !important;
  letter-spacing: -0.01em !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  position: relative;
  overflow: hidden;
}

.submit-btn:hover:not(:disabled),
.explanation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

.submit-btn:disabled {
  opacity: 0.6;
  transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}

/* 네비게이션 액션 */
.navigation-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.nav-btn {
  height: 48px !important;
  min-width: 100px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
  flex-shrink: 0;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.question-navigator {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 20px;
  min-width: 100px;
}

.current-question {
  font-size: 1.5rem;
  font-weight: 800;
  color: #667eea;
}

.question-separator {
  font-size: 1.25rem;
  color: #D1D5DB;
  margin: 0 8px;
}

.total-questions {
  font-size: 1rem;
  font-weight: 600;
  color: #6B7280;
}

/* 피드백 스낙바 */
.feedback-snackbar {
  font-weight: 600 !important;
  letter-spacing: -0.01em !important;
}

.feedback-snackbar .v-snackbar__wrapper {
  border-radius: 12px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

/* AI 해설 다이얼로그 */
.explanation-dialog {
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 152, 0, 0.2) !important;
  overflow: hidden;
}

.explanation-header {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  padding: 24px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.explanation-header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.explanation-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.explanation-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.explanation-subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 4px 0 0 0;
  font-weight: 500;
}

.close-btn {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1) !important;
}

.explanation-body {
  padding: 48px !important;
  min-height: 300px;
  background: #FFFFFF;
}

.explanation-loading {
  text-align: center;
  padding: 40px 20px;
}

.loading-animation {
  position: relative;
  display: inline-block;
  margin-bottom: 32px;
}

.loading-dots {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff9800;
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.dot-1 { animation-delay: -0.32s; }
.dot-2 { animation-delay: -0.16s; }
.dot-3 { animation-delay: 0s; }

@keyframes loading-bounce {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.6; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1A1D1F;
  margin-bottom: 8px;
}

.loading-subtitle {
  font-size: 1rem;
  color: #6B7280;
}

.explanation-content {
  line-height: 1.8;
  font-size: 1.0625rem;
}

.explanation-footer {
  background: #F9FAFB;
  padding: 24px 32px !important;
  border-top: 1px solid #E5E7EB;
}

.confirm-btn {
  height: 48px !important;
  font-size: 1.0625rem !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2) !important;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .hero-header {
    padding: 20px 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-icon-wrapper {
    width: 60px;
    height: 60px;
  }
  
  .question-section {
    padding: 24px;
  }
  
  .question-content {
    padding: 24px;
  }
  
  .question-text {
    font-size: 1.125rem;
  }
  
  .actions-wrapper {
    padding: 24px;
  }
  
  .navigation-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .nav-btn {
    width: 100%;
    min-width: auto !important;
  }
  
  .explanation-body {
    padding: 32px 24px !important;
  }
  
  .explanation-header {
    padding: 20px 24px;
  }
}

/* 애니메이션 */
.question-section,
.options-wrapper,
.actions-wrapper {
  animation: fadeInUp 0.6s ease-out;
}

.option-item:nth-child(1) { animation: slideInLeft 0.6s ease-out 0.1s both; }
.option-item:nth-child(2) { animation: slideInRight 0.6s ease-out 0.2s both; }
.option-item:nth-child(3) { animation: slideInLeft 0.6s ease-out 0.3s both; }
.option-item:nth-child(4) { animation: slideInRight 0.6s ease-out 0.4s both; }

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

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: #F3F4F6;
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 5px;
  border: 2px solid #F3F4F6;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
}

/* 마크다운 콘텐츠 스타일 */
.markdown-content {
  font-size: 1.0625rem;
  line-height: 1.8;
  color: #374151;
  max-width: 720px;
  margin: 0 auto;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin-top: 32px;
  margin-bottom: 16px;
  font-weight: 700;
  line-height: 1.4;
  color: #1A1D1F;
  letter-spacing: -0.01em;
}

.markdown-content h1 { font-size: 2rem; }
.markdown-content h2 { font-size: 1.75rem; }
.markdown-content h3 { font-size: 1.5rem; }
.markdown-content h4 { font-size: 1.25rem; }

.markdown-content h1:first-child,
.markdown-content h2:first-child,
.markdown-content h3:first-child {
  margin-top: 0;
}

.markdown-content p {
  margin-bottom: 20px;
  word-break: keep-all;
}

.markdown-content ul,
.markdown-content ol {
  margin-bottom: 20px;
  padding-left: 0;
}

.markdown-content li {
  margin-bottom: 12px;
  padding-left: 32px;
  position: relative;
  line-height: 1.8;
}

.markdown-content ul li::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 12px;
  width: 6px;
  height: 6px;
  background: #ff9800;
  border-radius: 50%;
}

.markdown-content strong {
  font-weight: 700;
  color: #1A1D1F;
  background: linear-gradient(to bottom, transparent 60%, rgba(255, 152, 0, 0.2) 60%);
  padding: 0 2px;
}

.markdown-content em {
  font-style: italic;
  color: #6B7280;
}

.markdown-content code {
  background: #FEF3C7;
  color: #92400e;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: 0.9375rem;
  font-weight: 600;
}

.markdown-content pre {
  background: #1F2937;
  color: #F9FAFB;
  padding: 24px;
  border-radius: 12px;
  overflow-x: auto;
  margin: 24px 0;
  border: 1px solid #374151;
}

.markdown-content pre code {
  background: transparent;
  color: #F9FAFB;
  padding: 0;
  font-weight: 400;
}

.markdown-content blockquote {
  border-left: 4px solid #ff9800;
  padding: 16px 0 16px 24px;
  margin: 24px 0;
  background: rgba(255, 152, 0, 0.05);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  color: #6B7280;
}

.markdown-content hr {
  border: none;
  border-top: 2px solid #E5E7EB;
  margin: 32px 0;
}

.markdown-content a {
  color: #ff9800;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 152, 0, 0.3);
  transition: border-color 0.2s ease;
}

.markdown-content a:hover {
  border-bottom-color: #ff9800;
}

.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E5E7EB;
}

.markdown-content th,
.markdown-content td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #E5E7EB;
}

.markdown-content th {
  background: #F9FAFB;
  font-weight: 700;
  color: #374151;
}

.markdown-content tr:last-child td {
  border-bottom: none;
}

/* 글로벌 오버라이드 */
.v-btn {
  text-transform: none !important;
  letter-spacing: -0.01em !important;
}

.v-progress-linear {
  border-radius: 10px !important;
}

.v-progress-circular {
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
}

.v-card {
  border-radius: 16px !important;
}

.v-divider {
  opacity: 0.3;
}

/* 상호작용 효과 */
.submit-btn:active {
  transform: scale(0.98);
}

.option-item:active {
  transform: scale(0.98);
}

/* 접근성 */
.option-item:focus-visible,
.submit-btn:focus-visible,
.explanation-btn:focus-visible,
.nav-btn:focus-visible {
  outline: 3px solid rgba(102, 126, 234, 0.5);
  outline-offset: 2px;
}
</style>