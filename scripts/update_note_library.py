#!/usr/bin/env python3
"""
예제노트들 폴더의 파일들을 읽어서 note-library.js를 업데이트하는 스크립트
"""

import os
import json
import re
import unicodedata

# 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_NOTES_DIR = os.path.join(SCRIPT_DIR, "예제노트들")
OUTPUT_JS = os.path.join(SCRIPT_DIR, "js", "note-library.js")

def escape_js_string(s):
    """JavaScript 문자열로 이스케이프"""
    s = s.replace('\\', '\\\\')
    s = s.replace('`', '\\`')
    s = s.replace('${', '\\${')
    return s

def categorize_file(filename):
    """파일을 카테고리별로 분류"""
    name = filename.replace('.md', '')
    # macOS NFD 유니코드 정규화 처리
    name = unicodedata.normalize('NFC', name)
    
    # 데일리노트 (날짜 형식)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', name):
        return 'daily', name
    
    # 학생 노트 (실제 파일명 기준)
    student_names = ['강도현', '김민준', '류승민', '박서준', '신시우', '이준우', '정수아', '조민서', '최예진', '황지아']
    if name in student_names:
        return 'student', name
    
    # 키워드/상황 노트 (실제 파일명 기준)
    keyword_files = ['월요병', '화장실빌런', '화장실빌런의비밀', '교우관계', '가정환경', '비계설정', '모둠활동', 
                     '비오는날', '4교시', '금요들뜸', '급식버프', '급식실', '수업방해', 
                     '수업이탈', '수업실패', '시험후유증', '행사후유증', '방송테러', '지각',
                     '스마트폰', '기자재고장', '안전사고', '과제제출', '발표', '형성평가',
                     '아이스브레이킹', '게임형학습', '직소모형', '라포형성', '갈등조정',
                     '방어기제', '분노조절', '자기효능감', '리더십', '관심필요학생',
                     '보건실투어', '영어회피', '학급경영', '마니또']
    if name in keyword_files:
        return 'keyword', name
    
    # 매뉴얼/업무 노트 (실제 파일명 기준)
    manual_files = ['체육대회', '체육대회 매뉴얼', '수학여행', '현장체험학습', '학부모상담', 
                    '학부모 민원 대응법', '학급경영 매뉴얼', '가정통신문 상용구', 
                    '신규교사를 위한 Q&A', '행정실']
    if name in manual_files:
        return 'manual', name
    
    # 수업 노트 (실제 파일명 기준)
    class_files = ['피타고라스 정리']
    if name in class_files:
        return 'class', name
    
    # 핵심 파일 (실제 파일명 기준)
    core_files = ['우리반 학생 명단', '나의 첫 에세이 글감']
    if name in core_files:
        return 'core', name
    
    return 'other', name

def read_all_files():
    """예제노트들 폴더의 모든 파일 읽기"""
    files = {}
    
    for filename in os.listdir(EXAMPLE_NOTES_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(EXAMPLE_NOTES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            category, name = categorize_file(filename)
            files[filename] = {
                'category': category,
                'name': name,
                'content': content
            }
    
    return files

def generate_js_templates(files):
    """JavaScript 템플릿 객체 생성"""
    templates = []
    
    # 카테고리별 정렬
    daily_notes = []
    student_notes = []
    keyword_notes = []
    manual_notes = []
    class_notes = []
    core_notes = []
    other_notes = []
    
    for filename, data in files.items():
        category = data['category']
        name = data['name']
        content = escape_js_string(data['content'])
        
        entry = {
            'filename': filename,
            'name': name,
            'content': content
        }
        
        if category == 'daily':
            daily_notes.append(entry)
        elif category == 'student':
            student_notes.append(entry)
        elif category == 'keyword':
            keyword_notes.append(entry)
        elif category == 'manual':
            manual_notes.append(entry)
        elif category == 'class':
            class_notes.append(entry)
        elif category == 'core':
            core_notes.append(entry)
        else:
            other_notes.append(entry)
    
    # 정렬
    daily_notes.sort(key=lambda x: x['name'])
    student_notes.sort(key=lambda x: x['name'])
    keyword_notes.sort(key=lambda x: x['name'])
    
    return {
        'daily': daily_notes,
        'student': student_notes,
        'keyword': keyword_notes,
        'manual': manual_notes,
        'class': class_notes,
        'core': core_notes,
        'other': other_notes
    }

def generate_js_file(categorized):
    """JavaScript 파일 생성"""
    
    js_content = '''/**
 * Note Library - JavaScript
 * 예제노트들 폴더에서 자동 생성됨
 */

document.addEventListener('DOMContentLoaded', () => {
    // Template contents - 실제 파일 내용
    const templates = {
'''
    
    # 핵심 템플릿 (기존 유지)
    js_content += '''        // 00_템플릿
        'daily-template': {
            filename: '데일리노트_템플릿.md',
            content: `# {{date:YYYY-MM-DD}} ({{date:ddd}})

## 오늘의 할 일
- [ ] 
- [ ] 
- [ ] 

---

## 수업 기록
- 1교시:
- 2교시:
- 3교시:
- 4교시:
- 5교시:
- 6교시:

---

## 오늘의 회고 (ORID)

### 1. 무슨 일이 있었나? (사실)
- 

### 2. 어떤 기분이 들었나? (감정)
- 

### 3. 왜 그랬을까? (해석)
- 

### 4. 그래서 어떻게 할까? (계획)
- [ ] 

---

## 🎋 대나무 숲 (오늘의 속마음)
*여기에 털어버리고 퇴근합니다*
- 

---

## 메모장
- 
`
        },
        'student-card-template': {
            filename: '학생카드_템플릿.md',
            content: `# (학생이름) (번호)

## 📌 기본 정보
- **성별:** 
- **특이사항:** 
- **관심사:** 

---

## 📊 정량 데이터
- **발표 횟수:** 
- **과제 제출율:** 
- **지각/결석:** 

---

## 🔗 관련 기록
*데일리 노트에서 이 학생을 [[링크]]로 언급하면 백링크에 자동으로 모입니다*

---

## 📝 상담 메모
### 날짜:
- 상담 내용:
- 후속 조치:

---

## 📋 생기부 초안
*12월에 복사해서 쓸 문장들*

### 행동특성 및 종합의견


### 세부능력특기사항

`
        },
'''
    
    # 핵심 파일 (우리반 학생 명단)
    for entry in categorized['core']:
        if entry['name'] == '우리반 학생 명단':
            js_content += f'''        'student-list': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    # 데일리노트
    for entry in categorized['daily']:
        key = f"daily-{entry['name'].replace('-', '')}"
        js_content += f'''        '{key}': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    # 학생 노트
    for entry in categorized['student']:
        key = f"student-{entry['name']}"
        js_content += f'''        '{key}': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    # 키워드 노트
    for entry in categorized['keyword']:
        key = f"keyword-{entry['name']}"
        js_content += f'''        '{key}': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    # 매뉴얼/업무 노트
    for entry in categorized['manual']:
        key = f"manual-{entry['name'].replace(' ', '-')}"
        js_content += f'''        '{key}': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    # 수업 노트
    for entry in categorized['class']:
        key = f"class-{entry['name'].replace(' ', '-')}"
        js_content += f'''        '{key}': {{
            filename: '{entry["filename"]}',
            content: `{entry["content"]}`
        }},
'''
    
    js_content += '''    };

    // Download button click handlers
    document.querySelectorAll('.download-btn, .file-download-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fileKey = e.target.closest('[data-file]')?.dataset.file;
            if (fileKey && templates[fileKey]) {
                downloadFile(templates[fileKey].filename, templates[fileKey].content);
            }
        });
    });

    // Download all buttons
    document.querySelectorAll('.download-all-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const category = e.target.dataset.category;
            downloadCategory(category);
        });
    });

    function downloadFile(filename, content) {
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function downloadCategory(category) {
        const prefix = category === 'daily' ? 'daily-' : 
                       category === 'students' ? 'student-' : 
                       category === 'keywords' ? 'keyword-' : '';
        
        Object.keys(templates).forEach(key => {
            if (key.startsWith(prefix)) {
                setTimeout(() => {
                    downloadFile(templates[key].filename, templates[key].content);
                }, 100);
            }
        });
    }
});
'''
    
    return js_content

def main():
    print("📂 예제노트들 폴더 읽는 중...")
    files = read_all_files()
    print(f"✓ {len(files)}개 파일 발견")
    
    print("\n📊 파일 분류 중...")
    categorized = generate_js_templates(files)
    print(f"  - 데일리노트: {len(categorized['daily'])}개")
    print(f"  - 학생 노트: {len(categorized['student'])}개")
    print(f"  - 키워드 노트: {len(categorized['keyword'])}개")
    print(f"  - 매뉴얼/업무: {len(categorized['manual'])}개")
    print(f"  - 수업 노트: {len(categorized['class'])}개")
    print(f"  - 핵심 파일: {len(categorized['core'])}개")
    print(f"  - 기타: {len(categorized['other'])}개")
    
    print("\n📝 JavaScript 파일 생성 중...")
    js_content = generate_js_file(categorized)
    
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✓ {OUTPUT_JS} 생성 완료!")
    print(f"\n📊 총 {len(files)}개 파일이 노트자료실에 반영되었습니다.")

if __name__ == "__main__":
    main()
