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
