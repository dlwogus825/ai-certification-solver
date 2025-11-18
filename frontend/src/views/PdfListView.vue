<template>
  <div class="pdf-list-container">
    <!-- 헤더 섹션 -->
    <div class="hero-header">
      <v-container class="px-6 py-8">
        <div class="header-content">
          <div class="hero-content">
            <div class="d-flex align-center mb-4">
              <div class="hero-icon-wrapper">
                <v-icon size="48" color="white">mdi-library-books</v-icon>
              </div>
              <div class="ml-4">
                <h1 class="hero-title">문제 선택</h1>
                <p class="hero-subtitle mb-0">학습할 PDF 문서를 선택해서 문제 풀이를 시작하세요</p>
              </div>
            </div>
          </div>
          <div class="stats-section">
            <v-card class="stats-card" elevation="0">
              <v-card-text class="pa-4">
                <div class="text-center">
                  <div class="stats-number">{{ ocrDocuments.length }}</div>
                  <div class="stats-label">사용 가능한 문서</div>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </div>
      </v-container>
    </div>

    <v-container class="px-6 pb-8">
      <!-- 빈 상태 -->
      <div v-if="ocrDocuments.length === 0" class="empty-state">
        <div class="empty-content">
          <div class="empty-animation">
            <div class="floating-icon">
              <v-icon size="80" color="grey-lighten-2">mdi-file-document-outline</v-icon>
            </div>
            <div class="floating-particles">
              <div class="particle particle-1"></div>
              <div class="particle particle-2"></div>
              <div class="particle particle-3"></div>
            </div>
          </div>
          <h3 class="empty-title">아직 업로드된 PDF가 없습니다</h3>
          <p class="empty-description">
            관리자가 PDF를 업로드하면 여기에 표시됩니다
          </p>
          <v-btn 
            color="primary" 
            variant="flat" 
            size="large"
            rounded="12"
            class="empty-action-btn"
            @click="fetchOcrDocuments">
            <v-icon start>mdi-refresh</v-icon>
            새로고침
          </v-btn>
        </div>
      </div>

      <!-- PDF 문서 그리드 -->
      <div v-else class="documents-grid">
        <div
          v-for="(doc, index) in ocrDocuments"
          :key="doc.id"
          class="document-card-wrapper"
          :style="{ animationDelay: `${index * 100}ms` }">
          
          <div class="document-card" @click="viewDocument(doc.id)">
            <!-- 배경 효과 -->
            <div class="card-background"></div>
            
            <!-- 카드 헤더 -->
            <div class="card-header">
              <div class="document-icon-section">
                <div class="document-icon-wrapper">
                  <v-icon size="32" color="white">mdi-file-document</v-icon>
                </div>
                <div class="document-type-badge">
                  <span class="badge-text">PDF</span>
                </div>
              </div>
              
              <!-- 상태 및 액션 -->
              <div class="card-actions">
                <div class="status-indicator">
                  <div class="status-dot ready"></div>
                  <span class="status-text">준비됨</span>
                </div>
                <v-btn
                  v-if="isAdmin"
                  icon
                  size="small"
                  variant="text"
                  color="white"
                  class="delete-action"
                  @click.stop="confirmDelete(doc.id, doc.filename)">
                  <v-icon size="18">mdi-close</v-icon>
                </v-btn>
              </div>
            </div>
            
            <!-- 카드 본문 -->
            <div class="card-body">
              <div class="document-title">
                {{ getDisplayFilename(doc.filename) }}
              </div>
              
              <!-- 메타 정보 -->
              <div class="document-meta">
                <div class="meta-row">
                  <div class="meta-item">
                    <v-icon size="16" color="grey-darken-2">mdi-calendar</v-icon>
                    <span>{{ formatDate(doc.uploaded_at) }}</span>
                  </div>
                  <div class="meta-item">
                    <v-icon size="16" color="grey-darken-2">mdi-help-circle</v-icon>
                    <span>{{ doc.questions_count || 0 }}개 문제</span>
                  </div>
                </div>
              </div>
              
              <!-- 진행률 섹션 -->
              <div class="progress-container">
                <div class="progress-header">
                  <span class="progress-title">학습 진도</span>
                  <span class="progress-percentage">0%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-fill" :style="{ width: '0%' }"></div>
                </div>
              </div>
              
              <!-- 시작 버튼 -->
              <div class="action-section">
                <v-btn
                  color="primary"
                  variant="flat"
                  size="large"
                  block
                  rounded="12"
                  class="start-button"
                  @click.stop="viewDocument(doc.id)">
                  <v-icon start size="20">mdi-rocket-launch</v-icon>
                  문제 시작하기
                  <v-icon end size="18">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </div>
            
            <!-- 호버 오버레이 -->
            <div class="card-overlay"></div>
          </div>
        </div>
      </div>
    </v-container>
  </div>
  
  <!-- 삭제 확인 다이얼로그 -->
  <v-dialog v-model="deleteDialog" max-width="500" persistent>
    <v-card class="delete-dialog" rounded="20">
      <!-- 헤더 -->
      <div class="delete-header">
        <div class="delete-icon-wrapper">
          <v-icon size="28" color="white">mdi-trash-can</v-icon>
        </div>
        <div class="delete-header-content">
          <h3 class="delete-title">문서 삭제 확인</h3>
          <p class="delete-subtitle">이 작업은 되돌릴 수 없습니다</p>
        </div>
      </div>
      
      <v-divider />
      
      <!-- 내용 -->
      <v-card-text class="delete-body">
        <div class="delete-warning">
          <div class="warning-icon">
            <v-icon size="24" color="warning">mdi-alert</v-icon>
          </div>
          <div class="warning-content">
            <p class="warning-text">
              다음 문서를 영구적으로 삭제하시겠습니까?
            </p>
          </div>
        </div>
        
        <div class="file-preview">
          <div class="preview-icon">
            <v-icon size="24" color="error">mdi-file-document</v-icon>
          </div>
          <div class="preview-details">
            <div class="preview-name">{{ deletingDocumentName }}</div>
            <div class="preview-warning">이 문서와 연결된 모든 문제가 함께 삭제됩니다</div>
          </div>
        </div>
      </v-card-text>
      
      <v-divider />
      
      <!-- 액션 버튼 -->
      <v-card-actions class="delete-actions">
        <v-spacer></v-spacer>
        <v-btn
          variant="outlined"
          color="grey-darken-1"
          rounded="12"
          @click="deleteDialog = false">
          취소
        </v-btn>
        <v-btn
          color="error"
          variant="flat"
          rounded="12"
          class="ml-3 delete-confirm-btn"
          @click="deleteDocument">
          <v-icon start size="18">mdi-delete</v-icon>
          삭제하기
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PdfListView',
  data() {
    return {
      ocrDocuments: [],
      isAdmin: false,
      deleteDialog: false,
      deletingDocumentId: null,
      deletingDocumentName: '',
    };
  },
  created() {
    this.fetchOcrDocuments();
    this.checkAdminStatus();
    // eventBus를 통해 PDF 업로드 완료 이벤트를 수신
    this.$eventBus.$on('pdfUploaded', this.fetchOcrDocuments);
  },
  beforeUnmount() {
    // 컴포넌트가 파괴될 때 이벤트 리스너 제거
    this.$eventBus.$off('pdfUploaded', this.fetchOcrDocuments);
  },
  methods: {
    async fetchOcrDocuments() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:8000/ocr-documents', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        this.ocrDocuments = response.data;
      } catch (error) {
        console.error('OCR 문서 목록 불러오기 오류:', error);
      }
    },
    
    viewDocument(documentId) {
      // 문서 상세 보기 또는 문제 풀이 페이지로 이동
      this.$router.push({ name: 'PdfProblemSolver', params: { documentId: documentId } });
    },
    
    async checkAdminStatus() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:8000/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        this.isAdmin = response.data.is_admin;
      } catch (error) {
        console.error('사용자 정보 확인 오류:', error);
      }
    },
    
    confirmDelete(documentId, filename) {
      console.log('confirmDelete 호출됨 - Document ID:', documentId, 'Filename:', filename);
      this.deletingDocumentId = documentId;
      this.deletingDocumentName = this.getDisplayFilename(filename);
      this.deleteDialog = true;
    },
    
    async deleteDocument() {
      console.log('삭제 시도 중... Document ID:', this.deletingDocumentId);
      const deleteUrl = `http://127.0.0.1:8000/ocr-documents/${this.deletingDocumentId}`;
      console.log('삭제 URL:', deleteUrl);
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.delete(deleteUrl, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        console.log('삭제 응답:', response);
        // 삭제 성공 후 목록 새로고침
        this.fetchOcrDocuments();
        this.deleteDialog = false;
        this.deletingDocumentId = null;
        this.deletingDocumentName = '';
        alert('문서가 성공적으로 삭제되었습니다.');
      } catch (error) {
        console.error('문서 삭제 오류:', error);
        console.error('에러 응답:', error.response);
        if (error.response && error.response.status === 403) {
          alert('관리자 권한이 필요합니다.');
        } else if (error.response && error.response.status === 404) {
          alert('문서를 찾을 수 없습니다.');
        } else {
          alert('문서 삭제 중 오류가 발생했습니다: ' + (error.response?.data?.detail || error.message));
        }
      }
    },
    
    // 파일명 표시용 함수 (UUID 제거)
    getDisplayFilename(filename) {
      if (!filename) return '알 수 없는 파일';
      
      // UUID 패턴 제거 (예: "12345678-1234-1234-1234-123456789012_파일명.pdf" -> "파일명.pdf")
      const cleanName = filename.replace(/^[a-f0-9\-]+_/, '');
      
      // 파일명이 너무 길면 자르기
      if (cleanName.length > 50) {
        const ext = cleanName.split('.').pop();
        const name = cleanName.substring(0, 47 - ext.length);
        return `${name}...${ext}`;
      }
      
      return cleanName;
    },
    
    // 날짜 포맷팅
    formatDate(dateString) {
      if (!dateString) return '알 수 없음';
      
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) {
        return '오늘';
      } else if (diffDays === 2) {
        return '어제';
      } else if (diffDays <= 7) {
        return `${diffDays - 1}일 전`;
      } else {
        return date.toLocaleDateString('ko-KR', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      }
    }
  },
};
</script>

<style scoped>
/* 컨테이너 및 기본 레이아웃 */
.pdf-list-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.pdf-list-container::before {
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

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
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

.stats-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.stats-number {
  font-size: 2rem;
  font-weight: 800;
  color: #667eea;
  line-height: 1;
}

.stats-label {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
  margin-top: 4px;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 120px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2;
  margin: 40px 0;
}

.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.empty-animation {
  position: relative;
  margin-bottom: 32px;
}

.floating-icon {
  animation: float 3s ease-in-out infinite;
  display: inline-block;
}

.floating-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  opacity: 0.6;
}

.particle-1 {
  top: 20%;
  left: 20%;
  animation: particle-float 2s ease-in-out infinite;
}

.particle-2 {
  top: 30%;
  right: 20%;
  animation: particle-float 2.5s ease-in-out infinite 0.5s;
}

.particle-3 {
  bottom: 20%;
  left: 30%;
  animation: particle-float 3s ease-in-out infinite 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes particle-float {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6; }
  50% { transform: translate(10px, -10px) scale(1.2); opacity: 1; }
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1A1D1F;
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.empty-description {
  font-size: 1.0625rem;
  color: #6B7280;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.empty-action-btn {
  height: 48px !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.3s ease !important;
}

.empty-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;
}

/* 문서 그리드 */
.documents-grid {
  display: grid;
  gap: 32px;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  position: relative;
  z-index: 2;
  margin-top: 40px;
}

.document-card-wrapper {
  animation: slideInUp 0.6s ease-out both;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 문서 카드 */
.document-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.document-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.document-card:hover .card-overlay {
  opacity: 1;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.document-card:hover .card-background {
  opacity: 1;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

/* 카드 헤더 */
.card-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.document-icon-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.document-icon-wrapper {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.document-type-badge {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.badge-text {
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}

.status-dot.ready {
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
}

@keyframes pulse-dot {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.status-text {
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}

.delete-action {
  background: rgba(239, 68, 68, 0.2) !important;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.delete-action:hover {
  background: rgba(239, 68, 68, 0.3) !important;
  transform: scale(1.1);
}

/* 카드 본문 */
.card-body {
  padding: 32px;
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.document-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1A1D1F;
  margin: 0 0 20px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
}

.document-card:hover .document-title {
  color: #667eea;
}

/* 메타 정보 */
.document-meta {
  margin-bottom: 24px;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
}

.meta-item span {
  color: #4B5563;
}

/* 진행률 컨테이너 */
.progress-container {
  background: #F8FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 32px;
  position: relative;
}

.progress-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.document-card:hover .progress-container::before {
  opacity: 1;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.progress-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.progress-percentage {
  font-size: 0.875rem;
  font-weight: 700;
  color: #667eea;
}

.progress-track {
  width: 100%;
  height: 8px;
  background: #E5E7EB;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: progress-shimmer 2s infinite;
}

@keyframes progress-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 액션 섹션 */
.action-section {
  margin-top: auto;
  position: relative;
  z-index: 1;
}

.start-button {
  height: 56px !important;
  font-size: 1.0625rem !important;
  font-weight: 700 !important;
  text-transform: none !important;
  letter-spacing: -0.01em !important;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  position: relative;
  overflow: hidden;
}

.start-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s ease;
}

.start-button:hover::before {
  left: 100%;
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4) !important;
}

.start-button:active {
  transform: translateY(0);
}

/* 삭제 다이얼로그 */
.delete-dialog {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2) !important;
  overflow: hidden;
}

.delete-header {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.delete-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.delete-header-content {
  flex: 1;
}

.delete-title {
  font-size: 1.375rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.delete-subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 4px 0 0 0;
  font-weight: 500;
}

.delete-body {
  padding: 32px !important;
}

.delete-warning {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: #FEF3C7;
  border-radius: 12px;
  border: 1px solid #FDE68A;
}

.warning-icon {
  width: 40px;
  height: 40px;
  background: #F59E0B;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.warning-text {
  font-size: 1.0625rem;
  color: #92400e;
  font-weight: 600;
  margin: 0;
  line-height: 1.5;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #F9FAFB;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
}

.preview-icon {
  width: 48px;
  height: 48px;
  background: #FEF2F2;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.preview-details {
  flex: 1;
}

.preview-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1D1F;
  margin: 0 0 4px 0;
}

.preview-warning {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

.delete-actions {
  background: #F9FAFB;
  padding: 24px 32px !important;
  border-top: 1px solid #E5E7EB;
}

.delete-confirm-btn {
  height: 48px !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2) !important;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
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
  
  .documents-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .empty-state {
    padding: 80px 24px;
  }
  
  .card-header {
    padding: 20px;
  }
  
  .card-body {
    padding: 24px;
  }
  
  .document-title {
    font-size: 1.125rem;
  }
  
  .delete-body {
    padding: 24px !important;
  }
  
  .delete-header {
    padding: 20px 24px;
  }
}

@media (min-width: 1200px) {
  .documents-grid {
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
    gap: 40px;
  }
}

@media (max-width: 480px) {
  .document-icon-section {
    flex-direction: column;
    gap: 12px;
  }
  
  .meta-row {
    flex-direction: column;
    gap: 12px;
  }
}

/* 글로벌 오버라이드 */
.v-btn {
  text-transform: none !important;
  letter-spacing: -0.01em !important;
}

.v-card {
  border-radius: 16px !important;
}

.v-divider {
  opacity: 0.3;
}

/* 상호작용 효과 */
.start-button:active,
.delete-confirm-btn:active,
.empty-action-btn:active {
  transform: scale(0.98);
}

.document-card:active {
  transform: scale(0.98);
}

/* 접근성 */
.document-card:focus-visible,
.start-button:focus-visible,
.delete-confirm-btn:focus-visible,
.empty-action-btn:focus-visible {
  outline: 3px solid rgba(102, 126, 234, 0.5);
  outline-offset: 2px;
}

/* 로딩 및 호버 효과 */
.document-card::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
  border-radius: 26px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
  animation: gradient-shift 3s ease infinite;
  background-size: 400% 400%;
}

.document-card:hover::before {
  opacity: 1;
}

@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
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

/* 컴팩트 모드 지원 */
@media (max-width: 380px) {
  .documents-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .document-card {
    margin: 0 8px;
  }
  
  .hero-header {
    padding: 16px 0;
  }
  
  .hero-title {
    font-size: 1.75rem;
  }
}

/* 고해상도 디스플레이 지원 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .document-card {
    border-width: 0.5px;
  }
  
  .card-background,
  .card-overlay {
    background-size: 200% 200%;
  }
}
</style>