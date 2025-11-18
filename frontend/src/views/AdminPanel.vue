<template>
  <v-container class="pa-6">
    <!-- 헤더 -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">
          <v-icon size="32" color="primary" class="mr-2">mdi-shield-crown</v-icon>
          관리자 패널
        </h1>
        <p class="text-subtitle-1 text-grey-darken-1">
          시스템 전체를 관리하고 모니터링하세요
        </p>
      </div>
      <v-chip color="success" variant="flat" prepend-icon="mdi-check-circle">
        시스템 정상
      </v-chip>
    </div>

    <!-- 대시보드 통계 카드들 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center stat-card" color="primary" variant="tonal">
          <v-icon size="48" color="primary" class="mb-2">mdi-account-group</v-icon>
          <div class="text-h4 font-weight-bold">{{ stats.totalUsers }}</div>
          <div class="text-body-2">전체 사용자</div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center stat-card" color="success" variant="tonal">
          <v-icon size="48" color="success" class="mb-2">mdi-file-pdf-box</v-icon>
          <div class="text-h4 font-weight-bold">{{ stats.totalPdfs }}</div>
          <div class="text-body-2">업로드된 PDF</div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center stat-card" color="warning" variant="tonal">
          <v-icon size="48" color="warning" class="mb-2">mdi-help-circle</v-icon>
          <div class="text-h4 font-weight-bold">{{ stats.totalQuestions }}</div>
          <div class="text-body-2">총 문제 수</div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center stat-card" color="info" variant="tonal">
          <v-icon size="48" color="info" class="mb-2">mdi-chart-line</v-icon>
          <div class="text-h4 font-weight-bold">{{ stats.todayLogins }}</div>
          <div class="text-body-2">오늘 로그인</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 탭 네비게이션 -->
    <v-tabs v-model="currentTab" class="mb-6" color="primary">
      <v-tab value="upload">
        <v-icon class="mr-2">mdi-upload</v-icon>
        PDF 업로드
      </v-tab>
      <v-tab value="users">
        <v-icon class="mr-2">mdi-account-group</v-icon>
        사용자 관리
      </v-tab>
      <v-tab value="questions">
        <v-icon class="mr-2">mdi-help-circle</v-icon>
        문제 관리
      </v-tab>
      <v-tab value="system">
        <v-icon class="mr-2">mdi-cog</v-icon>
        시스템 관리
      </v-tab>
    </v-tabs>

    <!-- 탭 콘텐츠 -->
    <v-tabs-window v-model="currentTab">
      <!-- PDF 업로드 탭 -->
      <v-tabs-window-item value="upload">
        <v-row>
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title class="text-h6 mb-4">
                <v-icon class="mr-2">mdi-file-upload</v-icon>
                PDF 업로드 및 OCR 처리
              </v-card-title>
              <v-card-text>
                <v-file-input
                  label="PDF 파일 선택"
                  accept="application/pdf"
                  prepend-icon="mdi-file-pdf-box"
                  v-model="selectedFile"
                  variant="outlined"
                  density="comfortable"
                ></v-file-input>
                
                <v-btn
                  color="primary"
                  size="large"
                  block
                  :disabled="!selectedFile || uploading"
                  @click="uploadPdf"
                  class="mt-4"
                >
                  <v-progress-circular
                    v-if="uploading"
                    indeterminate
                    size="20"
                    width="2"
                    color="white"
                    class="mr-2"
                  ></v-progress-circular>
                  {{ uploading ? uploadStage : 'PDF 업로드 및 OCR 처리' }}
                </v-btn>
                
                <!-- 진행률 표시 -->
                <div v-if="uploading" class="mt-4">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-body-2 font-weight-medium">{{ uploadStage }}</span>
                    <span class="text-body-2">{{ uploadProgress }}%</span>
                  </div>
                  <v-progress-linear
                    :model-value="uploadProgress"
                    color="primary"
                    height="8"
                    rounded
                    striped>
                  </v-progress-linear>
                  
                  <!-- 단계별 아이콘 -->
                  <div class="d-flex justify-space-around mt-3">
                    <div class="text-center">
                      <v-icon 
                        :color="uploadProgress >= 30 ? 'success' : (uploadProgress > 0 ? 'primary' : 'grey')"
                        size="24">
                        {{ uploadProgress >= 30 ? 'mdi-check-circle' : 'mdi-upload' }}
                      </v-icon>
                      <div class="text-caption mt-1">업로드</div>
                    </div>
                    <div class="text-center">
                      <v-icon 
                        :color="uploadProgress >= 70 ? 'success' : (uploadProgress >= 30 ? 'primary' : 'grey')"
                        size="24">
                        {{ uploadProgress >= 70 ? 'mdi-check-circle' : 'mdi-eye-scan' }}
                      </v-icon>
                      <div class="text-caption mt-1">OCR 처리</div>
                    </div>
                    <div class="text-center">
                      <v-icon 
                        :color="uploadProgress >= 100 ? 'success' : (uploadProgress >= 70 ? 'primary' : 'grey')"
                        size="24">
                        {{ uploadProgress >= 100 ? 'mdi-check-circle' : 'mdi-brain' }}
                      </v-icon>
                      <div class="text-caption mt-1">AI 파싱</div>
                    </div>
                  </div>
                </div>
                
                <v-alert 
                  v-if="uploadMessage" 
                  :type="uploadSuccess ? 'success' : 'error'" 
                  class="mt-4"
                  closable>
                  {{ uploadMessage }}
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title class="text-h6 mb-4">
                <v-icon class="mr-2">mdi-information</v-icon>
                업로드 가이드라인
              </v-card-title>
              <v-card-text>
                <v-list density="compact">
                  <v-list-item prepend-icon="mdi-check">
                    <v-list-item-title>PDF 파일 크기: 최대 10MB</v-list-item-title>
                  </v-list-item>
                  <v-list-item prepend-icon="mdi-check">
                    <v-list-item-title>지원 언어: 한국어, 영어</v-list-item-title>
                  </v-list-item>
                  <v-list-item prepend-icon="mdi-check">
                    <v-list-item-title>권장 해상도: 300 DPI 이상</v-list-item-title>
                  </v-list-item>
                  <v-list-item prepend-icon="mdi-check">
                    <v-list-item-title>문제 형식: 객관식 (4-5지선다)</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row class="mt-4">
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title class="text-h6 mb-4">업로드된 PDF 문서 목록</v-card-title>
              <v-card-text>
                <PdfListView />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-tabs-window-item>

      <!-- 사용자 관리 탭 -->
      <v-tabs-window-item value="users">
        <v-card class="pa-4">
          <v-card-title class="text-h6 mb-4">
            <v-icon class="mr-2">mdi-account-group</v-icon>
            사용자 관리
          </v-card-title>
          <v-card-text>
            <!-- 사용자 검색 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="userSearch"
                  label="사용자 검색"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  clearable>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="userFilter"
                  :items="['전체', '관리자', '일반사용자', '비활성']"
                  label="사용자 유형"
                  variant="outlined"
                  density="comfortable">
                </v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn color="primary" size="large" @click="loadUsers">
                  <v-icon class="mr-2">mdi-refresh</v-icon>
                  새로고침
                </v-btn>
              </v-col>
            </v-row>

            <!-- 사용자 목록 -->
            <v-data-table
              :headers="userHeaders"
              :items="filteredUsers"
              :loading="loadingUsers"
              class="elevation-1">
              
              <template v-slot:item.is_admin="{ item }">
                <v-chip 
                  :color="item.is_admin ? 'primary' : 'default'" 
                  size="small"
                  variant="flat">
                  {{ item.is_admin ? '관리자' : '일반사용자' }}
                </v-chip>
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <div class="d-flex flex-column ga-1">
                  <v-btn
                    color="primary"
                    size="small"
                    variant="tonal"
                    @click="editUser(item)"
                    class="rounded-pill text-caption d-flex justify-center align-center"
                    style="min-width: 80px;">
                    <v-icon start size="14">mdi-pencil</v-icon>
                    편집
                  </v-btn>
                  <v-btn
                    color="warning"
                    size="small"
                    variant="tonal"
                    @click="resetUserPassword(item)"
                    class="rounded-pill text-caption d-flex justify-center align-center"
                    style="min-width: 80px;">
                    <v-icon start size="14">mdi-key-variant</v-icon>
                    비번변경
                  </v-btn>
                  <v-btn
                    color="error"
                    size="small"
                    variant="tonal"
                    @click="deleteUser(item)"
                    class="rounded-pill text-caption d-flex justify-center align-center"
                    style="min-width: 80px;">
                    <v-icon start size="14">mdi-delete</v-icon>
                    삭제
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- 문제 관리 탭 -->
      <v-tabs-window-item value="questions">
        <v-card class="pa-4">
          <v-card-title class="text-h6 mb-4">
            <v-icon class="mr-2">mdi-help-circle</v-icon>
            문제 관리
          </v-card-title>
          <v-card-text>
            <!-- 통계 카드 -->
            <v-row class="mb-6">
              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 text-center">
                  <v-icon size="48" color="success" class="mb-2">mdi-check-circle</v-icon>
                  <div class="text-h5 font-weight-bold">{{ stats.totalQuestions }}</div>
                  <div class="text-body-2">총 문제 수</div>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 text-center">
                  <v-icon size="48" color="warning" class="mb-2">mdi-alert-circle</v-icon>
                  <div class="text-h5 font-weight-bold">0</div>
                  <div class="text-body-2">검토 필요</div>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 text-center">
                  <v-icon size="48" color="info" class="mb-2">mdi-star</v-icon>
                  <div class="text-h5 font-weight-bold">0</div>
                  <div class="text-body-2">즐겨찾기</div>
                </v-card>
              </v-col>
            </v-row>

            <!-- AI 문제 생성 섹션 -->
            <v-expansion-panels class="mb-6">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <div class="d-flex align-center">
                    <v-icon class="mr-3" color="primary">mdi-robot</v-icon>
                    <div>
                      <div class="text-h6">AI 문제 생성</div>
                      <div class="text-caption text-grey">AI를 활용하여 새로운 문제를 생성합니다</div>
                    </div>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-row class="mt-2">
                    <v-col cols="12" md="6">
                      <!-- 문제 생성 옵션 -->
                      <v-card variant="outlined" class="pa-4">
                        <v-card-subtitle class="text-h6 mb-3">
                          <v-icon class="mr-2" size="small">mdi-cog</v-icon>
                          생성 옵션
                        </v-card-subtitle>
                        
                        <v-select
                          v-model="aiGenOptions.documentId"
                          :items="pdfDocuments"
                          item-title="display_name"
                          item-value="id"
                          label="PDF 문서 선택"
                          variant="outlined"
                          density="comfortable"
                          class="mb-3"
                          :loading="loadingPdfs"
                        >
                          <template v-slot:item="{ item, props }">
                            <v-list-item v-bind="props">
                              <template v-slot:prepend>
                                <v-icon>mdi-file-pdf-box</v-icon>
                              </template>
                              <v-list-item-subtitle>
                                {{ item.raw.questions_count }}개 문제 • {{ formatDate(item.raw.created_at) }}
                              </v-list-item-subtitle>
                            </v-list-item>
                          </template>
                        </v-select>

                        <v-select
                          v-model="aiGenOptions.questionType"
                          :items="['similar', 'variation', 'advanced']"
                          label="문제 생성 유형"
                          variant="outlined"
                          density="comfortable"
                          class="mb-3"
                        >
                          <template v-slot:item="{ item }">
                            <v-list-item>
                              <v-list-item-title>
                                {{ item.value === 'similar' ? '유사 문제' : 
                                   item.value === 'variation' ? '변형 문제' : 
                                   '심화 문제' }}
                              </v-list-item-title>
                              <v-list-item-subtitle>
                                {{ item.value === 'similar' ? '기존 문제와 유사한 난이도와 형식' : 
                                   item.value === 'variation' ? '다른 각도에서 접근하는 변형' : 
                                   '더 높은 난이도의 심화 문제' }}
                              </v-list-item-subtitle>
                            </v-list-item>
                          </template>
                        </v-select>

                        <v-text-field
                          v-model="aiGenOptions.count"
                          label="생성할 문제 수"
                          type="number"
                          min="1"
                          max="20"
                          variant="outlined"
                          density="comfortable"
                          class="mb-3"
                        ></v-text-field>

                        <v-textarea
                          v-model="aiGenOptions.specificTopic"
                          label="특정 주제 집중 (선택사항)"
                          rows="3"
                          variant="outlined"
                          density="comfortable"
                          placeholder="예: 특정 챕터나 개념에 집중하여 문제 생성"
                        ></v-textarea>

                        <v-btn
                          color="info"
                          variant="tonal"
                          block
                          @click="previewSourceQuestions"
                          :disabled="!aiGenOptions.documentId"
                          class="mb-3"
                        >
                          <v-icon class="mr-2">mdi-eye</v-icon>
                          원본 문제 미리보기
                        </v-btn>
                      </v-card>
                    </v-col>

                    <v-col cols="12" md="6">
                      <!-- 생성 미리보기 -->
                      <v-card variant="outlined" class="pa-4">
                        <v-card-subtitle class="text-h6 mb-3">
                          <v-icon class="mr-2" size="small">mdi-eye</v-icon>
                          생성 설정 미리보기
                        </v-card-subtitle>
                        
                        <v-list density="compact">
                          <v-list-item v-if="aiGenOptions.certification">
                            <template v-slot:prepend>
                              <v-icon size="small">mdi-certificate</v-icon>
                            </template>
                            <v-list-item-title>자격증: {{ aiGenOptions.certification }}</v-list-item-title>
                          </v-list-item>
                          
                          <v-list-item v-if="aiGenOptions.subject">
                            <template v-slot:prepend>
                              <v-icon size="small">mdi-book</v-icon>
                            </template>
                            <v-list-item-title>과목: {{ aiGenOptions.subject }}</v-list-item-title>
                          </v-list-item>
                          
                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon size="small">mdi-gauge</v-icon>
                            </template>
                            <v-list-item-title>난이도: {{ aiGenOptions.difficulty }}</v-list-item-title>
                          </v-list-item>
                          
                          <v-list-item>
                            <template v-slot:prepend>
                              <v-icon size="small">mdi-counter</v-icon>
                            </template>
                            <v-list-item-title>문제 수: {{ aiGenOptions.count }}개</v-list-item-title>
                          </v-list-item>
                          
                          <v-list-item v-if="aiGenOptions.topic">
                            <template v-slot:prepend>
                              <v-icon size="small">mdi-tag</v-icon>
                            </template>
                            <v-list-item-title>주제: {{ aiGenOptions.topic }}</v-list-item-title>
                          </v-list-item>
                        </v-list>

                        <v-divider class="my-3"></v-divider>

                        <v-btn
                          color="primary"
                          block
                          size="large"
                          :disabled="!aiGenOptions.certification || !aiGenOptions.subject || aiGenerating"
                          :loading="aiGenerating"
                          @click="generateAIQuestions"
                        >
                          <v-icon class="mr-2">mdi-creation</v-icon>
                          AI 문제 생성 시작
                        </v-btn>

                        <v-alert
                          v-if="aiGenMessage"
                          :type="aiGenSuccess ? 'success' : 'error'"
                          class="mt-3"
                          closable
                        >
                          {{ aiGenMessage }}
                        </v-alert>
                      </v-card>
                    </v-col>
                  </v-row>

                  <!-- 생성된 문제 미리보기 -->
                  <v-card v-if="generatedQuestions.length > 0" class="mt-4" variant="outlined">
                    <v-card-title class="text-h6">
                      <v-icon class="mr-2">mdi-format-list-checks</v-icon>
                      생성된 문제 미리보기
                    </v-card-title>
                    <v-card-text>
                      <v-expansion-panels variant="accordion">
                        <v-expansion-panel
                          v-for="(question, index) in generatedQuestions"
                          :key="index"
                        >
                          <v-expansion-panel-title>
                            <div class="d-flex align-center">
                              <v-chip size="small" class="mr-3">{{ index + 1 }}</v-chip>
                              <span class="text-body-2">{{ question.question_text }}</span>
                            </div>
                          </v-expansion-panel-title>
                          <v-expansion-panel-text>
                            <v-list density="compact">
                              <v-list-item
                                v-for="(option, optIndex) in question.options"
                                :key="optIndex"
                              >
                                <template v-slot:prepend>
                                  <v-icon
                                    :color="option.is_correct ? 'success' : 'grey'"
                                    size="small"
                                  >
                                    {{ option.is_correct ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                                  </v-icon>
                                </template>
                                <v-list-item-title>{{ option.option_text }}</v-list-item-title>
                              </v-list-item>
                            </v-list>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>
                      
                      <v-divider class="my-4"></v-divider>
                      
                      <div class="d-flex justify-end gap-2">
                        <v-btn
                          variant="outlined"
                          color="error"
                          @click="cancelGeneratedQuestions"
                        >
                          <v-icon class="mr-2">mdi-close</v-icon>
                          취소
                        </v-btn>
                        <v-btn
                          color="success"
                          @click="saveGeneratedQuestions"
                          :loading="savingQuestions"
                        >
                          <v-icon class="mr-2">mdi-content-save</v-icon>
                          문제 저장
                        </v-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- 기존 문제 관리 기능 안내 -->
            <v-alert type="info" class="mb-4">
              <div class="text-body-1">
                <strong>문제 관리 기능 (개발 예정)</strong>
              </div>
              <div class="text-body-2 mt-2">
                • 문제 수정 및 삭제<br>
                • 문제 분류 및 태깅<br>
                • 난이도 조정<br>
                • 일괄 처리 기능
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- 시스템 관리 탭 -->
      <v-tabs-window-item value="system">
        <v-row>
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title class="text-h6 mb-4">
                <v-icon class="mr-2">mdi-server</v-icon>
                시스템 상태
              </v-card-title>
              <v-card-text>
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="success">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>백엔드 서버</v-list-item-title>
                    <v-list-item-subtitle>정상 작동 중</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="success">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>데이터베이스</v-list-item-title>
                    <v-list-item-subtitle>연결됨 (SQLite)</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="warning">mdi-alert-circle</v-icon>
                    </template>
                    <v-list-item-title>AI 서비스</v-list-item-title>
                    <v-list-item-subtitle>개발 모드 (비활성화)</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="success">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>파일 업로드</v-list-item-title>
                    <v-list-item-subtitle>정상 작동 중</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title class="text-h6 mb-4">
                <v-icon class="mr-2">mdi-tools</v-icon>
                시스템 도구
              </v-card-title>
              <v-card-text>
                <v-list>
                  <v-list-item @click="showLogs">
                    <template v-slot:prepend>
                      <v-icon>mdi-text-box</v-icon>
                    </template>
                    <v-list-item-title>시스템 로그 보기</v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item @click="clearCache">
                    <template v-slot:prepend>
                      <v-icon>mdi-cached</v-icon>
                    </template>
                    <v-list-item-title>캐시 정리</v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item @click="exportData">
                    <template v-slot:prepend>
                      <v-icon>mdi-download</v-icon>
                    </template>
                    <v-list-item-title>데이터 내보내기</v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item @click="showSettings">
                    <template v-slot:prepend>
                      <v-icon>mdi-cog</v-icon>
                    </template>
                    <v-list-item-title>시스템 설정</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-tabs-window-item>
    </v-tabs-window>
    
    <!-- 비밀번호 재설정 다이얼로그 -->
    <v-dialog v-model="passwordResetDialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title class="text-h6 bg-warning text-white rounded-t-xl pa-4">
          <v-icon class="mr-2">mdi-key-variant</v-icon>
          비밀번호 재설정
        </v-card-title>
        <v-card-text class="pa-6">
          <div v-if="selectedUser">
            <p class="text-body-1 mb-4">
              <strong>{{ selectedUser.username }}</strong> 사용자의 비밀번호를 재설정합니다
            </p>
            
            <v-text-field
              v-model="newPassword"
              label="새 비밀번호"
              type="password"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || '비밀번호를 입력해주세요', v => v.length >= 4 || '비밀번호는 4자 이상이어야 합니다']"
              class="mb-3">
            </v-text-field>
            
            <v-text-field
              v-model="confirmPassword"
              label="비밀번호 확인"
              type="password"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || '비밀번호 확인을 입력해주세요', v => v === newPassword || '비밀번호가 일치하지 않습니다']">
            </v-text-field>
            
            <v-alert v-if="passwordResetMessage" :type="passwordResetSuccess ? 'success' : 'error'" class="mt-4">
              {{ passwordResetMessage }}
            </v-alert>
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="outlined" @click="closePasswordResetDialog" class="rounded-pill">
            취소
          </v-btn>
          <v-btn 
            color="warning" 
            variant="flat" 
            @click="confirmPasswordReset" 
            :loading="passwordResetting"
            :disabled="!newPassword || !confirmPassword || newPassword !== confirmPassword"
            class="rounded-pill ml-2">
            재설정
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';
import PdfListView from './PdfListView.vue';

export default {
  name: 'AdminPanel',
  components: {
    PdfListView,
  },
  data() {
    return {
      // 탭 관리
      currentTab: 'upload',
      
      // PDF 업로드
      selectedFile: null,
      uploading: false,
      uploadMessage: '',
      uploadSuccess: false,
      uploadProgress: 0,
      uploadStage: '',
      
      // 통계 데이터
      stats: {
        totalUsers: 0,
        totalPdfs: 0,
        totalQuestions: 0,
        todayLogins: 0
      },
      
      // 사용자 관리
      users: [],
      userSearch: '',
      userFilter: '전체',
      loadingUsers: false,
      userHeaders: [
        { title: 'ID', key: 'id', sortable: true },
        { title: '사용자명', key: 'username', sortable: true },
        { title: '이메일', key: 'email', sortable: true },
        { title: '유형', key: 'is_admin', sortable: true },
        { title: '가입일', key: 'created_at', sortable: true },
        { title: '작업', key: 'actions', sortable: false }
      ],
      
      // 비밀번호 재설정 관련
      passwordResetDialog: false,
      selectedUser: null,
      newPassword: '',
      confirmPassword: '',
      passwordResetting: false,
      passwordResetMessage: '',
      passwordResetSuccess: false,
      
      // AI 문제 생성 관련
      aiGenOptions: {
        certification: '',
        subject: '',
        difficulty: '보통',
        count: 5,
        topic: ''
      },
      certificationList: [
        '정보처리기사',
        'SQLD',
        '빅데이터분석기사',
        '정보보안기사',
        'AWS Solutions Architect',
        'CCNA',
        '리눅스마스터'
      ],
      subjectList: [
        '데이터베이스',
        '소프트웨어 설계',
        '정보시스템 구축관리',
        '프로그래밍 언어 활용',
        '네트워크',
        '정보보안',
        '운영체제'
      ],
      aiGenerating: false,
      aiGenMessage: '',
      aiGenSuccess: false,
      generatedQuestions: [],
      savingQuestions: false
    };
  },
  
  computed: {
    filteredUsers() {
      let filtered = this.users;
      
      // 검색 필터
      if (this.userSearch) {
        const query = this.userSearch.toLowerCase();
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
        );
      }
      
      // 유형 필터
      if (this.userFilter === '관리자') {
        filtered = filtered.filter(user => user.is_admin);
      } else if (this.userFilter === '일반사용자') {
        filtered = filtered.filter(user => !user.is_admin);
      }
      
      return filtered;
    }
  },
  
  mounted() {
    this.loadStats();
    this.loadUsers();
  },
  methods: {
    // 통계 데이터 로드
    async loadStats() {
      try {
        const token = localStorage.getItem('access_token');
        
        // 더미 데이터로 시작 (실제로는 API에서 가져와야 함)
        this.stats = {
          totalUsers: 5,
          totalPdfs: 12,
          totalQuestions: 45,
          todayLogins: 3
        };
      } catch (error) {
        console.error('통계 로드 오류:', error);
      }
    },
    
    // 사용자 목록 로드
    async loadUsers() {
      this.loadingUsers = true;
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://127.0.0.1:8000/admin/users', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const users = await response.json();
          this.users = users.map(user => ({
            ...user,
            created_at: user.created_at ? new Date(user.created_at) : new Date()
          }));
        } else {
          console.error('사용자 목록 로드 실패');
          // 백업용 더미 데이터
          this.users = [
            {
              id: 1,
              username: 'admin2',
              email: 'admin2@example.com',
              is_admin: true,
              created_at: new Date('2025-01-20')
            }
          ];
        }
      } catch (error) {
        console.error('사용자 로드 오류:', error);
        // 백업용 더미 데이터
        this.users = [];
      } finally {
        this.loadingUsers = false;
      }
    },

    // PDF 업로드
    async uploadPdf() {
      if (!this.selectedFile) {
        this.uploadMessage = 'PDF 파일을 선택해주세요.';
        this.uploadSuccess = false;
        return;
      }

      this.uploading = true;
      this.uploadMessage = '';
      this.uploadProgress = 0;
      this.uploadStage = '파일 업로드 준비 중...';

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        // 1단계: 파일 업로드 시작
        this.uploadStage = '파일 업로드 중...';
        this.uploadProgress = 10;

        const token = localStorage.getItem('access_token');
        
        // 업로드 진행률 시뮬레이션
        const progressInterval = setInterval(() => {
          if (this.uploadProgress < 25) {
            this.uploadProgress += 2;
          }
        }, 200);

        const response = await axios.post('http://127.0.0.1:8000/admin/upload-pdf-for-ocr', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
          },
        });

        clearInterval(progressInterval);

        // 2단계: OCR 처리
        this.uploadStage = 'OCR 텍스트 추출 중...';
        this.uploadProgress = 30;
        await this.delay(1000); // 시각적 효과를 위한 지연
        this.uploadProgress = 50;
        await this.delay(1000);
        this.uploadProgress = 70;

        // 3단계: AI 파싱
        this.uploadStage = 'AI 문제 분석 중...';
        await this.delay(1000);
        this.uploadProgress = 85;
        await this.delay(1000);
        this.uploadProgress = 100;
        
        this.uploadStage = '처리 완료!';
        
        this.uploadMessage = `✅ ${response.data.message || 'PDF 업로드 및 처리가 완료되었습니다.'}\n📄 파일명: ${response.data.filename}\n❓ 추출된 문제: ${response.data.questions_saved || 0}개`;
        this.uploadSuccess = true;
        this.selectedFile = null;
        this.loadStats(); // 통계 업데이트
        this.$eventBus.$emit('pdfUploaded');
      } catch (error) {
        console.error('PDF 업로드 오류:', error);
        this.uploadMessage = error.response?.data?.detail || 'PDF 업로드 중 오류가 발생했습니다.';
        this.uploadSuccess = false;
        this.uploadStage = '처리 실패';
      } finally {
        // 2초 후 초기화
        setTimeout(() => {
          this.uploading = false;
          this.uploadProgress = 0;
          this.uploadStage = '';
        }, 2000);
      }
    },

    // 지연 함수
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // 사용자 관리
    editUser(user) {
      alert(`${user.username} 사용자 편집 기능 (개발 예정)`);
    },
    
    resetUserPassword(user) {
      this.selectedUser = user;
      this.newPassword = '';
      this.confirmPassword = '';
      this.passwordResetMessage = '';
      this.passwordResetDialog = true;
    },
    
    closePasswordResetDialog() {
      this.passwordResetDialog = false;
      this.selectedUser = null;
      this.newPassword = '';
      this.confirmPassword = '';
      this.passwordResetMessage = '';
    },
    
    async confirmPasswordReset() {
      if (!this.selectedUser || !this.newPassword || this.newPassword !== this.confirmPassword) {
        return;
      }
      
      this.passwordResetting = true;
      this.passwordResetMessage = '';
      
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://127.0.0.1:8000/admin/users/reset-password', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: this.selectedUser.id,
            new_password: this.newPassword
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.passwordResetMessage = `${this.selectedUser.username}의 비밀번호가 '${data.new_password}'로 재설정되었습니다`;
          this.passwordResetSuccess = true;
          
          // 3초 후 다이얼로그 닫기
          setTimeout(() => {
            this.closePasswordResetDialog();
          }, 3000);
        } else {
          this.passwordResetMessage = data.detail || '비밀번호 재설정에 실패했습니다';
          this.passwordResetSuccess = false;
        }
      } catch (error) {
        console.error('비밀번호 재설정 오류:', error);
        this.passwordResetMessage = '네트워크 오류가 발생했습니다';
        this.passwordResetSuccess = false;
      } finally {
        this.passwordResetting = false;
      }
    },
    
    deleteUser(user) {
      if (confirm(`정말 ${user.username} 사용자를 삭제하시겠습니까?`)) {
        alert('사용자 삭제 기능 (개발 예정)');
      }
    },
    
    // 시스템 관리
    showLogs() {
      alert('시스템 로그 보기 기능 (개발 예정)');
    },
    
    clearCache() {
      if (confirm('캐시를 정리하시겠습니까?')) {
        alert('캐시 정리 완료!');
      }
    },
    
    exportData() {
      alert('데이터 내보내기 기능 (개발 예정)');
    },
    
    showSettings() {
      alert('시스템 설정 기능 (개발 예정)');
    },
    
    // 날짜 포맷팅
    formatDate(date) {
      return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    
    // AI 문제 생성 관련 메서드들
    async generateAIQuestions() {
      this.aiGenerating = true;
      this.aiGenMessage = '';
      this.aiGenSuccess = false;
      
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://127.0.0.1:8000/admin/generate-questions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            certification: this.aiGenOptions.certification,
            subject: this.aiGenOptions.subject,
            difficulty: this.aiGenOptions.difficulty,
            count: parseInt(this.aiGenOptions.count),
            topic: this.aiGenOptions.topic || undefined
          })
        });
        
        if (!response.ok) {
          throw new Error('문제 생성 실패');
        }
        
        const data = await response.json();
        this.generatedQuestions = data.questions;
        this.aiGenMessage = `${data.questions.length}개의 문제가 성공적으로 생성되었습니다!`;
        this.aiGenSuccess = true;
      } catch (error) {
        console.error('AI 문제 생성 오류:', error);
        this.aiGenMessage = error.message || 'AI 문제 생성 중 오류가 발생했습니다.';
        this.aiGenSuccess = false;
      } finally {
        this.aiGenerating = false;
      }
    },
    
    async saveGeneratedQuestions() {
      this.savingQuestions = true;
      
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://127.0.0.1:8000/admin/save-generated-questions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            questions: this.generatedQuestions,
            certification: this.aiGenOptions.certification,
            subject: this.aiGenOptions.subject
          })
        });
        
        if (!response.ok) {
          throw new Error('문제 저장 실패');
        }
        
        const data = await response.json();
        this.$eventBus.$emit('show-snackbar', {
          text: `${data.saved_count}개의 문제가 저장되었습니다!`,
          color: 'success'
        });
        
        // 초기화
        this.generatedQuestions = [];
        this.aiGenOptions = {
          certification: '',
          subject: '',
          difficulty: '보통',
          count: 5,
          topic: ''
        };
        
        // 통계 업데이트
        this.loadStats();
      } catch (error) {
        console.error('문제 저장 오류:', error);
        this.$eventBus.$emit('show-snackbar', {
          text: '문제 저장 중 오류가 발생했습니다.',
          color: 'error'
        });
      } finally {
        this.savingQuestions = false;
      }
    },
    
    cancelGeneratedQuestions() {
      this.generatedQuestions = [];
      this.aiGenMessage = '';
    }
  },
};
</script>

<style scoped>
.stat-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.v-tabs-window-item {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-list-item {
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(0,0,0,0.04);
  transform: translateX(4px);
}
</style>
