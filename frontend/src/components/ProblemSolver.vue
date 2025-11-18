<template>
  <v-card class="problem-solver mb-4">
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2" :color="getTypeColor(problem.type)">
          {{ getTypeIcon(problem.type) }}
        </v-icon>
        <span>문제 {{ problemIndex + 1 }}</span>
        <v-chip :color="getDifficultyColor(problem.difficulty)" variant="flat" size="small" class="ml-3">
          {{ getDifficultyName(problem.difficulty) }}
        </v-chip>
      </div>
      <div class="d-flex align-center gap-2">
        <v-chip variant="outlined" size="small">{{ problem.points }}점</v-chip>
        <v-chip variant="outlined" size="small">{{ problem.estimatedTime }}분</v-chip>
      </div>
    </v-card-title>
    
    <v-divider></v-divider>
    
    <v-card-text>
      <!-- 문제 내용 -->
      <div class="mb-4">
        <h4 class="mb-3 font-weight-medium question-text">{{ problem.question }}</h4>
        
        <!-- 객관식 -->
        <div v-if="problem.type === 'multiple_choice' && problem.choices">
          <v-radio-group 
            v-model="userAnswer" 
            @change="handleAnswerChange"
            :disabled="isSubmitted"
          >
            <v-radio
              v-for="(choice, index) in problem.choices"
              :key="index"
              :label="choice"
              :value="index"
              :color="getChoiceColor(index)"
              class="choice-item"
            ></v-radio>
          </v-radio-group>
        </div>
        
        <!-- 단답형 -->
        <div v-else-if="problem.type === 'short_answer'">
          <v-text-field
            v-model="userAnswer"
            @input="handleAnswerChange"
            variant="outlined"
            label="답안을 입력하세요"
            :disabled="isSubmitted"
            :color="getAnswerFieldColor()"
          ></v-text-field>
        </div>
        
        <!-- 서술형 -->
        <div v-else-if="problem.type === 'essay'">
          <v-textarea
            v-model="userAnswer"
            @input="handleAnswerChange"
            variant="outlined"
            label="답안을 작성하세요"
            rows="4"
            :disabled="isSubmitted"
            :color="getAnswerFieldColor()"
            counter
          ></v-textarea>
        </div>
        
        <!-- O/X -->
        <div v-else-if="problem.type === 'true_false'">
          <v-btn-toggle 
            v-model="userAnswer" 
            @update:model-value="handleAnswerChange"
            variant="outlined" 
            :disabled="isSubmitted"
            class="true-false-buttons"
          >
            <v-btn value="true" :color="getTrueFalseColor(true)">
              <v-icon start>mdi-check</v-icon>
              O (참)
            </v-btn>
            <v-btn value="false" :color="getTrueFalseColor(false)">
              <v-icon start>mdi-close</v-icon>
              X (거짓)
            </v-btn>
          </v-btn-toggle>
        </div>
        
        <!-- 빈칸 채우기 -->
        <div v-else-if="problem.type === 'fill_blank'">
          <div class="fill-blank-content" v-html="renderFillBlank()"></div>
        </div>
      </div>
      
      <!-- 제출 후 결과 표시 -->
      <div v-if="isSubmitted" class="result-section mt-4">
        <v-alert 
          :type="isCorrect ? 'success' : 'error'" 
          variant="tonal"
          class="mb-3"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-2">
              {{ isCorrect ? 'mdi-check-circle' : 'mdi-close-circle' }}
            </v-icon>
            <strong>
              {{ isCorrect ? '정답입니다!' : '오답입니다.' }} 
              ({{ isCorrect ? problem.points : 0 }}/{{ problem.points }}점)
            </strong>
          </div>
        </v-alert>
        
        <!-- 정답 표시 -->
        <div class="mb-3">
          <strong class="text-success">정답:</strong>
          <span class="ml-2">{{ formatCorrectAnswer() }}</span>
        </div>
        
        <!-- 해설 -->
        <div v-if="problem.explanation" class="explanation-section">
          <strong class="text-info">해설:</strong>
          <p class="mt-2 text-body-2">{{ problem.explanation }}</p>
        </div>
      </div>
      
      <!-- 제출 버튼 -->
      <div v-if="!isSubmitted" class="text-center mt-4">
        <v-btn 
          color="primary" 
          :disabled="!hasAnswer"
          @click="submitAnswer"
          size="large"
        >
          <v-icon start>mdi-check</v-icon>
          답안 제출
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'ProblemSolver',
  props: {
    problem: {
      type: Object,
      required: true
    },
    problemIndex: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      userAnswer: null,
      isSubmitted: false,
      isCorrect: false,
      fillBlankAnswers: {} // 빈칸 채우기용
    };
  },
  computed: {
    hasAnswer() {
      if (this.problem.type === 'fill_blank') {
        return Object.keys(this.fillBlankAnswers).length > 0;
      }
      return this.userAnswer !== null && this.userAnswer !== '';
    }
  },
  methods: {
    getTypeIcon(type) {
      const icons = {
        multiple_choice: 'mdi-format-list-bulleted',
        short_answer: 'mdi-format-text',
        essay: 'mdi-format-align-left',
        true_false: 'mdi-check-bold',
        fill_blank: 'mdi-format-text-variant'
      };
      return icons[type] || 'mdi-help-circle';
    },
    
    getTypeColor(type) {
      const colors = {
        multiple_choice: 'primary',
        short_answer: 'success',
        essay: 'info',
        true_false: 'warning',
        fill_blank: 'purple'
      };
      return colors[type] || 'grey';
    },
    
    getDifficultyColor(difficulty) {
      const colors = {
        beginner: 'green',
        intermediate: 'orange',
        advanced: 'red'
      };
      return colors[difficulty] || 'grey';
    },
    
    getDifficultyName(difficulty) {
      const names = {
        beginner: '초급',
        intermediate: '중급',
        advanced: '고급'
      };
      return names[difficulty] || '미분류';
    },
    
    getChoiceColor(index) {
      if (!this.isSubmitted) return 'primary';
      if (this.problem.answer === index) return 'success';
      if (this.userAnswer === index && !this.isCorrect) return 'error';
      return 'grey';
    },
    
    getTrueFalseColor(value) {
      if (!this.isSubmitted) return value === 'true' ? 'success' : 'error';
      const correctAnswer = this.problem.answer === true || this.problem.answer === 'true';
      const isThisCorrect = (value === 'true') === correctAnswer;
      if (isThisCorrect) return 'success';
      if (this.userAnswer === value && !this.isCorrect) return 'error';
      return 'grey';
    },
    
    getAnswerFieldColor() {
      if (!this.isSubmitted) return 'primary';
      return this.isCorrect ? 'success' : 'error';
    },
    
    handleAnswerChange() {
      this.$emit('answer-changed', {
        problemIndex: this.problemIndex,
        answer: this.userAnswer,
        hasAnswer: this.hasAnswer
      });
    },
    
    submitAnswer() {
      this.isSubmitted = true;
      this.checkAnswer();
      
      this.$emit('answer-submitted', {
        problemIndex: this.problemIndex,
        userAnswer: this.userAnswer,
        isCorrect: this.isCorrect,
        points: this.isCorrect ? this.problem.points : 0
      });
    },
    
    checkAnswer() {
      const correctAnswer = this.problem.answer;
      
      switch (this.problem.type) {
        case 'multiple_choice':
          this.isCorrect = this.userAnswer === correctAnswer;
          break;
          
        case 'true_false':
          const userBool = this.userAnswer === 'true';
          const correctBool = correctAnswer === true || correctAnswer === 'true';
          this.isCorrect = userBool === correctBool;
          break;
          
        case 'short_answer':
          this.isCorrect = this.normalizeText(this.userAnswer) === this.normalizeText(correctAnswer);
          break;
          
        case 'essay':
          // 서술형은 간단한 키워드 매칭으로 처리 (실제로는 더 복잡한 평가 필요)
          this.isCorrect = this.checkEssayAnswer(this.userAnswer, correctAnswer);
          break;
          
        case 'fill_blank':
          this.isCorrect = this.checkFillBlankAnswer();
          break;
          
        default:
          this.isCorrect = false;
      }
    },
    
    normalizeText(text) {
      return text.toString().toLowerCase().trim().replace(/\s+/g, ' ');
    },
    
    checkEssayAnswer(userAnswer, correctAnswer) {
      // 간단한 키워드 기반 채점 (실제로는 AI 기반 채점 필요)
      if (!userAnswer || userAnswer.length < 10) return false;
      
      const userText = this.normalizeText(userAnswer);
      const keywords = this.normalizeText(correctAnswer).split(' ');
      
      let matchCount = 0;
      keywords.forEach(keyword => {
        if (keyword.length > 2 && userText.includes(keyword)) {
          matchCount++;
        }
      });
      
      return matchCount >= Math.ceil(keywords.length * 0.6); // 60% 이상 키워드 매칭
    },
    
    checkFillBlankAnswer() {
      // 빈칸 채우기 답안 확인 로직
      const answers = Object.values(this.fillBlankAnswers);
      const correctAnswers = this.problem.answer.split(',').map(a => a.trim());
      
      if (answers.length !== correctAnswers.length) return false;
      
      return answers.every((answer, index) => 
        this.normalizeText(answer) === this.normalizeText(correctAnswers[index])
      );
    },
    
    renderFillBlank() {
      let questionHtml = this.problem.question;
      let blankIndex = 0;
      
      questionHtml = questionHtml.replace(/___/g, () => {
        const inputId = `blank_${blankIndex}`;
        const inputHtml = `<input 
          type="text" 
          class="fill-blank-input" 
          id="${inputId}"
          data-blank-index="${blankIndex}"
          ${this.isSubmitted ? 'disabled' : ''}
          style="width: 120px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px; margin: 0 4px;"
        />`;
        blankIndex++;
        return inputHtml;
      });
      
      return questionHtml;
    },
    
    formatCorrectAnswer() {
      const answer = this.problem.answer;
      
      if (this.problem.type === 'multiple_choice') {
        return `${answer + 1}번: ${this.problem.choices[answer]}`;
      } else if (this.problem.type === 'true_false') {
        return answer === true || answer === 'true' ? 'O (참)' : 'X (거짓)';
      }
      
      return answer;
    }
  },
  
  mounted() {
    // 빈칸 채우기 input 이벤트 리스너 등록
    if (this.problem.type === 'fill_blank') {
      this.$nextTick(() => {
        const inputs = this.$el.querySelectorAll('.fill-blank-input');
        inputs.forEach(input => {
          input.addEventListener('input', (e) => {
            const blankIndex = e.target.dataset.blankIndex;
            this.fillBlankAnswers[blankIndex] = e.target.value;
            this.handleAnswerChange();
          });
        });
      });
    }
  }
};
</script>

<style scoped>
.problem-solver {
  margin-bottom: 24px;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
}

.choice-item {
  margin-bottom: 8px;
}

.true-false-buttons {
  width: 100%;
}

.true-false-buttons .v-btn {
  flex: 1;
}

.result-section {
  border-top: 1px solid #e0e0e0;
  padding-top: 16px;
}

.explanation-section {
  background: rgba(33, 150, 243, 0.05);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.fill-blank-input:focus {
  outline: 2px solid #2196F3;
  border-color: #2196F3;
}
</style>