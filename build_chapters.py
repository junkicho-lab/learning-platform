#!/usr/bin/env python3
"""
XHTML 파일들을 파싱하여 JavaScript 챕터 데이터로 변환
"""

import os
import re
from html.parser import HTMLParser

# 챕터 정보 (실제 xhtml 파일의 제목과 일치)
CHAPTERS = [
    ("chap_00.xhtml", "프롤로그", "왜 우리는 매일 까먹고, 매년 똑같이 힘들까?"),
    ("chap_01.xhtml", "제1장. 작심삼일 없는 '3분 기록' 세팅", "데일리 노트와 ORID 템플릿으로 시작하기"),
    ("chap_02.xhtml", "제2장. 마법의 대괄호, 링크의 발견", "[[]] 링크로 정보를 연결하는 방법"),
    ("chap_03.xhtml", "제3장. 기록의 골든타임", "언제 쓸 것인가? 최적의 기록 타이밍"),
    ("chap_04.xhtml", "제4장. 시간 여행자의 클릭", "링크와 백링크로 과거 기록 탐색"),
    ("chap_05.xhtml", "제5장. 꼬리에 꼬리를 무는 단서 찾기 (인물편)", "학생별 기록 추적과 패턴 발견"),
    ("chap_06.xhtml", "제6장. 교사의 데자뷰는 데이터가 된다 (환경편)", "반복되는 상황의 패턴 분석"),
    ("chap_07.xhtml", "제7장. 살아있는 생활기록부", "학생 프로파일링과 MOC 구축"),
    ("chap_08.xhtml", "제8장. 나만의 수업 백과사전 구축하기", "수업 자료와 노하우 체계화"),
    ("chap_09.xhtml", "제9장. 나만의 행사 업무 매뉴얼 구축하기", "학교 행사와 업무 템플릿화"),
    ("chap_10.xhtml", "제10장. 내 교실의 우주를 보다", "그래프 뷰로 지식 네트워크 시각화"),
    ("chap_11.xhtml", "제11장. 위기의 순간, 나를 지키는 방패", "민원 대응과 기록의 힘"),
    ("chap_12.xhtml", "제12장. 학기 말의 구세주", "NEIS 업무와 생기부 작성 효율화"),
    ("chap_13.xhtml", "제13장. 기록하는 노동자에서 성장하는 교육자로", "기록을 통한 교사 성장"),
    ("chap_14.xhtml", "에필로그", "기록의 여정을 마치며"),
    ("chap_15.xhtml", "부록", "박 선생님을 위한 '떠먹여 주는' 자료실"),
]

def extract_body_content(xhtml_path):
    """XHTML 파일에서 body 내용 추출"""
    with open(xhtml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # body 태그 내용 추출
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    if body_match:
        body_content = body_match.group(1)
        # container div 내용 추출
        container_match = re.search(r'<div class="container">(.*?)</div>\s*$', body_content, re.DOTALL)
        if container_match:
            return container_match.group(1).strip()
        return body_content.strip()
    return ""

def escape_js_string(s):
    """JavaScript 문자열 이스케이프"""
    s = s.replace('\\', '\\\\')
    s = s.replace('`', '\\`')
    s = s.replace('${', '\\${')
    return s

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    chapters_data = []
    
    for i, (filename, title, description) in enumerate(CHAPTERS):
        xhtml_path = os.path.join(parent_dir, filename)
        
        if os.path.exists(xhtml_path):
            content = extract_body_content(xhtml_path)
            content = escape_js_string(content)
            
            chapters_data.append({
                'id': i,
                'filename': filename,
                'title': title,
                'description': description,
                'content': content
            })
            print(f"✓ 처리 완료: {filename} ({title})")
        else:
            print(f"⚠ 파일 없음: {filename}")
    
    # JavaScript 파일 생성
    js_output = "// 자동 생성된 챕터 데이터\n"
    js_output += "const CHAPTERS_DATA = [\n"
    
    for ch in chapters_data:
        js_output += f"""    {{
        id: {ch['id']},
        title: `{ch['title']}`,
        description: `{ch['description']}`,
        content: `{ch['content']}`
    }},
"""
    
    js_output += "];\n"
    
    # 파일 저장
    js_path = os.path.join(script_dir, 'js', 'chapters.js')
    os.makedirs(os.path.dirname(js_path), exist_ok=True)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_output)
    
    print(f"\n✅ 챕터 데이터 생성 완료: js/chapters.js")
    print(f"📊 총 {len(chapters_data)}개 챕터 처리됨")

if __name__ == "__main__":
    main()
