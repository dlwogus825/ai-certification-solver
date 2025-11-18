<template>
  <v-container class="pa-6">
    <!-- 헤더 -->
    <div class="hero-section mb-8">
      <div class="d-flex justify-space-between align-center">
        <div class="hero-content">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="primary" class="mr-3">mdi-bullhorn</v-icon>
            <h1 class="text-h3 font-weight-bold gradient-text">공지사항</h1>
          </div>
          <p class="text-h6 text-grey-darken-1 mb-0">
            <v-icon size="20" class="mr-2">mdi-information</v-icon>
            중요한 소식과 업데이트를 확인하세요
          </p>
        </div>
        <v-btn
          v-if="isAdmin"
          color="primary"
          size="large"
          prepend-icon="mdi-plus"
          variant="elevated"
          class="write-btn"
          @click="openWriteDialog">
          <span class="font-weight-bold">공지사항 작성</span>
        </v-btn>
      </div>
      <v-divider class="mt-6 mb-2"></v-divider>
    </div>

    <!-- 검색 및 필터 -->
    <v-card class="filter-card mb-8" elevation="3" rounded="xl">
      <v-card-text class="pa-6">
        <div class="d-flex align-center mb-4">
          <v-icon color="primary" class="mr-2">mdi-filter-variant</v-icon>
          <span class="text-h6 font-weight-medium">필터 및 검색</span>
        </div>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="searchQuery"
              label="공지사항 검색"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              color="primary"
              bg-color="grey-lighten-5"
              hide-details>
            </v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedCategory"
              :items="categories"
              label="카테고리"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              density="comfortable"
              clearable
              color="primary"
              bg-color="grey-lighten-5"
              hide-details>
            </v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="정렬"
              prepend-inner-icon="mdi-sort"
              variant="outlined"
              density="comfortable"
              color="primary"
              bg-color="grey-lighten-5"
              hide-details>
            </v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 공지사항 목록 -->
    <div class="announcements-grid">
      <v-card
        v-for="announcement in paginatedAnnouncements"
        :key="announcement.id"
        class="announcement-card"
        elevation="4"
        rounded="xl"
        @click="openAnnouncement(announcement)"
        :class="{ 'important': announcement.isImportant }">
          
          <!-- 카드 헤더 -->
          <div class="card-header" :class="{ 'important-header': announcement.isImportant }">
            <div class="d-flex justify-space-between align-center pa-4">
              <div class="d-flex align-center">
                <v-chip
                  :color="getCategoryColor(announcement.category)"
                  size="small"
                  variant="elevated"
                  class="mr-2 font-weight-bold">
                  <v-icon size="16" class="mr-1">{{ getCategoryIcon(announcement.category) }}</v-icon>
                  {{ announcement.category }}
                </v-chip>
                <v-chip
                  v-if="announcement.isImportant"
                  color="error"
                  size="small"
                  variant="elevated"
                  prepend-icon="mdi-star"
                  class="pulse-animation">
                  중요
                </v-chip>
              </div>
              <div class="text-caption text-grey-darken-2 font-weight-medium">
                <v-icon size="16" class="mr-1">mdi-clock-outline</v-icon>
                {{ formatDate(announcement.createdAt) }}
              </div>
            </div>
          </div>
          
          <!-- 카드 내용 -->
          <v-card-text class="pa-5">
            <h3 class="text-h5 mb-3 announcement-title font-weight-bold">
              {{ announcement.title }}
            </h3>
            
            <p class="text-body-1 text-grey-darken-1 announcement-preview mb-4">
              {{ announcement.preview }}
            </p>
            
            <!-- 카드 푸터 -->
            <div class="d-flex justify-space-between align-center card-footer">
              <div class="d-flex align-center">
                <v-avatar size="24" color="primary" class="mr-2">
                  <v-icon size="16">mdi-account</v-icon>
                </v-avatar>
                <span class="text-body-2 font-weight-medium">{{ announcement.author }}</span>
              </div>
              <div class="d-flex align-center">
                <v-chip
                  size="small"
                  variant="text"
                  color="grey-darken-1"
                  prepend-icon="mdi-eye">
                  {{ announcement.views }}
                </v-chip>
                <v-icon color="primary" class="ml-2">mdi-chevron-right</v-icon>
              </div>
            </div>
          </v-card-text>
        </v-card>
    </div>

    <!-- 빈 상태 -->
    <v-card 
      v-if="filteredAnnouncements.length === 0" 
      class="empty-state text-center pa-12" 
      elevation="2" 
      rounded="xl">
      <div class="empty-icon mb-6">
        <v-icon size="80" color="grey-lighten-2">mdi-bulletin-board</v-icon>
      </div>
      <h3 class="text-h5 mb-3 font-weight-bold text-grey-darken-2">공지사항이 없습니다</h3>
      <p class="text-body-1 text-grey-darken-1 mb-0">
        새로운 공지사항이 있으면 여기에 표시됩니다.
      </p>
    </v-card>

    <!-- 페이지네이션 -->
    <div class="d-flex justify-center mt-8" v-if="totalPages > 1">
      <v-pagination
        v-model="currentPage"
        :length="totalPages"
        :total-visible="7"
        color="primary"
        variant="elevated"
        rounded="circle"
        size="large">
      </v-pagination>
    </div>

    <!-- 공지사항 상세 보기 다이얼로그 -->
    <v-dialog v-model="showDetailDialog" max-width="1000" scrollable>
      <v-card v-if="selectedAnnouncement" class="announcement-detail-card">
        <!-- 헤더 -->
        <div class="detail-header">
          <div class="detail-header-content">
            <div class="detail-badges">
              <v-chip
                :color="getCategoryColor(selectedAnnouncement.category)"
                variant="flat"
                size="small"
                label>
                <v-icon start size="14">{{ getCategoryIcon(selectedAnnouncement.category) }}</v-icon>
                {{ selectedAnnouncement.category }}
              </v-chip>
              <v-chip
                v-if="selectedAnnouncement.isImportant"
                color="error"
                variant="flat"
                size="small"
                label
                class="ml-2">
                <v-icon start size="14">mdi-star</v-icon>
                중요 공지
              </v-chip>
            </div>
            <h1 class="detail-title">{{ selectedAnnouncement.title }}</h1>
            <div class="detail-meta">
              <div class="meta-item">
                <v-icon size="18" color="grey-darken-2">mdi-account-circle</v-icon>
                <span>{{ selectedAnnouncement.author }}</span>
              </div>
              <v-divider vertical class="mx-3" />
              <div class="meta-item">
                <v-icon size="18" color="grey-darken-2">mdi-calendar</v-icon>
                <span>{{ formatDate(selectedAnnouncement.createdAt) }}</span>
              </div>
              <v-divider vertical class="mx-3" />
              <div class="meta-item">
                <v-icon size="18" color="grey-darken-2">mdi-eye</v-icon>
                <span>조회수 {{ selectedAnnouncement.views }}</span>
              </div>
            </div>
          </div>
          
          <!-- 액션 버튼들 -->
          <div class="detail-actions">
            <v-btn
              v-if="isAdmin"
              variant="tonal"
              color="primary"
              size="small"
              @click="editAnnouncement(selectedAnnouncement)">
              <v-icon start size="18">mdi-pencil</v-icon>
              수정
            </v-btn>
            <v-btn
              v-if="isAdmin"
              variant="tonal"
              color="error"
              size="small"
              @click="showDeleteConfirm = true"
              class="ml-2">
              <v-icon start size="18">mdi-delete</v-icon>
              삭제
            </v-btn>
            <v-btn 
              icon="mdi-close"
              variant="text"
              size="small"
              @click="showDetailDialog = false"
              class="ml-auto">
            </v-btn>
          </div>
        </div>
        
        <!-- 내용 -->
        <v-divider />
        <v-card-text class="detail-content">
          <div class="announcement-content" v-html="selectedAnnouncement.content">
          </div>
        </v-card-text>
        
        <!-- 푸터 -->
        <v-divider />
        <v-card-actions class="detail-footer">
          <v-spacer />
          <v-btn
            variant="flat"
            color="primary"
            @click="showDetailDialog = false">
            확인
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 공지사항 작성 다이얼로그 (관리자만) -->
    <v-dialog v-model="showWriteDialog" max-width="800" scrollable>
      <v-card>
        <v-card-title>
          <h2 class="text-h5">{{ isEditing ? '공지사항 수정' : '공지사항 작성' }}</h2>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-6">
          <v-form ref="writeForm">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="newAnnouncement.title"
                  label="제목"
                  variant="outlined"
                  :rules="[v => !!v || '제목을 입력해주세요']"
                  required>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="newAnnouncement.category"
                  :items="categories"
                  label="카테고리"
                  variant="outlined"
                  required>
                </v-select>
              </v-col>
            </v-row>
            
            <v-checkbox
              v-model="newAnnouncement.isImportant"
              label="중요 공지사항"
              color="error">
            </v-checkbox>
            
            <v-textarea
              v-model="newAnnouncement.content"
              label="내용"
              variant="outlined"
              rows="10"
              :rules="[v => !!v || '내용을 입력해주세요']"
              required>
            </v-textarea>
          </v-form>
        </v-card-text>
        
        <v-card-actions class="pa-6">
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="closeWriteDialog">
            취소
          </v-btn>
          <v-btn
            color="primary"
            @click="saveAnnouncement">
            {{ isEditing ? '수정' : '저장' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 삭제 확인 다이얼로그 -->
    <v-dialog v-model="showDeleteConfirm" max-width="400">
      <v-card>
        <v-card-title>
          <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
          공지사항 삭제
        </v-card-title>
        
        <v-card-text>
          <p>정말로 이 공지사항을 삭제하시겠습니까?</p>
          <p class="text-error font-weight-bold">삭제된 공지사항은 복구할 수 없습니다.</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="showDeleteConfirm = false">
            취소
          </v-btn>
          <v-btn
            color="error"
            @click="deleteAnnouncement">
            삭제
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  name: 'Announcements',
  data() {
    return {
      searchQuery: '',
      selectedCategory: null,
      sortBy: '최신순',
      currentPage: 1,
      itemsPerPage: 10,
      showDetailDialog: false,
      showWriteDialog: false,
      showDeleteConfirm: false,
      selectedAnnouncement: null,
      isEditing: false,
      
      // 더미 데이터 (localStorage에서 불러오거나 기본값 사용)
      announcements: [
        {
          id: 1,
          title: 'AI 자격증 학습 플랫폼 오픈!',
          content: `
            <h3>AI 자격증 학습 플랫폼에 오신 것을 환영합니다!</h3>
            <p>저희 플랫폼은 다음과 같은 기능을 제공합니다:</p>
            <ul>
              <li>PDF 업로드를 통한 자동 문제 추출</li>
              <li>AI 기반 문제 해설</li>
              <li>개인별 학습 진도 관리</li>
              <li>다양한 자격증 문제 지원</li>
            </ul>
            <p>궁금한 점이 있으시면 언제든 문의해 주세요!</p>
          `,
          preview: '새로운 AI 자격증 학습 플랫폼이 오픈했습니다. 다양한 기능을 활용해보세요!',
          category: '시스템',
          author: '관리자',
          createdAt: new Date('2025-01-20'),
          views: 156,
          isImportant: true
        },
        {
          id: 2,
          title: '서버 정기점검 안내',
          content: `
            <h3>서버 정기점검 안내</h3>
            <p><strong>점검 일시:</strong> 2025년 1월 25일 (토) 02:00 - 06:00</p>
            <p><strong>점검 내용:</strong></p>
            <ul>
              <li>서버 성능 최적화</li>
              <li>보안 업데이트</li>
              <li>데이터베이스 정리</li>
            </ul>
            <p>점검 시간 동안 서비스 이용이 제한될 수 있습니다. 양해 부탁드립니다.</p>
          `,
          preview: '1월 25일 새벽 서버 정기점검이 진행됩니다.',
          category: '점검',
          author: '시스템관리자',
          createdAt: new Date('2025-01-18'),
          views: 89,
          isImportant: true
        },
        {
          id: 3,
          title: '새로운 자격증 과목 추가',
          content: `
            <h3>새로운 자격증 과목이 추가되었습니다!</h3>
            <p>다음 자격증 과목들이 새롭게 추가되었습니다:</p>
            <ul>
              <li>정보처리기사</li>
              <li>컴활 1급</li>
              <li>ITQ 자격증</li>
            </ul>
            <p>더 많은 자격증 준비를 도와드리겠습니다!</p>
          `,
          preview: '정보처리기사, 컴활 1급 등 새로운 자격증 과목이 추가되었습니다.',
          category: '업데이트',
          author: '관리자',
          createdAt: new Date('2025-01-15'),
          views: 234,
          isImportant: false
        }
      ],
      
      categories: ['전체', '시스템', '업데이트', '점검', '이벤트', '기타'],
      sortOptions: ['최신순', '오래된순', '조회수순'],
      
      // 새 공지사항 작성 폼
      newAnnouncement: {
        title: '',
        content: '',
        category: '시스템',
        isImportant: false
      }
    };
  },
  computed: {
    isAdmin() {
      const token = localStorage.getItem('access_token');
      if (!token) return false;
      
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        return payload.is_admin === true;
      } catch (e) {
        return false;
      }
    },
    
    filteredAnnouncements() {
      let filtered = [...this.announcements];
      
      // 카테고리 필터
      if (this.selectedCategory && this.selectedCategory !== '전체') {
        filtered = filtered.filter(a => a.category === this.selectedCategory);
      }
      
      // 검색 필터
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(a => 
          a.title.toLowerCase().includes(query) ||
          a.content.toLowerCase().includes(query) ||
          a.preview.toLowerCase().includes(query)
        );
      }
      
      // 정렬
      filtered = [...filtered];  // 복사본 생성
      if (this.sortBy === '최신순') {
        filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      } else if (this.sortBy === '오래된순') {
        filtered.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      } else if (this.sortBy === '조회수순') {
        filtered.sort((a, b) => b.views - a.views);
      }
      
      // 중요 공지사항을 상단에 배치
      filtered.sort((a, b) => b.isImportant - a.isImportant);
      
      return filtered;
    },
    
    totalPages() {
      return Math.ceil(this.filteredAnnouncements.length / this.itemsPerPage);
    },
    
    paginatedAnnouncements() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredAnnouncements.slice(start, end);
    }
  },
  
  mounted() {
    this.loadAnnouncements();
  },
  
  methods: {
    // localStorage에서 공지사항 불러오기
    loadAnnouncements() {
      const saved = localStorage.getItem('announcements');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          // 날짜 객체 복원
          this.announcements = parsed.map(a => ({
            ...a,
            createdAt: new Date(a.createdAt)
          }));
        } catch (e) {
          console.warn('Failed to load announcements from localStorage:', e);
        }
      } else {
        // 첫 방문 시 localStorage에 기본 데이터 저장
        this.saveAnnouncementsToStorage();
      }
    },
    
    // localStorage에 공지사항 저장
    saveAnnouncementsToStorage() {
      try {
        localStorage.setItem('announcements', JSON.stringify(this.announcements));
      } catch (e) {
        console.warn('Failed to save announcements to localStorage:', e);
      }
    },
    openAnnouncement(announcement) {
      this.selectedAnnouncement = { ...announcement };
      this.showDetailDialog = true;
      // 조회수 증가 (실제로는 API 호출)
      const index = this.announcements.findIndex(a => a.id === announcement.id);
      if (index !== -1) {
        this.announcements[index].views++;
        this.saveAnnouncementsToStorage(); // localStorage에 저장
      }
    },
    
    getCategoryColor(category) {
      const colors = {
        '시스템': 'primary',
        '업데이트': 'success',
        '점검': 'warning',
        '이벤트': 'secondary',
        '기타': 'info'
      };
      return colors[category] || 'grey';
    },
    
    getCategoryIcon(category) {
      const icons = {
        '시스템': 'mdi-cog',
        '업데이트': 'mdi-update',
        '점검': 'mdi-wrench',
        '이벤트': 'mdi-party-popper',
        '기타': 'mdi-information'
      };
      return icons[category] || 'mdi-tag';
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    async saveAnnouncement() {
      // 간단한 검증
      if (!this.newAnnouncement.title || !this.newAnnouncement.content) {
        alert('제목과 내용을 입력해주세요.');
        return;
      }
      
      if (this.isEditing) {
        // 수정 모드
        const index = this.announcements.findIndex(a => a.id === this.newAnnouncement.id);
        if (index !== -1) {
          this.announcements[index] = {
            ...this.announcements[index],
            ...this.newAnnouncement,
            preview: this.newAnnouncement.content.substring(0, 100) + '...'
          };
          this.saveAnnouncementsToStorage();
          alert('공지사항이 수정되었습니다.');
        }
      } else {
        // 새 공지사항 작성
        const newId = Math.max(...this.announcements.map(a => a.id)) + 1;
        const announcement = {
          id: newId,
          ...this.newAnnouncement,
          author: '관리자',
          createdAt: new Date(),
          views: 0,
          preview: this.newAnnouncement.content.substring(0, 100) + '...'
        };
        
        this.announcements = [announcement, ...this.announcements];
        this.saveAnnouncementsToStorage();
        alert('공지사항이 저장되었습니다.');
      }
      
      // 폼 초기화
      this.resetForm();
      this.showWriteDialog = false;
    },
    
    editAnnouncement(announcement) {
      this.isEditing = true;
      this.newAnnouncement = {
        id: announcement.id,
        title: announcement.title,
        content: announcement.content,
        category: announcement.category,
        isImportant: announcement.isImportant
      };
      this.showDetailDialog = false;
      this.showWriteDialog = true;
    },
    
    deleteAnnouncement() {
      if (this.selectedAnnouncement) {
        this.announcements = this.announcements.filter(a => a.id !== this.selectedAnnouncement.id);
        this.saveAnnouncementsToStorage();
        this.showDeleteConfirm = false;
        this.showDetailDialog = false;
        alert('공지사항이 삭제되었습니다.');
      }
    },
    
    resetForm() {
      this.isEditing = false;
      this.newAnnouncement = {
        title: '',
        content: '',
        category: '시스템',
        isImportant: false
      };
    },
    
    openWriteDialog() {
      this.resetForm();
      this.showWriteDialog = true;
    },
    
    closeWriteDialog() {
      this.resetForm();
      this.showWriteDialog = false;
    }
  }
};
</script>

<style scoped>
/* 헤더 스타일 */
.hero-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.gradient-text {
  background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.write-btn {
  box-shadow: 0 8px 24px rgba(25, 118, 210, 0.3) !important;
  transition: all 0.3s ease;
}

.write-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(25, 118, 210, 0.4) !important;
}

/* 필터 카드 스타일 */
.filter-card {
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid rgba(25, 118, 210, 0.1);
}

/* 공지사항 그리드 */
.announcements-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
}

/* 공지사항 카드 스타일 */
.announcement-card {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  background: linear-gradient(145deg, #ffffff 0%, #fafbfc 100%);
  position: relative;
  overflow: hidden;
}

.announcement-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1976D2, #42A5F5);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.announcement-card:hover::before {
  transform: scaleX(1);
}

.announcement-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.announcement-card.important {
  border-left: 4px solid #f44336;
  background: linear-gradient(145deg, #fff5f5 0%, #ffffff 100%);
}

.announcement-card.important::before {
  background: linear-gradient(90deg, #f44336, #ff7961);
}

/* 카드 헤더 */
.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.important-header {
  background: linear-gradient(135deg, #ffebee 0%, #f8f9fa 100%);
}

/* 제목 스타일 */
.announcement-title {
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #2c3e50;
  transition: color 0.3s ease;
}

.announcement-card:hover .announcement-title {
  color: #1976D2;
}

/* 프리뷰 텍스트 */
.announcement-preview {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
}

/* 카드 푸터 */
.card-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding-top: 1rem;
  margin-top: 1rem;
}

/* 애니메이션 */
.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* 빈 상태 스타일 */
.empty-state {
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
}

.empty-icon {
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.empty-state:hover .empty-icon {
  opacity: 1;
}

/* 상세보기 다이얼로그 */
.announcement-detail-card {
  border-radius: 20px !important;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

.detail-header {
  background: linear-gradient(to bottom, #FFFFFF, #FAFBFC);
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.detail-header-content {
  flex: 1;
  max-width: 100%;
}

.detail-badges {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1A1D1F;
  line-height: 1.25;
  margin: 0 0 20px 0;
  letter-spacing: -0.02em;
  word-break: keep-all;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  color: #6B7280;
  font-size: 0.9375rem;
  font-weight: 500;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item span {
  color: #4B5563;
}

.detail-actions {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex-shrink: 0;
}

.detail-content {
  padding: 56px 64px !important;
  background: #FFFFFF;
  min-height: 400px;
}

/* 공지사항 내용 스타일 */
.announcement-content {
  max-width: 800px;
  margin: 0 auto;
  font-size: 1.1875rem;
  line-height: 1.85;
  color: #1F2937;
  font-weight: 400;
}

.announcement-content h3 {
  font-size: 1.625rem;
  font-weight: 700;
  color: #111827;
  margin: 40px 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 3px solid #E5E7EB;
  letter-spacing: -0.01em;
}

.announcement-content h3:first-child {
  margin-top: 0;
}

.announcement-content p {
  margin-bottom: 24px;
  text-align: left;
  word-break: keep-all;
  letter-spacing: -0.01em;
}

.announcement-content ul {
  margin: 28px 0;
  padding-left: 0;
  list-style: none;
}

.announcement-content li {
  margin-bottom: 16px;
  line-height: 1.85;
  color: #374151;
  padding-left: 32px;
  position: relative;
  font-weight: 400;
}

.announcement-content li::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 10px;
  width: 6px;
  height: 6px;
  background: #2196F3;
  border-radius: 50%;
}

.announcement-content strong {
  font-weight: 700;
  color: #111827;
  background: linear-gradient(to bottom, transparent 60%, #FEF3C7 60%);
  padding: 0 2px;
}

.detail-footer {
  background: #F9FAFB;
  padding: 20px 32px !important;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    padding: 20px;
  }
  
  .detail-title {
    font-size: 1.75rem;
  }
  
  .detail-content {
    padding: 32px 24px !important;
  }
  
  .announcement-content {
    font-size: 1.0625rem;
  }
  
  .detail-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

/* 반응형 디자인 */
@media (min-width: 768px) {
  .announcements-grid {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }
}

@media (min-width: 1200px) {
  .announcements-grid {
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  }
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #1976D2, #42A5F5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #1565C0, #1976D2);
}
</style>