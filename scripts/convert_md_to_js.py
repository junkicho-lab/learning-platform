#!/usr/bin/env python3
"""
마크다운 파일을 chapters_abridged.js로 변환하는 스크립트
"""
import os
import re
from pathlib import Path

def md_to_html(md_content):
    """마크다운을 HTML로 변환"""
    html = md_content
    
    # 코드 블록을 플레이스홀더로 보호 (변환 후 복원)
    code_blocks = []
    def save_code_block(m):
        lang = m.group(1) or ''
        code = m.group(2)
        # HTML 특수문자 이스케이프
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        placeholder = f'CODEBLOCKPLACEHOLDER{len(code_blocks)}END'
        code_blocks.append(f'<pre><code class="language-{lang}">{code}</code></pre>')
        return placeholder
    
    html = re.sub(r'```(\w*)\n(.*?)```', save_code_block, html, flags=re.DOTALL)
    
    # 인라인 코드도 플레이스홀더로 보호
    inline_codes = []
    def save_inline_code(m):
        code = m.group(1)
        placeholder = f'INLINECODEPLACEHOLDER{len(inline_codes)}END'
        inline_codes.append(f'<code>{code}</code>')
        return placeholder
    
    def save_obsidian_link_code(m):
        link = m.group(1)
        placeholder = f'INLINECODEPLACEHOLDER{len(inline_codes)}END'
        inline_codes.append(f'<code class="obsidian-link">[[{link}]]</code>')
        return placeholder
    
    html = re.sub(r'`\[\[([^\]]+)\]\]`', save_obsidian_link_code, html)
    html = re.sub(r'`([^`]+)`', save_inline_code, html)
    
    # 헤더
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 수평선
    html = re.sub(r'^---+$', r'<hr/>', html, flags=re.MULTILINE)
    
    # 볼드/이탤릭
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)
    
    # 인용문 (blockquote)
    lines = html.split('\n')
    in_blockquote = False
    result_lines = []
    blockquote_content = []
    
    for line in lines:
        if line.startswith('> '):
            if not in_blockquote:
                in_blockquote = True
            blockquote_content.append(line[2:])
        else:
            if in_blockquote:
                result_lines.append('<blockquote>' + '<br/>'.join(blockquote_content) + '</blockquote>')
                blockquote_content = []
                in_blockquote = False
            result_lines.append(line)
    
    if in_blockquote:
        result_lines.append('<blockquote>' + '<br/>'.join(blockquote_content) + '</blockquote>')
    
    html = '\n'.join(result_lines)
    
    # 테이블 변환
    def convert_table(match):
        table_text = match.group(0)
        lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return table_text
        
        # 헤더 행
        header_cells = [c.strip() for c in lines[0].split('|') if c.strip()]
        # 구분선 건너뛰기 (lines[1])
        # 데이터 행
        data_rows = lines[2:] if len(lines) > 2 else []
        
        html_table = '<table><thead><tr>'
        for cell in header_cells:
            html_table += f'<th>{cell}</th>'
        html_table += '</tr></thead><tbody>'
        
        for row in data_rows:
            cells = [c.strip() for c in row.split('|') if c.strip()]
            html_table += '<tr>'
            for cell in cells:
                html_table += f'<td>{cell}</td>'
            html_table += '</tr>'
        
        html_table += '</tbody></table>'
        return html_table
    
    # 테이블 패턴 매칭
    table_pattern = r'\|[^\n]+\|\n\|[-:\| ]+\|\n(?:\|[^\n]+\|\n?)+'
    html = re.sub(table_pattern, convert_table, html)
    
    # 리스트 변환
    lines = html.split('\n')
    result_lines = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        stripped = line.strip()
        
        # 순서 없는 리스트
        if stripped.startswith('- '):
            if not in_ul:
                result_lines.append('<ul>')
                in_ul = True
            result_lines.append(f'<li>{stripped[2:]}</li>')
        # 순서 있는 리스트
        elif re.match(r'^\d+\. ', stripped):
            if not in_ol:
                result_lines.append('<ol>')
                in_ol = True
            content = re.sub(r'^\d+\. ', '', stripped)
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            result_lines.append(line)
    
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')
    
    html = '\n'.join(result_lines)
    
    # 단락 (빈 줄로 구분된 텍스트)
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 이미 HTML 태그로 시작하면 그대로
        if p.startswith('<') or p.startswith('\n<'):
            result.append(p)
        else:
            # 여러 줄이면 각각 p 태그
            lines = p.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('<'):
                    result.append(f'<p>{line}</p>')
                elif line:
                    result.append(line)
    
    html = '\n'.join(result)
    
    # 플레이스홀더 복원
    for i, code in enumerate(code_blocks):
        html = html.replace(f'CODEBLOCKPLACEHOLDER{i}END', code)
    for i, code in enumerate(inline_codes):
        html = html.replace(f'INLINECODEPLACEHOLDER{i}END', code)
    
    return html

def escape_js_string(s):
    """JavaScript 문자열 이스케이프"""
    s = s.replace('\\', '\\\\')
    s = s.replace('`', '\\`')
    s = s.replace('${', '\\${')
    return s

def get_chapter_info(filename, content):
    """파일명과 내용에서 챕터 정보 추출"""
    # 첫 번째 헤더에서 제목 추출
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else filename
    
    # 설명 추출 (첫 번째 단락 또는 "이 장을 마치면..." 섹션)
    desc_match = re.search(r'## 이 장을 마치면\.\.\.\n\n(.+?)(?:\n\n|$)', content, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1)[:100].strip()
    else:
        # 첫 번째 일반 단락
        para_match = re.search(r'\n\n([^#\n][^\n]+)', content)
        desc = para_match.group(1)[:100].strip() if para_match else ""
    
    return title, desc

def main():
    base_dir = Path('/Users/woodncarpenter/Desktop/learning-platform 복사본')
    md_dir = base_dir / '수정본_축약'
    output_file = base_dir / 'js' / 'chapters_abridged.js'
    
    # 파일 순서 정의
    file_order = [
        'P00_프롤로그.md',
        '제1장_수정본.md',
        '제2장_수정본.md',
        '제3장_수정본.md',
        '제4장_수정본.md',
        '제5장_수정본.md',
        '제6장_수정본.md',
        '제7장_수정본.md',
        '제8장_수정본.md',
        '제9장_수정본.md',
        '제10장_수정본.md',
        '제10-5장_회고특별편.md',
        '제11장_수정본.md',
        '제12장_수정본.md',
        '제13장_수정본.md',
        'P01_에필로그.md',
        'P02_부록.md',
    ]
    
    chapters = []
    
    for idx, filename in enumerate(file_order):
        filepath = md_dir / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title, desc = get_chapter_info(filename, content)
        html_content = md_to_html(content)
        html_content = escape_js_string(html_content)
        
        # 제목 정리 및 이스케이프
        title = title.replace('📘 ', '').strip()
        title = escape_js_string(title)
        desc = escape_js_string(desc)
        
        chapters.append({
            'id': idx,
            'title': title,
            'description': desc,
            'content': html_content
        })
        print(f"Converted: {filename} -> {title}")
    
    # JS 파일 생성
    js_content = """// 자동 생성된 챕터 데이터 (수정본_축약 마크다운에서 변환)
// 생성일: 2025-12-15
const CHAPTERS_DATA_ABRIDGED = [
"""
    
    for ch in chapters:
        js_content += f"""    {{
        id: {ch['id']},
        title: `{ch['title']}`,
        description: `{ch['description']}`,
        content: `{ch['content']}`
    }},
"""
    
    js_content += "];\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\nGenerated: {output_file}")
    print(f"Total chapters: {len(chapters)}")

if __name__ == '__main__':
    main()
