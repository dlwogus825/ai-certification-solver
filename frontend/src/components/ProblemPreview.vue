<template>
  <v-card variant="outlined" class="problem-preview">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2" :color="getTypeColor(problem.type)">
        {{ getTypeIcon(problem.type) }}
      </v-icon>
      <span class="font-weight-medium">{{ getTypeName(problem.type) }}</span>
      <v-spacer></v-spacer>
      <v-chip :color="getDifficultyColor(problem.difficulty)" variant="flat" size="small">
        {{ getDifficultyName(problem.difficulty) }}
      </v-chip>
    </v-card-title>
    
    <v-divider></v-divider>
    
    <v-card-text>
      <!-- 문제 내용 -->
      <div class="mb-4">
        <h4 class="mb-3 font-weight-medium">{{ problem.question }}</h4>
        
        <!-- 객관식 선택지 -->
        <div v-if="problem.type === 'multiple_choice' && problem.choices">
          <v-radio-group v-model="selectedAnswer" :disabled="true">
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
            variant="outlined"
            label="답안 입력"
            disabled
            placeholder="학생이 답안을 입력하는 영역"
          ></v-text-field>
        </div>
        
        <!-- 서술형 -->
        <div v-else-if="problem.type === 'essay'">
          <v-textarea
            variant="outlined"
            label="답안 작성"
            disabled
            rows="4"
            placeholder="학생이 서술형 답안을 작성하는 영역"
          ></v-textarea>
        </div>
        
        <!-- O/X -->
        <div v-else-if="problem.type === 'true_false'">
          <v-btn-toggle variant="outlined" disabled class="true-false-buttons">
            <v-btn value="true" color="success">
              <v-icon start>mdi-check</v-icon>
              O (참)
            </v-btn>
            <v-btn value="false" color="error">
              <v-icon start>mdi-close</v-icon>
              X (거짓)
            </v-btn>
          </v-btn-toggle>
        </div>
        
        <!-- 빈칸 채우기 -->
        <div v-else-if="problem.type === 'fill_blank'">
          <div class="fill-blank-content" v-html="formatFillBlank(problem.question)"></div>
        </div>
      </div>
      
      <!-- 정답 및 해설 -->
      <v-expansion-panels variant="accordion" class="mt-4">
        <v-expansion-panel>
          <v-expansion-panel-title class="text-success font-weight-medium">
            <v-icon class="mr-2">mdi-check-circle</v-icon>
            정답 및 해설 보기
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="mb-3">
              <strong class="text-success">정답:</strong>
              <span class="ml-2">{{ formatAnswer(problem.answer) }}</span>
            </div>
            <div v-if="problem.explanation">
              <strong class="text-info">해설:</strong>
              <p class="mt-2 text-body-2">{{ problem.explanation }}</p>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
      
      <!-- 문제 메타데이터 -->
      <div class="d-flex flex-wrap gap-2 mt-4">
        <v-chip v-if="problem.topic" variant="outlined" size="small">
          <v-icon start size="small">mdi-tag</v-icon>
          {{ problem.topic }}
        </v-chip>
        <v-chip v-if="problem.points" variant="outlined" size="small" color="orange">
          <v-icon start size="small">mdi-star</v-icon>
          {{ problem.points }}점
        </v-chip>
        <v-chip v-if="problem.estimatedTime" variant="outlined" size="small" color="blue">
          <v-icon start size="small">mdi-clock</v-icon>
          {{ problem.estimatedTime }}분
        </v-chip>
      </div>
    </v-card-text>
    
    <!-- 문제 액션 -->
    <v-card-actions>
      <v-btn variant="text" size="small" @click="editProblem">
        <v-icon start>mdi-pencil</v-icon>
        편집
      </v-btn>
      <v-btn variant="text" size="small" @click="duplicateProblem">
        <v-icon start>mdi-content-copy</v-icon>
        복사
      </v-btn>
      <v-btn variant="text" size="small" color="error" @click="deleteProblem">
        <v-icon start>mdi-delete</v-icon>
        삭제
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'ProblemPreview',
  props: {
    problem: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selectedAnswer: null
    };
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
    
    getTypeName(type) {
      const names = {
        multiple_choice: '객관식',
        short_answer: '단답형',
        essay: '서술형',
        true_false: 'O/X 문제',
        fill_blank: '빈칸 채우기'
      };
      return names[type] || '알 수 없음';
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
      if (this.problem.answer === index) {
        return 'success';
      }
      return 'primary';
    },
    
    mounted() {
      console.log('Problem data:', this.problem);
    },
    
    formatAnswer(answer) {
      if (this.problem.type === 'multiple_choice') {
        if (typeof answer === 'number' && this.problem.choices) {
          return `${answer + 1}번: ${this.problem.choices[answer]}`;
        }
      } else if (this.problem.type === 'true_false') {
        return answer === true || answer === 'true' ? 'O (참)' : 'X (거짓)';
      }
      return answer;
    },
    
    formatFillBlank(text) {
      return text.replace(/___/g, '<input type="text" class="fill-blank-input" disabled />');
    },
    
    editProblem() {
      this.$emit('edit-problem', this.problem);
    },
    
    duplicateProblem() {
      this.$emit('duplicate-problem', this.problem);
    },
    
    deleteProblem() {
      this.$emit('delete-problem', this.problem);
    }
  }
};
</script>

<style scoped>
.problem-preview {
  margin-bottom: 16px;
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

.fill-blank-content {
  line-height: 2;
  font-size: 1.1em;
}

.fill-blank-input {
  display: inline-block;
  width: 100px;
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f5f5f5;
  text-align: center;
  margin: 0 4px;
}

.v-expansion-panel-text {
  background: rgba(0, 0, 0, 0.02);
}
</style>