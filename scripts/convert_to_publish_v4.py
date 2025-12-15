#!/usr/bin/env python3
"""
사이트 서식을 적용하여 수정본_축약 폴더의 마크다운 파일들을 출판용 파일로 변환
출력: 출판물(4판) 폴더
"""
import os
import subprocess
import unicodedata
from pathlib import Path

def normalize_name(name):
    return unicodedata.normalize('NFC', name)

def get_file_order():
    """파일 순서 정의"""
    return [
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

# 사이트 스타일을 적용한 CSS
SITE_STYLE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

:root {
    --primary-color: #4A6C6F;
    --primary-light: #5A7C7F;
    --primary-dark: #3A5C5F;
    --accent-color: #C4A16E;
    --bg-color: #F7F6F3;
    --bg-secondary: #EBEBEB;
    --text-color: #37352F;
    --text-light: #6B6B6B;
    --border-color: #E0E0E0;
    --success-color: #4CAF50;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.8;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
}

h1 {
    color: var(--primary-color);
    font-size: 2em;
    font-weight: 700;
    margin: 2em 0 1em 0;
    padding-bottom: 0.5em;
    border-bottom: 3px solid var(--accent-color);
}

h2 {
    color: var(--primary-dark);
    font-size: 1.5em;
    font-weight: 600;
    margin: 1.5em 0 0.8em 0;
    padding-left: 12px;
    border-left: 4px solid var(--primary-color);
}

h3 {
    color: var(--text-color);
    font-size: 1.2em;
    font-weight: 600;
    margin: 1.2em 0 0.6em 0;
}

p {
    margin: 1em 0;
    text-align: justify;
}

/* 표 스타일 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

th {
    background: var(--primary-color);
    color: white;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 12px 15px;
    border-bottom: 1px solid var(--border-color);
}

tr:nth-child(even) {
    background-color: var(--bg-secondary);
}

tr:hover {
    background-color: rgba(74, 108, 111, 0.1);
}

/* 코드 블록 */
pre {
    background: #2D2D2D;
    color: #E0E0E0;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1.5em 0;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
    line-height: 1.5;
}

code {
    background: rgba(74, 108, 111, 0.1);
    color: var(--primary-dark);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre code {
    background: none;
    color: inherit;
    padding: 0;
}

/* 인용문 */
blockquote {
    background: linear-gradient(135deg, rgba(196, 161, 110, 0.1) 0%, rgba(74, 108, 111, 0.1) 100%);
    border-left: 4px solid var(--accent-color);
    padding: 15px 20px;
    margin: 1.5em 0;
    border-radius: 0 8px 8px 0;
    font-style: italic;
}

blockquote p {
    margin: 0;
}

/* 리스트 */
ul, ol {
    margin: 1em 0;
    padding-left: 2em;
}

li {
    margin: 0.5em 0;
}

/* 강조 */
strong {
    color: var(--primary-dark);
    font-weight: 600;
}

em {
    color: var(--accent-color);
}

/* 구분선 */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    margin: 2em 0;
    border-radius: 1px;
}

/* 링크 */
a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* 목차 */
#TOC {
    background: white;
    padding: 20px 30px;
    border-radius: 8px;
    margin-bottom: 2em;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

#TOC ul {
    list-style: none;
    padding-left: 0;
}

#TOC li {
    margin: 0.3em 0;
}

#TOC a {
    color: var(--text-color);
}

/* 페이지 나누기 */
.newpage {
    page-break-before: always;
}

/* 인쇄용 스타일 */
@media print {
    body {
        max-width: none;
        padding: 0;
    }
    
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    table {
        box-shadow: none;
        border: 1px solid var(--border-color);
    }
}

/* 표지 스타일 */
.title-page {
    text-align: center;
    padding: 100px 20px;
    page-break-after: always;
}

.title-page h1 {
    font-size: 2.5em;
    border: none;
    margin-bottom: 0.5em;
}

.title-page .subtitle {
    font-size: 1.3em;
    color: var(--text-light);
    margin-bottom: 2em;
}
"""

def merge_markdown_files(source_dir, output_file):
    """마크다운 파일들을 하나로 합치기"""
    file_order = get_file_order()
    
    file_map = {}
    for f in source_dir.glob('*.md'):
        normalized = normalize_name(f.name)
        file_map[normalized] = f
    
    merged_content = []
    
    # 메타데이터
    merged_content.append('---')
    merged_content.append('title: "옵시디언으로 교실 기록하기"')
    merged_content.append('subtitle: "바쁜 선생님을 위한 실용 가이드"')
    merged_content.append('author: ""')
    merged_content.append('lang: ko')
    merged_content.append('toc: true')
    merged_content.append('toc-depth: 2')
    merged_content.append('---')
    merged_content.append('')
    
    for filename in file_order:
        normalized_filename = normalize_name(filename)
        if normalized_filename in file_map:
            file_path = file_map[normalized_filename]
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            merged_content.append(content)
            merged_content.append('\n<div class="newpage"></div>\n')
            print(f"  Added: {filename}")
        else:
            print(f"  Not found: {filename}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_content))
    
    return output_file

def create_styled_html(merged_md, output_dir, base_name):
    """사이트 스타일이 적용된 HTML 생성"""
    html_file = output_dir / f'{base_name}.html'
    css_file = output_dir / 'style.css'
    
    # CSS 파일 저장
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(SITE_STYLE_CSS)
    
    # pandoc으로 HTML 변환 (외부 CSS 참조)
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(html_file),
        '--toc',
        '--toc-depth=2',
        '-f', 'markdown+smart',
        '--standalone',
        '-c', 'style.css',
        '--metadata', 'title=옵시디언으로 교실 기록하기'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, cwd=str(output_dir))
        print(f"  Created: {html_file.name}")
        return html_file
    except subprocess.CalledProcessError as e:
        print(f"  HTML Error: {e.stderr.decode()}")
        return None

def create_self_contained_html(merged_md, output_dir, base_name):
    """CSS가 내장된 HTML 생성 (PDF 변환용)"""
    html_file = output_dir / f'{base_name}_styled.html'
    
    # pandoc으로 기본 HTML 생성
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(html_file),
        '--toc',
        '--toc-depth=2',
        '-f', 'markdown+smart',
        '--standalone',
        '--metadata', 'title=옵시디언으로 교실 기록하기'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"  HTML Error: {e.stderr.decode()}")
        return None
    
    # CSS 삽입
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # <head> 태그에 스타일 삽입
    style_tag = f'<style>\n{SITE_STYLE_CSS}\n</style>'
    html_content = html_content.replace('</head>', f'{style_tag}\n</head>')
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  Created: {html_file.name}")
    return html_file

def convert_to_formats(styled_html, merged_md, output_dir, base_name):
    """다양한 형식으로 변환"""
    results = {}
    
    # EPUB 변환
    epub_file = output_dir / f'{base_name}.epub'
    css_file = output_dir / 'style.css'
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(epub_file),
        '--toc',
        '--toc-depth=2',
        '--epub-chapter-level=1',
        '-f', 'markdown+smart',
        '--css', str(css_file)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        results['epub'] = epub_file
        print(f"  Created: {epub_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"  EPUB Error: {e.stderr.decode()}")
    
    # DOCX 변환
    docx_file = output_dir / f'{base_name}.docx'
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(docx_file),
        '--toc',
        '--toc-depth=2',
        '-f', 'markdown+smart'
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        results['docx'] = docx_file
        print(f"  Created: {docx_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"  DOCX Error: {e.stderr.decode()}")
    
    # PDF 변환 (weasyprint 사용)
    pdf_file = output_dir / f'{base_name}.pdf'
    try:
        cmd = ['weasyprint', str(styled_html), str(pdf_file)]
        subprocess.run(cmd, check=True, capture_output=True)
        results['pdf'] = pdf_file
        print(f"  Created: {pdf_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"  PDF Error: {e.stderr.decode()[:200]}")
    except FileNotFoundError:
        print(f"  PDF Error: weasyprint not found")
    
    return results

def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    source_dir = base_dir / '수정본_축약'
    output_dir = base_dir / '출판물(4판)'
    output_dir.mkdir(exist_ok=True)
    
    print("=== 사이트 서식 적용 출판 변환 (4판) ===")
    print(f"소스: {source_dir}")
    print(f"출력: {output_dir}")
    
    print("\n1. 마크다운 파일 병합 중...")
    merged_md = output_dir / '옵시디언으로_교실_기록하기.md'
    merge_markdown_files(source_dir, merged_md)
    
    print("\n2. 사이트 스타일 HTML 생성 중...")
    create_styled_html(merged_md, output_dir, '옵시디언으로_교실_기록하기')
    styled_html = create_self_contained_html(merged_md, output_dir, '옵시디언으로_교실_기록하기')
    
    print("\n3. 출판 형식으로 변환 중...")
    convert_to_formats(styled_html, merged_md, output_dir, '옵시디언으로_교실_기록하기')
    
    print("\n=== 완료 ===")
    print(f"출력 폴더: {output_dir}")
    print("\n※ HWP 형식은 DOCX 파일을 한글에서 열어 저장하세요.")

if __name__ == '__main__':
    main()
