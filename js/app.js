/**
 * 원격학습 플랫폼 - 메인 애플리케이션
 */

class LearningPlatform {
    constructor() {
        this.currentChapter = -1;
        this.currentVersion = this.loadVersion(); // 'full' or 'abridged'
        this.chaptersData = this.getChaptersData();
        this.completedChapters = this.loadProgress();
        this.searchIndex = [];
        this.feedbacks = this.loadFeedbacks();
        this.currentPracticeCategory = null;
        this.currentLesson = null;
        
        this.init();
    }
    
    // ===== Version Management =====
    loadVersion() {
        return localStorage.getItem('learningVersion') || 'full';
    }
    
    saveVersion(version) {
        localStorage.setItem('learningVersion', version);
        this.currentVersion = version;
    }
    
    getChaptersData() {
        return this.currentVersion === 'abridged' ? CHAPTERS_DATA_ABRIDGED : CHAPTERS_DATA;
    }
    
    switchVersion(version) {
        this.saveVersion(version);
        this.chaptersData = this.getChaptersData();
        this.renderNavMenu();
        this.renderChapterGrid();
        this.updateProgress();
        this.buildSearchIndex();
        this.updateVersionIndicator();
        this.showToast(version === 'abridged' ? '⚡ 축약본으로 전환되었습니다' : '📚 원본으로 전환되었습니다');
    }
    
    updateVersionIndicator() {
        const indicator = document.getElementById('versionIndicator');
        if (indicator) {
            indicator.innerHTML = this.currentVersion === 'abridged' 
                ? '<span style="color: #10b981;">⚡ 축약본</span>'
                : '<span style="color: #6366f1;">📚 원본</span>';
        }
    }
    
    init() {
        this.bindElements();
        this.bindEvents();
        this.renderNavMenu();
        this.renderChapterGrid();
        this.updateProgress();
        this.loadTheme();
        this.buildSearchIndex();
        this.initFeedbackSystem();
        this.updateFeedbackCount();
        this.initPracticeSystem();
        this.updateVersionIndicator();
    }
    
    bindElements() {
        // Sidebar
        this.sidebar = document.getElementById('sidebar');
        this.sidebarClose = document.getElementById('sidebarClose');
        this.menuToggle = document.getElementById('menuToggle');
        this.navMenu = document.getElementById('navMenu');
        this.themeToggle = document.getElementById('themeToggle');
        this.progressFill = document.getElementById('progressFill');
        this.progressPercent = document.getElementById('progressPercent');
        
        // Sections
        this.homeSection = document.getElementById('homeSection');
        this.chapterSection = document.getElementById('chapterSection');
        this.searchSection = document.getElementById('searchSection');
        
        // Home
        this.chapterGrid = document.getElementById('chapterGrid');
        this.startLearningFull = document.getElementById('startLearningFull');
        this.startLearningAbridged = document.getElementById('startLearningAbridged');
        
        // Chapter
        this.chapterContent = document.getElementById('chapterContent');
        this.backToHome = document.getElementById('backToHome');
        this.prevChapter = document.getElementById('prevChapter');
        this.nextChapter = document.getElementById('nextChapter');
        this.prevChapter2 = document.getElementById('prevChapter2');
        this.nextChapter2 = document.getElementById('nextChapter2');
        this.completeCheckbox = document.getElementById('completeCheckbox');
        
        // Search
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.searchResults = document.getElementById('searchResults');
        
        // Practice
        this.practiceSection = document.getElementById('practiceSection');
        this.practiceCategories = document.getElementById('practiceCategories');
        this.practiceDetail = document.getElementById('practiceDetail');
        this.practiceContent = document.getElementById('practiceContent');
    }
    
    bindEvents() {
        // Sidebar toggle
        this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        this.sidebarClose.addEventListener('click', () => this.closeSidebar());
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Navigation - Version selection (Home page)
        if (this.startLearningFull) {
            this.startLearningFull.addEventListener('click', () => {
                this.switchVersion('full');
                this.clickNavItem(0);
            });
        }
        if (this.startLearningAbridged) {
            this.startLearningAbridged.addEventListener('click', () => {
                this.switchVersion('abridged');
                this.clickNavItem(0);
            });
        }
        
        // Version switch buttons (Sidebar)
        const switchToFull = document.getElementById('switchToFull');
        const switchToAbridged = document.getElementById('switchToAbridged');
        if (switchToFull) {
            switchToFull.addEventListener('click', () => this.switchVersion('full'));
        }
        if (switchToAbridged) {
            switchToAbridged.addEventListener('click', () => this.switchVersion('abridged'));
        }
        
        this.backToHome.addEventListener('click', () => this.showHome());
        
        this.prevChapter.addEventListener('click', () => this.navigateChapter(-1));
        this.nextChapter.addEventListener('click', () => this.navigateChapter(1));
        this.prevChapter2.addEventListener('click', () => this.navigateChapter(-1));
        this.nextChapter2.addEventListener('click', () => this.navigateChapter(1));
        
        // Complete checkbox
        this.completeCheckbox.addEventListener('change', (e) => {
            this.toggleComplete(this.currentChapter, e.target.checked);
        });
        
        // Search
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // Close sidebar on outside click (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 1024 && 
                this.sidebar.classList.contains('open') &&
                !this.sidebar.contains(e.target) &&
                !this.menuToggle.contains(e.target)) {
                this.closeSidebar();
            }
        });
    }
    
    // ===== Sidebar =====
    toggleSidebar() {
        this.sidebar.classList.toggle('open');
    }
    
    closeSidebar() {
        this.sidebar.classList.remove('open');
    }
    
    // ===== Theme =====
    toggleTheme() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
        localStorage.setItem('theme', isDark ? 'light' : 'dark');
        this.updateThemeButton();
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeButton();
    }
    
    updateThemeButton() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        this.themeToggle.innerHTML = isDark 
            ? '<span class="theme-icon">☀️</span><span>라이트모드</span>'
            : '<span class="theme-icon">🌙</span><span>다크모드</span>';
    }
    
    // ===== Progress =====
    loadProgress() {
        const saved = localStorage.getItem('completedChapters');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveProgress() {
        localStorage.setItem('completedChapters', JSON.stringify(this.completedChapters));
    }
    
    updateProgress() {
        const total = this.chaptersData.length;
        const completed = this.completedChapters.length;
        const percent = Math.round((completed / total) * 100);
        
        this.progressFill.style.width = `${percent}%`;
        this.progressPercent.textContent = `${percent}%`;
    }
    
    toggleComplete(chapterId, isComplete) {
        if (isComplete && !this.completedChapters.includes(chapterId)) {
            this.completedChapters.push(chapterId);
        } else if (!isComplete) {
            this.completedChapters = this.completedChapters.filter(id => id !== chapterId);
        }
        
        this.saveProgress();
        this.updateProgress();
        this.renderNavMenu();
        this.renderChapterGrid();
    }
    
    // ===== Navigation Menu =====
    renderNavMenu() {
        this.navMenu.innerHTML = '';
        
        this.chaptersData.forEach((chapter, index) => {
            const isCompleted = this.completedChapters.includes(index);
            const isActive = this.currentChapter === index;
            
            const navItem = document.createElement('div');
            navItem.className = `nav-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`;
            navItem.setAttribute('data-chapter', index);
            navItem.innerHTML = `
                <span class="nav-chapter-num">${isCompleted ? '✓' : index}</span>
                <span>${chapter.title}</span>
            `;
            navItem.addEventListener('click', () => {
                this.openChapter(index);
                this.closeSidebar();
            });
            
            this.navMenu.appendChild(navItem);
        });
    }
    
    // ===== Chapter Grid =====
    renderChapterGrid() {
        this.chapterGrid.innerHTML = '';
        
        this.chaptersData.forEach((chapter, index) => {
            const isCompleted = this.completedChapters.includes(index);
            
            const card = document.createElement('div');
            card.className = `chapter-card ${isCompleted ? 'completed' : ''}`;
            card.innerHTML = `
                <div class="chapter-card-header">
                    <div class="chapter-num"><span>${index}</span></div>
                    <h3>${chapter.title}</h3>
                </div>
                <p>${chapter.description}</p>
            `;
            card.addEventListener('click', () => this.clickNavItem(index));
            
            this.chapterGrid.appendChild(card);
        });
    }
    
    // ===== Chapter View =====
    showHome() {
        this.currentChapter = -1;
        this.homeSection.style.display = 'block';
        this.chapterSection.style.display = 'none';
        this.searchSection.style.display = 'none';
        this.renderNavMenu();
        window.scrollTo(0, 0);
    }
    
    openChapter(index) {
        if (index < 0 || index >= this.chaptersData.length) return;
        
        this.currentChapter = index;
        const chapter = this.chaptersData[index];
        
        // Update content
        this.chapterContent.innerHTML = chapter.content;
        
        // Update checkbox
        this.completeCheckbox.checked = this.completedChapters.includes(index);
        
        // Update navigation buttons
        this.prevChapter.disabled = index === 0;
        this.prevChapter2.disabled = index === 0;
        this.nextChapter.disabled = index === this.chaptersData.length - 1;
        this.nextChapter2.disabled = index === this.chaptersData.length - 1;
        
        // Show chapter section
        this.homeSection.style.display = 'none';
        this.chapterSection.style.display = 'block';
        this.searchSection.style.display = 'none';
        
        // Update nav menu
        this.renderNavMenu();
        
        // Scroll to chapter section top
        this.chapterSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    navigateChapter(direction) {
        const newIndex = this.currentChapter + direction;
        if (newIndex >= 0 && newIndex < this.chaptersData.length) {
            this.clickNavItem(newIndex);
        }
    }
    
    // 사이드바 nav-item 클릭 헬퍼
    clickNavItem(index) {
        const navItem = this.navMenu.querySelector(`[data-chapter="${index}"]`);
        if (navItem) {
            navItem.click();
        } else {
            this.openChapter(index);
        }
    }
    
    // ===== Search =====
    buildSearchIndex() {
        this.searchIndex = this.chaptersData.map((chapter, index) => ({
            id: index,
            title: chapter.title,
            description: chapter.description,
            // Strip HTML tags for search
            text: chapter.content.replace(/<[^>]*>/g, ' ').toLowerCase()
        }));
    }
    
    performSearch() {
        const query = this.searchInput.value.trim().toLowerCase();
        if (!query) return;
        
        const results = this.searchIndex.filter(item => 
            item.title.toLowerCase().includes(query) ||
            item.description.toLowerCase().includes(query) ||
            item.text.includes(query)
        );
        
        this.showSearchResults(query, results);
    }
    
    showSearchResults(query, results) {
        this.homeSection.style.display = 'none';
        this.chapterSection.style.display = 'none';
        this.searchSection.style.display = 'block';
        
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <p style="text-align: center; color: var(--text-light); padding: 40px;">
                    "${query}"에 대한 검색 결과가 없습니다.
                </p>
            `;
            return;
        }
        
        this.searchResults.innerHTML = results.map(result => {
            // Find snippet with query
            const textIndex = result.text.indexOf(query);
            let snippet = '';
            if (textIndex !== -1) {
                const start = Math.max(0, textIndex - 50);
                const end = Math.min(result.text.length, textIndex + query.length + 100);
                snippet = '...' + result.text.substring(start, end).replace(
                    new RegExp(query, 'gi'),
                    match => `<mark>${match}</mark>`
                ) + '...';
            }
            
            return `
                <div class="search-result-item" data-chapter="${result.id}">
                    <h4>${result.title}</h4>
                    <p>${result.description}</p>
                    ${snippet ? `<p style="font-size: 13px; margin-top: 10px;">${snippet}</p>` : ''}
                </div>
            `;
        }).join('');
        
        // Bind click events
        this.searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const chapterId = parseInt(item.dataset.chapter);
                this.openChapter(chapterId);
            });
        });
    }
    
    // ===== Feedback System =====
    loadFeedbacks() {
        const saved = localStorage.getItem('betaFeedbacks');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveFeedbacks() {
        localStorage.setItem('betaFeedbacks', JSON.stringify(this.feedbacks));
    }
    
    initFeedbackSystem() {
        // Elements
        this.feedbackFab = document.getElementById('feedbackFab');
        this.feedbackModal = document.getElementById('feedbackModal');
        this.feedbackListModal = document.getElementById('feedbackListModal');
        this.feedbackForm = document.getElementById('feedbackForm');
        this.modalClose = document.getElementById('modalClose');
        this.listModalClose = document.getElementById('listModalClose');
        this.cancelFeedback = document.getElementById('cancelFeedback');
        this.viewFeedbackList = document.getElementById('viewFeedbackList');
        this.feedbackCount = document.getElementById('feedbackCount');
        this.toast = document.getElementById('toast');
        
        // Form fields
        this.readerName = document.getElementById('readerName');
        this.currentChapterDisplay = document.getElementById('currentChapterDisplay');
        this.feedbackType = document.getElementById('feedbackType');
        this.selectedText = document.getElementById('selectedText');
        this.feedbackContent = document.getElementById('feedbackContent');
        
        // List elements
        this.feedbackList = document.getElementById('feedbackList');
        this.feedbackStats = document.getElementById('feedbackStats');
        this.filterChapter = document.getElementById('filterChapter');
        this.filterType = document.getElementById('filterType');
        this.exportFeedback = document.getElementById('exportFeedback');
        this.exportJSON = document.getElementById('exportJSON');
        this.importJSON = document.getElementById('importJSON');
        
        // Bind events - use named function to prevent duplicate listeners
        if (!this.feedbackFab._listenerAdded) {
            this.feedbackFab.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('FAB clicked');
                this.openFeedbackModal();
            });
            this.feedbackFab._listenerAdded = true;
        }
        this.modalClose.addEventListener('click', () => this.closeFeedbackModal());
        this.cancelFeedback.addEventListener('click', () => this.closeFeedbackModal());
        this.listModalClose.addEventListener('click', () => this.closeFeedbackListModal());
        this.viewFeedbackList.addEventListener('click', () => this.openFeedbackListModal());
        this.feedbackForm.addEventListener('submit', (e) => this.submitFeedback(e));
        this.exportFeedback.addEventListener('click', () => this.exportFeedbackData());
        this.exportJSON.addEventListener('click', () => this.exportFeedbackJSON());
        this.importJSON.addEventListener('change', (e) => this.importFeedbackJSON(e));
        this.filterChapter.addEventListener('change', () => this.renderFeedbackList());
        this.filterType.addEventListener('change', () => this.renderFeedbackList());
        
        // Close modal on overlay click
        this.feedbackModal.addEventListener('click', (e) => {
            if (e.target === this.feedbackModal) this.closeFeedbackModal();
        });
        this.feedbackListModal.addEventListener('click', (e) => {
            if (e.target === this.feedbackListModal) this.closeFeedbackListModal();
        });
        
        // Text selection for feedback
        document.addEventListener('mouseup', () => this.captureSelectedText());
        
        // Load saved reader name
        const savedName = localStorage.getItem('betaReaderName');
        if (savedName) this.readerName.value = savedName;
        
        // Populate chapter filter
        this.populateChapterFilter();
    }
    
    captureSelectedText() {
        const selection = window.getSelection();
        const text = selection.toString().trim();
        
        if (text && text.length > 0 && text.length < 500) {
            // Check if selection is within chapter content
            const chapterContent = document.getElementById('chapterContent');
            if (chapterContent && chapterContent.contains(selection.anchorNode)) {
                this.lastSelectedText = text;
            }
        }
    }
    
    openFeedbackModal() {
        // Ensure modal is in clean state first
        this.feedbackModal.classList.remove('active');
        
        // Set current chapter
        if (this.currentChapter >= 0 && CHAPTERS_DATA[this.currentChapter]) {
            this.currentChapterDisplay.value = CHAPTERS_DATA[this.currentChapter].title;
        } else {
            this.currentChapterDisplay.value = '홈 화면';
        }
        
        // Pre-fill selected text if available
        if (this.lastSelectedText) {
            this.selectedText.value = this.lastSelectedText;
            this.lastSelectedText = null;
        }
        
        // Open modal with slight delay to ensure DOM is ready
        requestAnimationFrame(() => {
            this.feedbackModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    closeFeedbackModal() {
        this.feedbackModal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Reset form fields manually to ensure clean state
        this.feedbackType.value = '';
        this.selectedText.value = '';
        this.feedbackContent.value = '';
        
        // Reset priority to default (medium)
        const mediumPriority = document.querySelector('input[name="priority"][value="medium"]');
        if (mediumPriority) mediumPriority.checked = true;
        
        // Restore saved name
        const savedName = localStorage.getItem('betaReaderName');
        if (savedName) {
            this.readerName.value = savedName;
        } else {
            this.readerName.value = '';
        }
    }
    
    submitFeedback(e) {
        e.preventDefault();
        
        const feedback = {
            id: Date.now(),
            chapterId: this.currentChapter,
            chapterTitle: this.currentChapterDisplay.value,
            readerName: this.readerName.value.trim(),
            type: this.feedbackType.value,
            selectedText: this.selectedText.value.trim(),
            content: this.feedbackContent.value.trim(),
            priority: document.querySelector('input[name="priority"]:checked')?.value || 'medium',
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleDateString('ko-KR')
        };
        
        // Save reader name for future use
        localStorage.setItem('betaReaderName', feedback.readerName);
        
        // Add to feedbacks
        this.feedbacks.push(feedback);
        this.saveFeedbacks();
        this.updateFeedbackCount();
        
        // Close modal and show toast
        this.closeFeedbackModal();
        this.showToast('피드백이 저장되었습니다. 감사합니다! 🙏', 'success');
    }
    
    updateFeedbackCount() {
        this.feedbackCount.textContent = this.feedbacks.length;
    }
    
    openFeedbackListModal() {
        this.renderFeedbackList();
        this.renderFeedbackStats();
        this.feedbackListModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.closeSidebar();
    }
    
    closeFeedbackListModal() {
        this.feedbackListModal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    populateChapterFilter() {
        this.filterChapter.innerHTML = '<option value="all">모든 챕터</option>';
        CHAPTERS_DATA.forEach((chapter, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = chapter.title;
            this.filterChapter.appendChild(option);
        });
    }
    
    getFilteredFeedbacks() {
        let filtered = [...this.feedbacks];
        
        const chapterFilter = this.filterChapter.value;
        const typeFilter = this.filterType.value;
        
        if (chapterFilter !== 'all') {
            filtered = filtered.filter(f => f.chapterId === parseInt(chapterFilter));
        }
        
        if (typeFilter !== 'all') {
            filtered = filtered.filter(f => f.type === typeFilter);
        }
        
        // Sort by timestamp (newest first)
        filtered.sort((a, b) => b.id - a.id);
        
        return filtered;
    }
    
    getTypeLabel(type) {
        const labels = {
            typo: '🔤 오탈자',
            unclear: '❓ 이해 어려움',
            suggestion: '💡 제안',
            question: '🙋 질문',
            praise: '👍 좋았던 점',
            other: '📌 기타'
        };
        return labels[type] || type;
    }
    
    renderFeedbackList() {
        const filtered = this.getFilteredFeedbacks();
        
        if (filtered.length === 0) {
            this.feedbackList.innerHTML = `
                <div class="feedback-empty">
                    <div class="feedback-empty-icon">📭</div>
                    <p>아직 피드백이 없습니다.</p>
                </div>
            `;
            return;
        }
        
        this.feedbackList.innerHTML = filtered.map(feedback => `
            <div class="feedback-item priority-${feedback.priority}" data-id="${feedback.id}">
                <div class="feedback-item-header">
                    <div class="feedback-item-meta">
                        <span class="feedback-type-badge">${this.getTypeLabel(feedback.type)}</span>
                        <span class="feedback-chapter">${feedback.chapterTitle}</span>
                    </div>
                    <div>
                        <span class="feedback-reader">${feedback.readerName}</span>
                        <span class="feedback-date">${feedback.date}</span>
                        <button class="feedback-delete" title="삭제">🗑️</button>
                    </div>
                </div>
                ${feedback.selectedText ? `<div class="feedback-selected-text">"${feedback.selectedText}"</div>` : ''}
                <div class="feedback-content">${feedback.content}</div>
            </div>
        `).join('');
        
        // Bind delete buttons
        this.feedbackList.querySelectorAll('.feedback-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.feedback-item');
                const id = parseInt(item.dataset.id);
                this.deleteFeedback(id);
            });
        });
    }
    
    renderFeedbackStats() {
        const total = this.feedbacks.length;
        const byType = {};
        
        this.feedbacks.forEach(f => {
            byType[f.type] = (byType[f.type] || 0) + 1;
        });
        
        this.feedbackStats.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${total}</div>
                <div class="stat-label">전체</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${byType.typo || 0}</div>
                <div class="stat-label">오탈자</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${byType.unclear || 0}</div>
                <div class="stat-label">이해 어려움</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${byType.suggestion || 0}</div>
                <div class="stat-label">제안</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${byType.praise || 0}</div>
                <div class="stat-label">좋았던 점</div>
            </div>
        `;
    }
    
    deleteFeedback(id) {
        if (!confirm('이 피드백을 삭제하시겠습니까?')) return;
        
        this.feedbacks = this.feedbacks.filter(f => f.id !== id);
        this.saveFeedbacks();
        this.updateFeedbackCount();
        this.renderFeedbackList();
        this.renderFeedbackStats();
        this.showToast('피드백이 삭제되었습니다.', 'success');
    }
    
    exportFeedbackData() {
        if (this.feedbacks.length === 0) {
            this.showToast('내보낼 피드백이 없습니다.', 'error');
            return;
        }
        
        // Create CSV content
        const headers = ['날짜', '리더', '챕터', '유형', '중요도', '선택 텍스트', '피드백 내용'];
        const rows = this.feedbacks.map(f => [
            f.date,
            f.readerName,
            f.chapterTitle,
            this.getTypeLabel(f.type),
            f.priority,
            `"${(f.selectedText || '').replace(/"/g, '""')}"`,
            `"${f.content.replace(/"/g, '""')}"`
        ]);
        
        const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
        
        // Add BOM for Korean support in Excel
        const bom = '\uFEFF';
        const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `피드백_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showToast('피드백이 CSV 파일로 내보내졌습니다.', 'success');
    }
    
    exportFeedbackJSON() {
        if (this.feedbacks.length === 0) {
            this.showToast('내보낼 피드백이 없습니다.', 'error');
            return;
        }
        
        const exportData = {
            exportDate: new Date().toISOString(),
            bookTitle: '기억을 잇다, 교실을 읽다',
            version: '2.0',
            totalFeedbacks: this.feedbacks.length,
            feedbacks: this.feedbacks
        };
        
        const json = JSON.stringify(exportData, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `피드백_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showToast('피드백이 JSON 파일로 저장되었습니다.', 'success');
    }
    
    importFeedbackJSON(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                
                if (!data.feedbacks || !Array.isArray(data.feedbacks)) {
                    throw new Error('올바른 피드백 파일이 아닙니다.');
                }
                
                // 중복 제거를 위해 기존 ID 수집
                const existingIds = new Set(this.feedbacks.map(f => f.id));
                
                // 새 피드백만 추가
                let addedCount = 0;
                data.feedbacks.forEach(feedback => {
                    if (!existingIds.has(feedback.id)) {
                        this.feedbacks.push(feedback);
                        addedCount++;
                    }
                });
                
                this.saveFeedbacks();
                this.updateFeedbackCount();
                this.renderFeedbackList();
                this.renderFeedbackStats();
                
                if (addedCount > 0) {
                    this.showToast(`${addedCount}개의 피드백을 불러왔습니다.`, 'success');
                } else {
                    this.showToast('새로운 피드백이 없습니다. (중복 제외)', 'success');
                }
            } catch (error) {
                console.error('Import error:', error);
                this.showToast('파일을 읽는 중 오류가 발생했습니다.', 'error');
            }
        };
        
        reader.readAsText(file);
        
        // 같은 파일 다시 선택 가능하도록 초기화
        e.target.value = '';
    }
    
    showToast(message, type = '') {
        this.toast.textContent = message;
        this.toast.className = `toast show ${type}`;
        
        setTimeout(() => {
            this.toast.classList.remove('show');
        }, 3000);
    }
    
    // ===== Practice System =====
    initPracticeSystem() {
        // Practice buttons
        const openPracticeBtn = document.getElementById('openPractice');
        const startPracticeBtn = document.getElementById('startPractice');
        const backFromPractice = document.getElementById('backFromPractice');
        const backToCategories = document.getElementById('backToCategories');
        
        if (openPracticeBtn) {
            openPracticeBtn.addEventListener('click', () => {
                this.showPractice();
                this.closeSidebar();
            });
        }
        
        if (startPracticeBtn) {
            startPracticeBtn.addEventListener('click', () => this.showPractice());
        }
        
        if (backFromPractice) {
            backFromPractice.addEventListener('click', () => this.showHome());
        }
        
        if (backToCategories) {
            backToCategories.addEventListener('click', () => this.showPracticeCategories());
        }
        
        // Category cards
        if (this.practiceCategories) {
            this.practiceCategories.querySelectorAll('.practice-category-card').forEach(card => {
                card.addEventListener('click', () => {
                    const category = card.dataset.category;
                    this.openPracticeCategory(category);
                });
            });
        }
        
        // Update progress displays
        if (this.practiceCategories) {
            this.updatePracticeProgress();
        }
    }
    
    showPractice() {
        this.homeSection.style.display = 'none';
        this.chapterSection.style.display = 'none';
        this.searchSection.style.display = 'none';
        this.practiceSection.style.display = 'block';
        this.showPracticeCategories();
        window.scrollTo(0, 0);
    }
    
    showPracticeCategories() {
        this.practiceCategories.style.display = 'grid';
        this.practiceDetail.style.display = 'none';
        this.currentPracticeCategory = null;
        this.currentLesson = null;
        this.updatePracticeProgress();
    }
    
    updatePracticeProgress() {
        const beginnerProgress = document.getElementById('beginnerProgress');
        const scenariosProgress = document.getElementById('scenariosProgress');
        
        if (beginnerProgress && PRACTICE_DATA.beginner) {
            const completed = PracticeProgress.getCompletedCount('beginner');
            const total = PRACTICE_DATA.beginner.lessons.length;
            beginnerProgress.textContent = `${completed}/${total} 완료`;
        }
        
        if (scenariosProgress && PRACTICE_DATA.scenarios) {
            const completed = PracticeProgress.getCompletedCount('scenarios');
            const total = PRACTICE_DATA.scenarios.lessons.length;
            scenariosProgress.textContent = `${completed}/${total} 완료`;
        }
    }
    
    openPracticeCategory(category) {
        this.currentPracticeCategory = category;
        this.practiceCategories.style.display = 'none';
        this.practiceDetail.style.display = 'block';
        
        const data = PRACTICE_DATA[category];
        if (!data) return;
        
        let html = '';
        
        switch (category) {
            case 'beginner':
            case 'scenarios':
                html = this.renderLessonList(data);
                break;
            case 'complete':
                html = this.renderCompleteGuide(data);
                break;
            case 'templates':
                html = this.renderTemplates(data);
                break;
            case 'shortcuts':
                html = this.renderShortcuts(data);
                break;
            case 'sixweeks':
                html = this.renderSixWeeks(data);
                break;
        }
        
        this.practiceContent.innerHTML = html;
        this.bindPracticeContentEvents();
        window.scrollTo(0, 0);
    }
    
    renderLessonList(data) {
        const lessonsHtml = data.lessons.map(lesson => {
            const isCompleted = PracticeProgress.isComplete(lesson.id);
            return `
                <div class="lesson-card ${isCompleted ? 'completed' : ''}" data-lesson-id="${lesson.id}">
                    <div class="lesson-card-header">
                        <h4>${lesson.title}</h4>
                        <span class="lesson-status">${isCompleted ? '✅' : '📝'}</span>
                    </div>
                    <p>${lesson.mission || lesson.situation || ''}</p>
                </div>
            `;
        }).join('');
        
        return `
            <h3>${data.icon} ${data.title}</h3>
            <p style="color: var(--text-light); margin-bottom: 20px;">${data.description}</p>
            <div class="lesson-list">
                ${lessonsHtml}
            </div>
        `;
    }
    
    renderCompleteGuide(data) {
        const partsHtml = data.parts.map(part => {
            const chaptersHtml = part.chapters.map(ch => `
                <div class="guide-chapter-card" data-chapter-num="${ch.num}">
                    <div class="guide-chapter-header">
                        <div class="chapter-number">${ch.num}</div>
                        <div class="chapter-info">
                            <h5>${ch.title}</h5>
                            <p>${ch.desc}</p>
                        </div>
                        <span class="expand-icon">▼</span>
                    </div>
                    ${ch.example ? this.renderChapterExample(ch.example) : ''}
                </div>
            `).join('');
            
            return `
                <div class="guide-part">
                    <h4>${part.title}</h4>
                    ${part.subtitle ? `<p class="part-subtitle">${part.subtitle}</p>` : ''}
                    ${chaptersHtml}
                </div>
            `;
        }).join('');
        
        return `
            <h3>${data.icon} ${data.title}</h3>
            <p style="color: var(--text-light); margin-bottom: 30px;">${data.description}</p>
            <p style="color: var(--primary-color); font-size: 14px; margin-bottom: 20px;">💡 각 챕터를 클릭하면 실제 더미 데이터 사례를 볼 수 있습니다.</p>
            ${partsHtml}
        `;
    }
    
    renderChapterExample(example) {
        let html = `<div class="chapter-example" style="display: none;">`;
        
        // 제목
        html += `<div class="example-title">📝 ${example.title}</div>`;
        
        // 일반 content
        if (example.content) {
            html += `
                <div class="code-example">
                    <pre>${this.escapeHtml(example.content)}</pre>
                </div>
            `;
        }
        
        // Before/After 비교
        if (example.before && example.after) {
            html += `
                <div class="before-after">
                    <div class="before-box">
                        <h5>❌ Before (링크 없음)</h5>
                        <code>${this.escapeHtml(example.before)}</code>
                    </div>
                    <div class="after-box">
                        <h5>✅ After (링크 적용)</h5>
                        <code>${this.escapeHtml(example.after)}</code>
                    </div>
                </div>
            `;
        }
        
        // 여러 노트 (notes 배열)
        if (example.notes && example.notes.length > 0) {
            const notesHtml = example.notes.map(note => `
                <div class="example-note">
                    <div class="note-date">${note.title || note.date}</div>
                    <div class="code-example" style="margin-top: 8px;">
                        <pre>${this.escapeHtml(note.content)}</pre>
                    </div>
                </div>
            `).join('');
            html += `<div class="example-notes">${notesHtml}</div>`;
        }
        
        // 발견 (discovery)
        if (example.discovery) {
            html += `
                <div class="discovery-box">
                    <h5>🔍 발견!</h5>
                    <pre>${this.escapeHtml(example.discovery)}</pre>
                </div>
            `;
        }
        
        // 인사이트 (insight)
        if (example.insight) {
            html += `
                <div class="insight-box">
                    <h5>💡 인사이트</h5>
                    <p>${example.insight.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        }
        
        // 학생 카드 (studentCard)
        if (example.studentCard) {
            html += `
                <div class="example-title" style="margin-top: 20px;">📝 ${example.studentCard.title}</div>
                <div class="code-example">
                    <pre>${this.escapeHtml(example.studentCard.content)}</pre>
                </div>
            `;
        }
        
        // 민원 대응 (situation, search, response)
        if (example.situation) {
            html += `
                <div class="insight-box">
                    <h5>📋 상황</h5>
                    <p>${example.situation.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        }
        if (example.search) {
            html += `
                <div class="code-example">
                    <pre>${this.escapeHtml(example.search)}</pre>
                </div>
            `;
        }
        if (example.response) {
            html += `
                <div class="discovery-box">
                    <h5>💬 대응</h5>
                    <pre>${this.escapeHtml(example.response)}</pre>
                </div>
            `;
        }
        
        // 생기부 기록 (records, result)
        if (example.records && example.records.length > 0) {
            const recordsHtml = example.records.map(r => `<li>${r}</li>`).join('');
            html += `
                <div class="example-records">
                    <h5>📋 1년간 기록</h5>
                    <ul>${recordsHtml}</ul>
                </div>
            `;
        }
        if (example.result) {
            html += `
                <div class="discovery-box">
                    <h5>📝 완성된 생기부</h5>
                    <pre>${this.escapeHtml(example.result)}</pre>
                </div>
            `;
        }
        
        // 타임라인 (timeline)
        if (example.timeline && example.timeline.length > 0) {
            if (example.keyword) {
                html += `<div class="code-label">검색 키워드: ${example.keyword}</div>`;
            }
            const timelineHtml = example.timeline.map(t => `
                <div class="timeline-item">
                    <span class="timeline-month">${t.month}</span>
                    <span class="timeline-content">${t.content}</span>
                </div>
            `).join('');
            html += `<div class="example-timeline">${timelineHtml}</div>`;
            
            if (example.insight) {
                html += `
                    <div class="insight-box">
                        <h5>💡 결과</h5>
                        <p>${example.insight.replace(/\n/g, '<br>')}</p>
                    </div>
                `;
            }
        }
        
        html += `</div>`;
        return html;
    }
    
    renderTemplates(data) {
        const templatesHtml = data.items.map(template => `
            <div class="template-card">
                <h4>
                    ${template.title}
                    <button class="copy-btn" data-template-id="${template.id}">📋 복사</button>
                </h4>
                <div class="code-example">
                    <pre>${this.escapeHtml(template.content)}</pre>
                </div>
            </div>
        `).join('');
        
        return `
            <h3>${data.icon} ${data.title}</h3>
            <p style="color: var(--text-light); margin-bottom: 20px;">${data.description}</p>
            ${templatesHtml}
        `;
    }
    
    renderShortcuts(data) {
        const rowsHtml = data.items.map(item => `
            <tr>
                <td><kbd>${item.key}</kbd></td>
                <td>${item.desc}</td>
                <td>${item.use}</td>
            </tr>
        `).join('');
        
        return `
            <h3>${data.icon} ${data.title}</h3>
            <p style="color: var(--text-light); margin-bottom: 20px;">${data.description}</p>
            <table class="shortcuts-table">
                <thead>
                    <tr>
                        <th>단축키</th>
                        <th>기능</th>
                        <th>사용 상황</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;
    }
    
    renderSixWeeks(data) {
        const weeksHtml = data.weeks.map(week => {
            const topicsHtml = week.topics.map(t => `<li>${t}</li>`).join('');
            return `
                <div class="week-card-practice">
                    <div class="week-badge">Week ${week.num}</div>
                    <h4>${week.title}</h4>
                    <p class="week-subtitle">${week.subtitle}</p>
                    <ul class="week-topics">${topicsHtml}</ul>
                    <a href="${week.link}" target="_blank" class="btn-week-start">시작하기 →</a>
                </div>
            `;
        }).join('');
        
        return `
            <h3>${data.icon} ${data.title}</h3>
            <p style="color: var(--text-light); margin-bottom: 30px;">${data.description}</p>
            <div class="weeks-grid">
                ${weeksHtml}
            </div>
        `;
    }
    
    bindPracticeContentEvents() {
        // Lesson cards
        this.practiceContent.querySelectorAll('.lesson-card').forEach(card => {
            card.addEventListener('click', () => {
                const lessonId = card.dataset.lessonId;
                this.openLesson(lessonId);
            });
        });
        
        // Copy buttons
        this.practiceContent.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const templateId = btn.dataset.templateId;
                this.copyTemplate(templateId, btn);
            });
        });
        
        // Guide chapter cards (expandable)
        this.practiceContent.querySelectorAll('.guide-chapter-card').forEach(card => {
            const header = card.querySelector('.guide-chapter-header');
            const example = card.querySelector('.chapter-example');
            const icon = card.querySelector('.expand-icon');
            
            if (header && example) {
                header.addEventListener('click', () => {
                    const isOpen = example.style.display !== 'none';
                    example.style.display = isOpen ? 'none' : 'block';
                    if (icon) {
                        icon.textContent = isOpen ? '▼' : '▲';
                    }
                    card.classList.toggle('expanded', !isOpen);
                });
            }
        });
    }
    
    openLesson(lessonId) {
        const category = this.currentPracticeCategory;
        const data = PRACTICE_DATA[category];
        if (!data || !data.lessons) return;
        
        const lesson = data.lessons.find(l => l.id === lessonId);
        if (!lesson) return;
        
        this.currentLesson = lesson;
        
        let html = `
            <button class="btn-back" id="backToLessonList">← 목록으로</button>
            <div class="lesson-detail">
                <h3>${lesson.title}</h3>
        `;
        
        // Mission box
        if (lesson.mission) {
            html += `
                <div class="mission-box">
                    <h4>오늘의 미션</h4>
                    <p>${lesson.mission}</p>
                </div>
            `;
        }
        
        // Situation (for scenarios)
        if (lesson.situation) {
            html += `
                <div class="insight-box">
                    <h5>📋 상황</h5>
                    <p>${lesson.situation}</p>
                </div>
            `;
        }
        
        // Steps
        if (lesson.steps && lesson.steps.length > 0) {
            const stepsHtml = lesson.steps.map((step, idx) => `
                <div class="step-item" data-step-idx="${idx}">
                    <div class="step-checkbox"></div>
                    <span class="step-text">${step.text}</span>
                </div>
            `).join('');
            
            html += `
                <div class="steps-section">
                    <h4>📝 따라하기</h4>
                    ${stepsHtml}
                </div>
            `;
        }
        
        // Template
        if (lesson.template) {
            html += `
                <div class="code-label">📋 템플릿</div>
                <div class="code-example">
                    <pre>${this.escapeHtml(lesson.template)}</pre>
                </div>
            `;
        }
        
        // Example
        if (lesson.example) {
            html += `
                <div class="code-label">✍️ 예시</div>
                <div class="code-example">
                    <pre>${this.escapeHtml(lesson.example)}</pre>
                </div>
            `;
        }
        
        // Before/After
        if (lesson.before && lesson.after) {
            html += `
                <div class="before-after">
                    <div class="before-box">
                        <h5>❌ Before</h5>
                        <code>${this.escapeHtml(lesson.before)}</code>
                    </div>
                    <div class="after-box">
                        <h5>✅ After</h5>
                        <code>${this.escapeHtml(lesson.after)}</code>
                    </div>
                </div>
            `;
        }
        
        // Examples (multiple)
        if (lesson.examples && lesson.examples.length > 0) {
            const examplesHtml = lesson.examples.map(ex => `
                <div style="margin-bottom: 10px;">
                    <div class="code-label">${ex.date}</div>
                    <div class="code-example" style="margin-top: 5px;">
                        <pre>${this.escapeHtml(ex.content)}</pre>
                    </div>
                </div>
            `).join('');
            
            html += `
                <div class="steps-section">
                    <h4>📝 예시 기록</h4>
                    ${examplesHtml}
                </div>
            `;
        }
        
        // Discovery
        if (lesson.discovery) {
            html += `
                <div class="discovery-box">
                    <h5>🔍 발견!</h5>
                    <pre>${lesson.discovery}</pre>
                </div>
            `;
        }
        
        // Insight
        if (lesson.insight) {
            html += `
                <div class="insight-box">
                    <h5>💡 교육적 의미</h5>
                    <p>${lesson.insight}</p>
                </div>
            `;
        }
        
        // Result (for scenarios)
        if (lesson.result) {
            html += `
                <div class="discovery-box">
                    <h5>📝 완성된 문장</h5>
                    <pre>${lesson.result}</pre>
                </div>
            `;
        }
        
        // Tip
        if (lesson.tip) {
            html += `
                <div class="insight-box">
                    <h5>💡 팁</h5>
                    <p>${lesson.tip}</p>
                </div>
            `;
        }
        
        // Checkpoints
        if (lesson.checkpoints && lesson.checkpoints.length > 0) {
            const checkpointsHtml = lesson.checkpoints.map(cp => `
                <div class="checkpoint-item">
                    <span class="checkpoint-icon">☐</span>
                    <span>${cp}</span>
                </div>
            `).join('');
            
            html += `
                <div class="checkpoints-section">
                    <h4>✅ 성공 체크</h4>
                    ${checkpointsHtml}
                </div>
            `;
        }
        
        // Complete button
        const isCompleted = PracticeProgress.isComplete(lessonId);
        html += `
            <button class="complete-lesson-btn ${isCompleted ? 'completed' : ''}" data-lesson-id="${lessonId}">
                ${isCompleted ? '✅ 완료됨' : '🎉 이 실습 완료하기'}
            </button>
        `;
        
        html += '</div>';
        
        this.practiceContent.innerHTML = html;
        
        // Bind events
        const backBtn = document.getElementById('backToLessonList');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.openPracticeCategory(this.currentPracticeCategory);
            });
        }
        
        // Step checkboxes
        this.practiceContent.querySelectorAll('.step-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', () => {
                checkbox.classList.toggle('checked');
                checkbox.closest('.step-item').classList.toggle('completed');
            });
        });
        
        // Complete button
        const completeBtn = this.practiceContent.querySelector('.complete-lesson-btn');
        if (completeBtn && !isCompleted) {
            completeBtn.addEventListener('click', () => {
                PracticeProgress.markComplete(lessonId);
                completeBtn.classList.add('completed');
                completeBtn.textContent = '✅ 완료됨';
                this.showToast('실습을 완료했습니다! 🎉', 'success');
                this.updatePracticeProgress();
            });
        }
        
        window.scrollTo(0, 0);
    }
    
    copyTemplate(templateId, btn) {
        const data = PRACTICE_DATA.templates;
        if (!data) return;
        
        const template = data.items.find(t => t.id === templateId);
        if (!template) return;
        
        navigator.clipboard.writeText(template.content).then(() => {
            btn.textContent = '✅ 복사됨!';
            btn.classList.add('copied');
            
            setTimeout(() => {
                btn.textContent = '📋 복사';
                btn.classList.remove('copied');
            }, 2000);
        }).catch(() => {
            this.showToast('복사에 실패했습니다.', 'error');
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new LearningPlatform();
});
