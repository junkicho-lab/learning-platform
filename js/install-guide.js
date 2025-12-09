/**
 * Install Guide - Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const chapters = document.querySelectorAll('.chapter-content');
    
    // Early return if elements don't exist (not on install-guide page)
    if (!tabBtns.length || !chapters.length) return;
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update tab buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update chapter content
            chapters.forEach(chapter => {
                if (chapter.id === targetTab) {
                    chapter.classList.remove('hidden');
                } else {
                    chapter.classList.add('hidden');
                }
            });
            
            // Scroll to top immediately
            window.scrollTo(0, 0);
        });
    });
    
    // OS Tabs (Windows/Mac)
    const osTabs = document.querySelectorAll('.os-tab');
    osTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const os = tab.dataset.os;
            const parent = tab.closest('.content-section');
            
            // Update OS tabs
            parent.querySelectorAll('.os-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update OS content
            parent.querySelectorAll('.os-content').forEach(content => {
                if (content.id === `${os}-content`) {
                    content.classList.remove('hidden');
                } else {
                    content.classList.add('hidden');
                }
            });
        });
    });
    
    // Chapter Navigation Buttons
    const navBtns = document.querySelectorAll('.nav-btn[data-next], .nav-btn[data-prev]');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const nextChapter = btn.dataset.next;
            const prevChapter = btn.dataset.prev;
            const targetChapter = nextChapter || prevChapter;
            
            if (targetChapter) {
                // Update tab buttons
                tabBtns.forEach(b => b.classList.remove('active'));
                const targetTab = document.querySelector(`.tab-btn[data-tab="${targetChapter}"]`);
                if (targetTab) {
                    targetTab.classList.add('active');
                }
                
                // Update chapter content
                chapters.forEach(chapter => {
                    if (chapter.id === targetChapter) {
                        chapter.classList.remove('hidden');
                    } else {
                        chapter.classList.add('hidden');
                    }
                });
                
                // Scroll to top immediately
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Checklist persistence (localStorage)
    const checkboxes = document.querySelectorAll('.checklist input[type="checkbox"]');
    const storageKey = 'install-guide-progress';
    
    // Load saved progress
    const savedProgress = JSON.parse(localStorage.getItem(storageKey) || '{}');
    checkboxes.forEach((checkbox, index) => {
        const key = `checkbox-${index}`;
        if (savedProgress[key]) {
            checkbox.checked = true;
        }
        
        // Save on change
        checkbox.addEventListener('change', () => {
            savedProgress[key] = checkbox.checked;
            localStorage.setItem(storageKey, JSON.stringify(savedProgress));
        });
    });
    
    // Image error handling
    const images = document.querySelectorAll('.image-placeholder img');
    images.forEach(img => {
        img.addEventListener('error', () => {
            img.style.display = 'none';
            const placeholder = img.closest('.image-placeholder');
            if (placeholder) {
                placeholder.innerHTML = `
                    <div style="padding: 2rem; color: #64748b;">
                        <p>📷 이미지를 불러올 수 없습니다</p>
                        <p style="font-size: 0.85rem;">${img.alt || '스크린샷'}</p>
                    </div>
                `;
            }
        });
    });

    // Image Lightbox (클릭 시 확대/축소)
    createImageLightbox();
    
    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Progress tracking
    function updateProgress() {
        const totalCheckboxes = checkboxes.length;
        const checkedCount = document.querySelectorAll('.checklist input[type="checkbox"]:checked').length;
        const progress = totalCheckboxes > 0 ? Math.round((checkedCount / totalCheckboxes) * 100) : 0;
        
        // Could display progress somewhere if needed
        console.log(`Progress: ${progress}%`);
    }
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateProgress);
    });
    
    // Initial progress check
    updateProgress();
});

/**
 * Image Lightbox - 이미지 클릭 시 확대/축소
 */
function createImageLightbox() {
    // 라이트박스 오버레이 생성
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = `
        <div class="lightbox-content">
            <img src="" alt="" class="lightbox-image">
            <div class="lightbox-caption"></div>
            <button class="lightbox-close" aria-label="닫기">✕</button>
            <div class="lightbox-hint">클릭하거나 ESC를 눌러 닫기</div>
        </div>
    `;
    document.body.appendChild(overlay);

    const lightboxImage = overlay.querySelector('.lightbox-image');
    const lightboxCaption = overlay.querySelector('.lightbox-caption');
    const closeBtn = overlay.querySelector('.lightbox-close');

    // 스타일 추가
    const style = document.createElement('style');
    style.textContent = `
        .lightbox-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
            cursor: zoom-out;
        }

        .lightbox-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .lightbox-content {
            position: relative;
            max-width: 95vw;
            max-height: 95vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .lightbox-image {
            max-width: 95vw;
            max-height: 85vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }

        .lightbox-overlay.active .lightbox-image {
            transform: scale(1);
        }

        .lightbox-caption {
            color: white;
            margin-top: 1rem;
            font-size: 0.95rem;
            text-align: center;
            max-width: 600px;
        }

        .lightbox-close {
            position: absolute;
            top: -40px;
            right: 0;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 1.2rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        .lightbox-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .lightbox-hint {
            position: absolute;
            bottom: -30px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.8rem;
        }

        /* 이미지에 클릭 가능 표시 */
        .image-placeholder img {
            cursor: zoom-in;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .image-placeholder img:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
    `;
    document.head.appendChild(style);

    // 모든 이미지에 클릭 이벤트 추가
    const allImages = document.querySelectorAll('.image-placeholder img');
    allImages.forEach(img => {
        img.addEventListener('click', () => {
            lightboxImage.src = img.src;
            lightboxCaption.textContent = img.alt || '';
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    // 닫기 기능
    function closeLightbox() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    overlay.addEventListener('click', closeLightbox);
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeLightbox();
    });

    // ESC 키로 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            closeLightbox();
        }
    });

    // 이미지 클릭 시 닫히지 않도록
    lightboxImage.addEventListener('click', (e) => {
        e.stopPropagation();
        closeLightbox();
    });
}
