#!/usr/bin/env python3
"""
수정본 마크다운 파일들을 파싱하여 JavaScript 챕터 데이터로 변환
(외부 라이브러리 없이 순수 Python으로 구현)
"""

import os
import re
from datetime import datetime

# 챕터 정보 (파일명, 제목, 설명)
CHAPTERS = [
    ("P00_프롤로그.md", "프롤로그", "왜 우리는 매일 까먹고, 매년 똑같이 힘들까?"),
    ("제1장_수정본.md", "제1장. 작심삼일 없는 '3분 기록' 세팅", "데일리 노트와 ORID 템플릿으로 시작하기"),
    ("제2장_수정본.md", "제2장. 마법의 대괄호, 링크의 발견", "[[]] 링크로 정보를 연결하는 방법"),
    ("제3장_수정본.md", "제3장. 기록의 골든타임", "언제 쓸 것인가? 최적의 기록 타이밍"),
    ("제4장_수정본.md", "제4장. 시간 여행자의 클릭", "링크와 백링크로 과거 기록 탐색"),
    ("제5장_수정본.md", "제5장. 꼬리에 꼬리를 무는 단서 찾기 (인물편)", "학생별 기록 추적과 패턴 발견"),
    ("제6장_수정본.md", "제6장. 교사의 데자뷰는 데이터가 된다 (환경편)", "반복되는 상황의 패턴 분석"),
    ("제7장_수정본.md", "제7장. 살아있는 생활기록부", "학생 프로파일링과 MOC 구축"),
    ("제8장_수정본.md", "제8장. 나만의 수업 백과사전 구축하기", "수업 자료와 노하우 체계화"),
    ("제9장_수정본.md", "제9장. 나만의 행사 업무 매뉴얼 구축하기", "학교 행사와 업무 템플릿화"),
    ("제10장_수정본.md", "제10장. 내 교실의 우주를 보다", "그래프 뷰로 지식 네트워크 시각화"),
    ("제11장_수정본.md", "제11장. 위기의 순간, 나를 지키는 방패", "민원 대응과 기록의 힘"),
    ("제12장_수정본.md", "제12장. 학기 말의 구세주", "NEIS 업무와 생기부 작성 효율화"),
    ("제13장_수정본.md", "제13장. 기록하는 노동자에서 성장하는 교육자로", "기록을 통한 교사 성장"),
    ("P01_에필로그.md", "에필로그", "기록의 여정을 마치며"),
    ("P02_부록.md", "부록", "박 선생님을 위한 '떠먹여 주는' 자료실"),
]

def convert_md_to_html(md_content):
    """마크다운을 HTML로 변환 (순수 Python 구현)"""
    lines = md_content.split('\n')
    html_lines = []
    in_code_block = False
    in_table = False
    in_list = False
    in_blockquote = False
    list_type = None
    table_rows = []
    blockquote_lines = []
    in_journey_box = False  # 지금까지의 여정 박스 상태
    journey_box_lines = []
    next_code_is_journey = False  # 다음 코드 블록이 여정 박스인지
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # '지금까지의 여정' 헤더 감지
        if '지금까지의 여정' in line and line.strip().startswith('#'):
            next_code_is_journey = True
        
        # 코드 블록 처리
        if line.strip().startswith('```'):
            if in_code_block:
                if in_journey_box:
                    # 여정 박스 닫기 - 리스트 형태로 변환
                    html_lines.append('<div class="journey-box"><ul>')
                    for jline in journey_box_lines:
                        if jline.strip():
                            html_lines.append(f'<li>{jline}</li>')
                    html_lines.append('</ul></div>')
                    journey_box_lines = []
                    in_journey_box = False
                else:
                    html_lines.append('</code></pre>')
                in_code_block = False
            else:
                if next_code_is_journey:
                    in_journey_box = True
                    next_code_is_journey = False
                else:
                    lang = line.strip()[3:].strip()
                    html_lines.append(f'<pre><code class="language-{lang}">' if lang else '<pre><code>')
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            if in_journey_box:
                journey_box_lines.append(line)
            else:
                html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue
        
        # 빈 줄 처리
        if not line.strip():
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            if in_blockquote:
                html_lines.append('<blockquote>' + '<br/>'.join(blockquote_lines) + '</blockquote>')
                blockquote_lines = []
                in_blockquote = False
            if in_table:
                html_lines.append(convert_table_to_html(table_rows))
                table_rows = []
                in_table = False
            i += 1
            continue
        
        # 테이블 처리
        if '|' in line and line.strip().startswith('|'):
            in_table = True
            table_rows.append(line)
            i += 1
            continue
        elif in_table:
            html_lines.append(convert_table_to_html(table_rows))
            table_rows = []
            in_table = False
        
        # 인용문 처리
        if line.strip().startswith('>'):
            quote_content = line.strip()[1:].strip()
            if in_blockquote:
                blockquote_lines.append(process_inline(quote_content))
            else:
                in_blockquote = True
                blockquote_lines = [process_inline(quote_content)]
            i += 1
            continue
        elif in_blockquote:
            html_lines.append('<blockquote>' + '<br/>'.join(blockquote_lines) + '</blockquote>')
            blockquote_lines = []
            in_blockquote = False
        
        # 헤더 처리
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            content = process_inline(header_match.group(2))
            html_lines.append(f'<h{level}>{content}</h{level}>')
            i += 1
            continue
        
        # 수평선 처리
        if re.match(r'^---+$', line.strip()) or re.match(r'^\*\*\*+$', line.strip()):
            html_lines.append('<hr/>')
            i += 1
            continue
        
        # 리스트 처리
        ul_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        
        if ul_match:
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_lines.append(f'<li>{process_inline(ul_match.group(2))}</li>')
            i += 1
            continue
        elif ol_match:
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_lines.append(f'<li>{process_inline(ol_match.group(2))}</li>')
            i += 1
            continue
        elif in_list:
            html_lines.append(f'</{list_type}>')
            in_list = False
            list_type = None
        
        # 일반 단락
        if line.strip():
            html_lines.append(f'<p>{process_inline(line)}</p>')
        
        i += 1
    
    # 마무리 처리
    if in_list:
        html_lines.append(f'</{list_type}>')
    if in_blockquote:
        html_lines.append('<blockquote>' + '<br/>'.join(blockquote_lines) + '</blockquote>')
    if in_table:
        html_lines.append(convert_table_to_html(table_rows))
    if in_code_block:
        html_lines.append('</code></pre>')
    
    return '\n'.join(html_lines)

def convert_table_to_html(rows):
    """테이블 행들을 HTML 테이블로 변환"""
    if not rows:
        return ''
    
    html = '<table>'
    header_done = False
    
    for row in rows:
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        
        # 구분선 행 건너뛰기
        if all(re.match(r'^:?-+:?$', c) for c in cells):
            continue
        
        if not header_done:
            html += '<thead><tr>'
            for cell in cells:
                html += f'<th>{process_inline(cell)}</th>'
            html += '</tr></thead><tbody>'
            header_done = True
        else:
            html += '<tr>'
            for cell in cells:
                html += f'<td>{process_inline(cell)}</td>'
            html += '</tr>'
    
    html += '</tbody></table>'
    return html

def process_inline(text):
    """인라인 마크다운 처리 (볼드, 이탤릭, 코드, 링크 등)"""
    # [[옵시디언 링크]] 처리
    text = re.sub(r'\[\[([^\]]+)\]\]', r'<code class="obsidian-link">[[\1]]</code>', text)
    
    # 이미지 처리
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1"/>', text)
    
    # 링크 처리
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    # 인라인 코드 처리 (백틱)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # 볼드+이탤릭 (***text***)
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\1</em></strong>', text)
    
    # 볼드 (**text**)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # 이탤릭 (*text*)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    # 이탤릭 (_text_) - 단어 경계 확인
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', text)
    
    return text

def escape_js_string(s):
    """JavaScript 문자열 이스케이프"""
    s = s.replace('\\', '\\\\')
    s = s.replace('${', '\\${')
    # 백틱을 HTML 엔티티로 변환 (JavaScript 템플릿 리터럴 충돌 방지)
    s = s.replace('`', '&#96;')
    return s

def escape_for_js_template(title, description, content):
    """JavaScript 템플릿 리터럴용 이스케이프"""
    def escape(s):
        s = s.replace('\\', '\\\\')
        s = s.replace('`', '\\`')
        s = s.replace('${', '\\${')
        return s
    return escape(title), escape(description), escape(content)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_dir = os.path.join(script_dir, '수정본')
    
    chapters_data = []
    
    for i, (filename, title, description) in enumerate(CHAPTERS):
        md_path = os.path.join(md_dir, filename)
        
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = convert_md_to_html(md_content)
            html_content = escape_js_string(html_content)
            
            chapters_data.append({
                'id': i,
                'filename': filename,
                'title': title,
                'description': description,
                'content': html_content
            })
            print(f"✓ 처리 완료: {filename} ({title})")
        else:
            print(f"⚠ 파일 없음: {filename}")
    
    # JavaScript 파일 생성
    js_output = "// 자동 생성된 챕터 데이터 (수정본 마크다운에서 변환)\n"
    js_output += "// 생성일: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
    js_output += "const CHAPTERS_DATA = [\n"
    
    for ch in chapters_data:
        # JavaScript 템플릿 리터럴 이스케이프 처리
        # 백슬래시는 HTML에서 불필요하므로 제거, 백틱과 ${만 이스케이프
        title_escaped = ch['title'].replace('`', '\\`').replace('${', '\\${')
        desc_escaped = ch['description'].replace('`', '\\`').replace('${', '\\${')
        content_escaped = ch['content'].replace('`', '\\`').replace('${', '\\${')
        
        js_output += f"""    {{
        id: {ch['id']},
        title: `{title_escaped}`,
        description: `{desc_escaped}`,
        content: `{content_escaped}`
    }},
"""
    
    js_output += "];\n"
    
    # 파일 저장
    js_path = os.path.join(script_dir, 'js', 'chapters.js')
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_output)
    
    print(f"\n✅ 챕터 데이터 생성 완료: js/chapters.js")
    print(f"📊 총 {len(chapters_data)}개 챕터 처리됨")

if __name__ == "__main__":
    main()
