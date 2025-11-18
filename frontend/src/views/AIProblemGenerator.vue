<template>
  <v-container fluid class="pa-6">
    <!-- 페이지 헤더 -->
    <div class="mb-8">
      <h1 class="text-h3 font-weight-bold mb-2">🤖 AI 문제 생성</h1>
      <p class="text-subtitle-1 text-medium-emphasis">PDF 파일을 업로드하고 AI가 자동으로 문제를 생성합니다</p>
    </div>

    <v-row>
      <!-- 좌측 패널: 파일 업로드 및 설정 -->
      <v-col cols="12" md="6">
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="mr-2">mdi-cloud-upload</v-icon>
            PDF 파일 업로드
          </v-card-title>
          <v-card-text>
            <!-- 파일 업로드 영역 -->
            <div
              class="upload-area"
              :class="{ 'dragover': isDragOver }"
              @drop="handleDrop"
              @dragover.prevent="isDragOver = true"
              @dragleave="isDragOver = false"
              @click="$refs.fileInput.click()"
            >
              <div class="upload-content">
                <v-icon size="64" color="primary" class="mb-4">mdi-file-pdf-box</v-icon>
                <h3 class="mb-2">PDF 파일을 여기에 드롭하거나 클릭하세요</h3>
                <p class="text-medium-emphasis">최대 10MB까지 업로드 가능</p>
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf"
                  @change="handleFileSelect"
                  style="display: none"
                />
              </div>
            </div>

            <!-- 업로드된 파일 정보 -->
            <div v-if="selectedFile" class="mt-4">
              <v-alert type="success" variant="tonal">
                <v-icon class="mr-2">mdi-check-circle</v-icon>
                {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
              </v-alert>
            </div>
          </v-card-text>
        </v-card>

        <!-- 문제 생성 설정 -->
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-cog</v-icon>
            문제 생성 설정
          </v-card-title>
          <v-card-text>
            <!-- 문제 유형 선택 -->
            <div class="mb-4">
              <v-label class="mb-2">문제 유형</v-label>
              <v-chip-group
                v-model="settings.questionTypes"
                multiple
                selected-class="text-primary"
              >
                <v-chip filter variant="outlined" value="multiple_choice">
                  <v-icon start>mdi-format-list-bulleted</v-icon>
                  객관식
                </v-chip>
                <v-chip filter variant="outlined" value="short_answer">
                  <v-icon start>mdi-format-text</v-icon>
                  단답형
                </v-chip>
                <v-chip filter variant="outlined" value="essay">
                  <v-icon start>mdi-format-align-left</v-icon>
                  서술형
                </v-chip>
                <v-chip filter variant="outlined" value="true_false">
                  <v-icon start>mdi-check-bold</v-icon>
                  O/X
                </v-chip>
                <v-chip filter variant="outlined" value="fill_blank">
                  <v-icon start>mdi-format-text-variant</v-icon>
                  빈칸 채우기
                </v-chip>
              </v-chip-group>
            </div>

            <!-- 난이도 설정 -->
            <div class="mb-4">
              <v-label class="mb-2">난이도</v-label>
              <v-btn-toggle
                v-model="settings.difficulty"
                mandatory
                variant="outlined"
                divided
              >
                <v-btn value="beginner">
                  <v-icon start>mdi-school</v-icon>
                  초급
                </v-btn>
                <v-btn value="intermediate">
                  <v-icon start>mdi-graduate-cap</v-icon>
                  중급
                </v-btn>
                <v-btn value="advanced">
                  <v-icon start>mdi-medal</v-icon>
                  고급
                </v-btn>
              </v-btn-toggle>
            </div>

            <!-- 문제 개수 -->
            <div class="mb-4">
              <v-label class="mb-2">생성할 문제 개수: {{ settings.questionCount }}개</v-label>
              <v-slider
                v-model="settings.questionCount"
                :min="5"
                :max="50"
                :step="5"
                track-color="grey-lighten-2"
                thumb-label
                show-ticks="always"
                tick-size="4"
              ></v-slider>
            </div>

            <!-- 언어 설정 -->
            <div class="mb-4">
              <v-select
                v-model="settings.language"
                :items="languageOptions"
                label="문제 언어"
                variant="outlined"
                prepend-inner-icon="mdi-translate"
              ></v-select>
            </div>

            <!-- 고급 설정 -->
            <v-expansion-panels variant="accordion">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon class="mr-2">mdi-tune</v-icon>
                  고급 설정
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-checkbox
                    v-model="settings.includeExplanations"
                    label="정답 해설 포함"
                    color="primary"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="settings.avoidDuplicates"
                    label="중복 문제 방지"
                    color="primary"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="settings.useImages"
                    label="이미지 기반 문제 생성"
                    color="primary"
                  ></v-checkbox>
                  <v-textarea
                    v-model="settings.customPrompt"
                    label="추가 요구사항 (선택사항)"
                    placeholder="예: 특정 주제에 집중해서 문제를 만들어주세요..."
                    variant="outlined"
                    rows="3"
                  ></v-textarea>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 우측 패널: 미리보기 및 결과 -->
      <v-col cols="12" md="6">
        <!-- 생성 버튼 -->
        <div class="mb-4">
          <v-btn
            color="primary"
            size="x-large"
            block
            :loading="isGenerating"
            :disabled="!selectedFile || settings.questionTypes.length === 0"
            @click="generateProblems"
          >
            <v-icon start>mdi-auto-fix</v-icon>
            AI 문제 생성 시작
          </v-btn>
        </div>

        <!-- 진행 상황 -->
        <v-card v-if="isGenerating || generationProgress > 0" class="mb-4">
          <v-card-text>
            <div class="d-flex align-center mb-2">
              <v-icon class="mr-2" color="primary">mdi-robot</v-icon>
              <span class="font-weight-medium">AI가 문제를 생성 중입니다...</span>
            </div>
            <v-progress-linear
              :model-value="generationProgress"
              color="primary"
              height="8"
              rounded
            ></v-progress-linear>
            <div class="text-center mt-2 text-caption">
              {{ progressText }}
            </div>
          </v-card-text>
        </v-card>

        <!-- 생성된 문제 -->
        <v-card v-if="generatedProblems.length > 0">
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon class="mr-2">{{ isSolvingMode ? 'mdi-school' : 'mdi-eye' }}</v-icon>
              {{ isSolvingMode ? '문제 풀이' : '생성된 문제 미리보기' }}
            </div>
            <div class="d-flex align-center gap-2">
              <v-chip color="success" variant="flat">
                {{ generatedProblems.length }}개 완료
              </v-chip>
              <v-btn-toggle v-model="isSolvingMode" variant="outlined">
                <v-btn :value="false" size="small">
                  <v-icon start>mdi-eye</v-icon>
                  미리보기
                </v-btn>
                <v-btn :value="true" size="small">
                  <v-icon start>mdi-school</v-icon>
                  문제 풀이
                </v-btn>
              </v-btn-toggle>
            </div>
          </v-card-title>
          
          <v-card-text>
            <!-- 미리보기 모드 -->
            <div v-if="!isSolvingMode">
              <v-tabs v-model="previewTab" color="primary">
                <v-tab 
                  v-for="(problem, index) in generatedProblems.slice(0, 5)" 
                  :key="index"
                  :value="index"
                >
                  문제 {{ index + 1 }}
                </v-tab>
              </v-tabs>
              <v-window v-model="previewTab" class="mt-4">
                <v-window-item
                  v-for="(problem, index) in generatedProblems.slice(0, 5)"
                  :key="index"
                  :value="index"
                >
                  <ProblemPreview :problem="problem" />
                </v-window-item>
              </v-window>
            </div>
            
            <!-- 문제 풀이 모드 -->
            <div v-else>
              <!-- 디버깅 정보 -->
              <div class="mb-2" style="background: #f5f5f5; padding: 8px; border-radius: 4px; font-size: 12px;">
                디버그: 문제 수={{ generatedProblems.length }}, 풀이모드={{ isSolvingMode }}, 최종결과={{ showFinalResults }}
              </div>
              
              <!-- 진행률 표시 -->
              <div class="mb-4">
                <div class="d-flex align-center justify-space-between mb-2">
                  <span class="font-weight-medium">진행률: {{ solvedCount }}/{{ generatedProblems.length }}</span>
                  <span class="font-weight-medium">점수: {{ totalScore }}/{{ totalPossibleScore }}</span>
                </div>
                <v-progress-linear 
                  :model-value="(solvedCount / generatedProblems.length) * 100"
                  color="primary"
                  height="8"
                  rounded
                ></v-progress-linear>
              </div>
              
              <!-- 문제가 없는 경우 -->
              <div v-if="generatedProblems.length === 0" class="text-center py-8">
                <v-icon size="64" color="grey">mdi-help-circle-outline</v-icon>
                <h3 class="mt-4 mb-2">문제가 없습니다</h3>
                <p class="text-medium-emphasis">먼저 PDF를 업로드하고 문제를 생성해주세요.</p>
              </div>
              
              <!-- 문제 풀이 -->
              <div v-else-if="!showFinalResults && generatedProblems.length > 0">
                <h4 class="mb-4">{{ generatedProblems.length }}개 문제를 풀어보세요!</h4>
                <ProblemSolver
                  v-for="(problem, index) in generatedProblems"
                  :key="`problem-${index}`"
                  :problem="problem"
                  :problem-index="index"
                  @answer-submitted="handleAnswerSubmitted"
                  @answer-changed="handleAnswerChanged"
                />
              </div>
              
              <!-- 최종 결과 -->
              <div v-else>
                <v-alert type="success" variant="tonal" class="mb-4">
                  <h3 class="mb-2">🎉 문제 풀이 완료!</h3>
                  <p class="mb-2">
                    <strong>최종 점수: {{ totalScore }}/{{ totalPossibleScore }} 
                    ({{ Math.round((totalScore/totalPossibleScore) * 100) }}%)</strong>
                  </p>
                  <p class="mb-0">
                    정답: {{ correctCount }}개, 오답: {{ generatedProblems.length - correctCount }}개
                  </p>
                </v-alert>
                
                <v-btn color="primary" @click="resetQuiz" class="mr-2">
                  <v-icon start>mdi-refresh</v-icon>
                  다시 풀기
                </v-btn>
                <v-btn variant="outlined" @click="downloadResults">
                  <v-icon start>mdi-download</v-icon>
                  결과 다운로드
                </v-btn>
              </div>
            </div>
            
            <!-- 액션 버튼들 (미리보기 모드에서만) -->
            <div v-if="!isSolvingMode" class="mt-6">
              <v-btn
                color="primary"
                variant="flat"
                class="mr-2"
                @click="startSolving"
              >
                <v-icon start>mdi-school</v-icon>
                문제 풀기 시작
              </v-btn>
              <v-btn
                color="success"
                variant="outlined"
                class="mr-2"
                @click="downloadProblems"
              >
                <v-icon start>mdi-download</v-icon>
                문제 다운로드
              </v-btn>
              <v-btn
                color="warning"
                variant="outlined"
                @click="regenerateProblems"
              >
                <v-icon start>mdi-refresh</v-icon>
                다시 생성
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- 오류 표시 -->
        <v-alert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          closable
          @click:close="errorMessage = ''"
        >
          <strong>오류 발생:</strong> {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ProblemPreview from '../components/ProblemPreview.vue';
import ProblemSolver from '../components/ProblemSolver.vue';

export default {
  name: 'AIProblemGenerator',
  components: {
    ProblemPreview,
    ProblemSolver
  },
  data() {
    return {
      isDragOver: false,
      selectedFile: null,
      isGenerating: false,
      generationProgress: 0,
      progressText: '',
      generatedProblems: [],
      previewTab: 0,
      errorMessage: '',
      
      // 문제 풀이 관련
      isSolvingMode: false,
      userAnswers: {},
      solvedCount: 0,
      totalScore: 0,
      correctCount: 0,
      showFinalResults: false,
      
      settings: {
        questionTypes: ['multiple_choice'],
        difficulty: 'intermediate',
        questionCount: 20,
        language: 'ko',
        includeExplanations: true,
        avoidDuplicates: true,
        useImages: false,
        customPrompt: ''
      },
      
      languageOptions: [
        { title: '한국어', value: 'ko' },
        { title: 'English', value: 'en' },
        { title: '日本語', value: 'ja' },
        { title: '中文', value: 'zh' }
      ]
    };
  },
  computed: {
    totalPossibleScore() {
      return this.generatedProblems.reduce((sum, problem) => sum + problem.points, 0);
    }
  },
  methods: {
    handleDrop(e) {
      e.preventDefault();
      this.isDragOver = false;
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },
    
    handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) {
        this.processFile(file);
      }
    },
    
    processFile(file) {
      if (file.type !== 'application/pdf') {
        this.showError('PDF 파일만 업로드 가능합니다.');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        this.showError('파일 크기는 10MB 이하여야 합니다.');
        return;
      }
      
      this.selectedFile = file;
      this.errorMessage = '';
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    async generateProblems() {
      if (!this.selectedFile) {
        this.showError('PDF 파일을 먼저 업로드해주세요.');
        return;
      }
      
      if (this.settings.questionTypes.length === 0) {
        this.showError('최소 하나의 문제 유형을 선택해주세요.');
        return;
      }
      
      this.isGenerating = true;
      this.generationProgress = 0;
      this.generatedProblems = [];
      this.errorMessage = '';
      
      try {
        // 1단계: PDF 업로드
        this.updateProgress(10, 'PDF 파일 업로드 중...');
        const uploadedPdf = await this.uploadPDF();
        console.log('업로드 결과:', uploadedPdf);
        
        // 2단계: 텍스트 추출
        this.updateProgress(30, 'PDF에서 텍스트 추출 중...');
        const extractedText = await this.extractText(uploadedPdf.id);
        console.log('텍스트 추출 결과:', extractedText);
        
        // 3단계: AI 문제 생성
        this.updateProgress(50, 'AI가 문제를 생성 중...');
        let problems;
        try {
          problems = await this.callAIProblemGeneration(extractedText);
          console.log('AI 문제 생성 결과:', problems);
        } catch (error) {
          console.warn('실제 AI API 실패, 테스트 데이터 사용:', error);
          problems = await this.callAIProblemGenerationTest();
          console.log('테스트 데이터 사용 결과:', problems);
        }
        
        // 4단계: 후처리
        this.updateProgress(80, '문제 품질 검증 중...');
        this.generatedProblems = await this.processGeneratedProblems(problems);
        
        console.log('Generated problems:', this.generatedProblems);
        console.log('Problems length:', this.generatedProblems.length);
        this.updateProgress(100, '완료!');
        
        if (this.generatedProblems.length === 0) {
          this.showError('문제 생성에 실패했습니다. 다시 시도해주세요.');
        }
        
      } catch (error) {
        this.showError(error.message);
        console.error('문제 생성 오류:', error);
      } finally {
        this.isGenerating = false;
      }
    },
    
    async uploadPDF() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      
      const response = await fetch('http://127.0.0.1:8000/api/upload-pdf', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('PDF 업로드에 실패했습니다.');
      }
      
      return await response.json();
    },
    
    async extractText(pdfId) {
      const response = await fetch(`http://127.0.0.1:8000/api/extract-text/${pdfId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('텍스트 추출에 실패했습니다.');
      }
      
      return await response.json();
    },
    
    async callAIProblemGeneration(extractedText) {
      const response = await fetch('http://127.0.0.1:8000/api/generate-problems', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: extractedText.content,
          settings: this.settings
        })
      });
      
      if (!response.ok) {
        throw new Error('AI 문제 생성에 실패했습니다.');
      }
      
      return await response.json();
    },
    
    async callAIProblemGenerationTest() {
      const response = await fetch('http://127.0.0.1:8000/api/generate-problems-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: "테스트용 텍스트",
          settings: this.settings
        })
      });
      
      if (!response.ok) {
        throw new Error('테스트 문제 생성에 실패했습니다.');
      }
      
      return await response.json();
    },
    
    async processGeneratedProblems(problems) {
      return problems.map((problem, index) => ({
        id: index + 1,
        ...problem
      }));
    },
    
    updateProgress(value, text) {
      this.generationProgress = value;
      this.progressText = text;
    },
    
    showError(message) {
      this.errorMessage = message;
    },
    
    downloadProblems() {
      const dataStr = JSON.stringify(this.generatedProblems, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `generated_problems_${new Date().toISOString().slice(0,10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    },
    
    editProblems() {
      // 문제 편집 모달 또는 페이지로 이동
      this.$router.push({ name: 'ProblemEditor', params: { problems: this.generatedProblems }});
    },
    
    regenerateProblems() {
      this.generateProblems();
    },
    
    // 문제 풀이 관련 메서드
    startSolving() {
      console.log('문제 풀이 시작, 문제 수:', this.generatedProblems.length);
      console.log('문제 데이터:', this.generatedProblems);
      this.isSolvingMode = true;
      this.resetQuizData();
    },
    
    handleAnswerChanged(data) {
      // 답안 변경 시 처리 (필요시 구현)
    },
    
    handleAnswerSubmitted(data) {
      this.userAnswers[data.problemIndex] = {
        userAnswer: data.userAnswer,
        isCorrect: data.isCorrect,
        points: data.points
      };
      
      this.solvedCount = Object.keys(this.userAnswers).length;
      this.totalScore = Object.values(this.userAnswers).reduce((sum, answer) => sum + answer.points, 0);
      this.correctCount = Object.values(this.userAnswers).filter(answer => answer.isCorrect).length;
      
      // 모든 문제를 풀었는지 확인
      if (this.solvedCount === this.generatedProblems.length) {
        setTimeout(() => {
          this.showFinalResults = true;
        }, 1000);
      }
    },
    
    resetQuiz() {
      this.resetQuizData();
      this.showFinalResults = false;
    },
    
    resetQuizData() {
      this.userAnswers = {};
      this.solvedCount = 0;
      this.totalScore = 0;
      this.correctCount = 0;
      this.showFinalResults = false;
    },
    
    downloadResults() {
      const results = {
        timestamp: new Date().toISOString(),
        totalProblems: this.generatedProblems.length,
        solvedCount: this.solvedCount,
        totalScore: this.totalScore,
        totalPossibleScore: this.totalPossibleScore,
        percentage: Math.round((this.totalScore / this.totalPossibleScore) * 100),
        correctCount: this.correctCount,
        problems: this.generatedProblems.map((problem, index) => ({
          question: problem.question,
          type: problem.type,
          userAnswer: this.userAnswers[index]?.userAnswer || 'No answer',
          correctAnswer: problem.answer,
          isCorrect: this.userAnswers[index]?.isCorrect || false,
          points: this.userAnswers[index]?.points || 0
        }))
      };
      
      const dataStr = JSON.stringify(results, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `quiz_results_${new Date().toISOString().slice(0,10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    }
  }
};
</script>

<style scoped>
.upload-area {
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #2196F3;
  background-color: rgba(33, 150, 243, 0.02);
}

.upload-area.dragover {
  border-color: #2196F3;
  background-color: rgba(33, 150, 243, 0.05);
  transform: scale(1.02);
}

.upload-content {
  pointer-events: none;
}

.v-chip-group {
  gap: 8px;
}

.v-expansion-panel-text {
  padding-top: 16px;
}
</style>