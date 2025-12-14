/**
 * TTS (Text-to-Speech) 기능
 * 시력이 약한 사용자를 위한 오디오북 기능
 */

class TTSController {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.isPlaying = false;
        this.isPaused = false;
        this.currentText = '';
        this.voices = [];
        
        // DOM 요소
        this.playBtn = document.getElementById('ttsPlay');
        this.pauseBtn = document.getElementById('ttsPause');
        this.stopBtn = document.getElementById('ttsStop');
        this.speedSelect = document.getElementById('ttsSpeed');
        
        this.init();
    }
    
    init() {
        // 음성 목록 로드
        this.loadVoices();
        this.synth.onvoiceschanged = () => this.loadVoices();
        
        // 이벤트 리스너
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.play());
        }
        if (this.pauseBtn) {
            this.pauseBtn.addEventListener('click', () => this.pause());
        }
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stop());
        }
        if (this.speedSelect) {
            this.speedSelect.addEventListener('change', () => {
                if (this.isPlaying) {
                    this.stop();
                    this.play();
                }
            });
        }
    }
    
    loadVoices() {
        this.voices = this.synth.getVoices();
        // 한국어 음성 찾기
        this.koreanVoice = this.voices.find(voice => 
            voice.lang.includes('ko') || voice.lang.includes('KR')
        );
    }
    
    getTextFromContent() {
        const content = document.getElementById('chapterContent');
        if (!content) return '';
        
        // HTML에서 텍스트만 추출 (코드 블록 제외)
        const clone = content.cloneNode(true);
        
        // 코드 블록 제거
        clone.querySelectorAll('pre, code').forEach(el => {
            el.textContent = '(코드 생략)';
        });
        
        // 테이블 간소화
        clone.querySelectorAll('table').forEach(el => {
            el.textContent = '(표 내용 생략)';
        });
        
        let text = clone.textContent || clone.innerText;
        
        // 텍스트 정리
        text = text
            .replace(/\s+/g, ' ')  // 연속 공백 제거
            .replace(/\n+/g, '. ') // 줄바꿈을 마침표로
            .replace(/\.+/g, '.') // 연속 마침표 제거
            .trim();
        
        return text;
    }
    
    play() {
        if (this.isPaused && this.utterance) {
            this.synth.resume();
            this.isPaused = false;
            this.updateButtons('playing');
            return;
        }
        
        this.stop();
        
        this.currentText = this.getTextFromContent();
        if (!this.currentText) {
            alert('읽을 내용이 없습니다.');
            return;
        }
        
        // 텍스트가 너무 길면 분할 (브라우저 제한)
        const maxLength = 5000;
        const chunks = this.splitText(this.currentText, maxLength);
        
        this.speakChunks(chunks, 0);
    }
    
    splitText(text, maxLength) {
        const chunks = [];
        let start = 0;
        
        while (start < text.length) {
            let end = start + maxLength;
            
            if (end < text.length) {
                // 문장 끝에서 자르기
                const lastPeriod = text.lastIndexOf('.', end);
                const lastQuestion = text.lastIndexOf('?', end);
                const lastExclaim = text.lastIndexOf('!', end);
                const breakPoint = Math.max(lastPeriod, lastQuestion, lastExclaim);
                
                if (breakPoint > start) {
                    end = breakPoint + 1;
                }
            }
            
            chunks.push(text.substring(start, end).trim());
            start = end;
        }
        
        return chunks;
    }
    
    speakChunks(chunks, index) {
        if (index >= chunks.length) {
            this.stop();
            return;
        }
        
        this.utterance = new SpeechSynthesisUtterance(chunks[index]);
        
        // 설정
        this.utterance.lang = 'ko-KR';
        this.utterance.rate = parseFloat(this.speedSelect?.value || 1);
        this.utterance.pitch = 1;
        this.utterance.volume = 1;
        
        // 한국어 음성 사용
        if (this.koreanVoice) {
            this.utterance.voice = this.koreanVoice;
        }
        
        // 이벤트
        this.utterance.onstart = () => {
            this.isPlaying = true;
            this.updateButtons('playing');
        };
        
        this.utterance.onend = () => {
            // 다음 청크 재생
            this.speakChunks(chunks, index + 1);
        };
        
        this.utterance.onerror = (e) => {
            console.error('TTS Error:', e);
            this.stop();
        };
        
        this.synth.speak(this.utterance);
    }
    
    pause() {
        if (this.isPlaying && !this.isPaused) {
            this.synth.pause();
            this.isPaused = true;
            this.updateButtons('paused');
        }
    }
    
    stop() {
        this.synth.cancel();
        this.isPlaying = false;
        this.isPaused = false;
        this.utterance = null;
        this.updateButtons('stopped');
    }
    
    updateButtons(state) {
        if (!this.playBtn || !this.pauseBtn || !this.stopBtn) return;
        
        switch (state) {
            case 'playing':
                this.playBtn.style.display = 'none';
                this.pauseBtn.style.display = 'inline-block';
                this.stopBtn.style.display = 'inline-block';
                break;
            case 'paused':
                this.playBtn.style.display = 'inline-block';
                this.playBtn.textContent = '▶️ 계속';
                this.pauseBtn.style.display = 'none';
                this.stopBtn.style.display = 'inline-block';
                break;
            case 'stopped':
            default:
                this.playBtn.style.display = 'inline-block';
                this.playBtn.textContent = '🔊 읽어주기';
                this.pauseBtn.style.display = 'none';
                this.stopBtn.style.display = 'none';
                break;
        }
    }
}

// 페이지 로드 시 초기화
let ttsController;
document.addEventListener('DOMContentLoaded', () => {
    ttsController = new TTSController();
});

// 페이지 이동 시 TTS 정지
window.addEventListener('beforeunload', () => {
    if (ttsController) {
        ttsController.stop();
    }
});
