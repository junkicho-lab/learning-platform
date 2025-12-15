#!/usr/bin/env python3
"""
수정본 마크다운 파일들을 하나로 합치고 각 장 사이에 페이지 구분 추가
- 각 장 내부의 부록/한페이지 요약 섹션은 페이지 나누지 않음
- 노트(코드 블록) 스타일: 옅은 회색 배경 + 흰 글자
"""

import os
import re

# 프로젝트 루트
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source_dir = os.path.join(project_root, "수정본")
output_dir = os.path.join(project_root, "출판물", "수정본_출판")

# 챕터 순서
chapters = [
    "P00_프롤로그.md",
    "제1장_수정본.md",
    "제2장_수정본.md",
    "제3장_수정본.md",
    "제4장_수정본.md",
    "제5장_수정본.md",
    "제6장_수정본.md",
    "제7장_수정본.md",
    "제8장_수정본.md",
    "제9장_수정본.md",
    "제10장_수정본.md",
    "제11장_수정본.md",
    "제12장_수정본.md",
    "제13장_수정본.md",
    "P01_에필로그.md",
    "P02_부록.md",
]

# 페이지 구분 (DOCX/PDF용)
PAGE_BREAK = "\n\n<div style=\"page-break-after: always;\"></div>\n\n"

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

def style_code_blocks(content):
    """코드 블록(노트 예시)을 옅은 회색 배경 + 흰 글자 스타일로 변환"""
    # 코드 블록을 HTML div로 변환
    def replace_code_block(match):
        code_content = match.group(1)
        # HTML 특수문자 이스케이프
        code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # 리스트 마커 이스케이프 (Pandoc이 <li>로 변환하지 않도록)
        lines = code_content.split('\n')
        escaped_lines = []
        for line in lines:
            # 리스트 마커 변환: "- " -> "• ", "- [ ]" -> "☐ "
            if line.strip().startswith('- [ ]'):
                line = line.replace('- [ ]', '☐', 1)
            elif line.strip().startswith('- [x]'):
                line = line.replace('- [x]', '☑', 1)
            elif line.strip().startswith('- '):
                line = line.replace('- ', '• ', 1)
            escaped_lines.append(line)
        code_content = '\n'.join(escaped_lines)
        return f'\n\n<pre style="background-color: #6b7280; color: white; padding: 16px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; margin: 16px 0;">{code_content}</pre>\n\n'
    
    # ```로 감싸진 코드 블록 찾기
    pattern = r'```\n?(.*?)```'
    content = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)
    return content

def style_tables(content):
    """마크다운 표를 옅은 베이지색 배경 HTML 표로 변환"""
    lines = content.split('\n')
    result = []
    in_table = False
    table_lines = []
    
    for line in lines:
        # 표 행 감지 (|로 시작하고 |로 끝나는 줄)
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                in_table = True
            table_lines.append(line)
        else:
            if in_table:
                # 표 종료, HTML로 변환
                result.append(convert_table_to_html(table_lines))
                table_lines = []
                in_table = False
            result.append(line)
    
    # 마지막 표 처리
    if in_table and table_lines:
        result.append(convert_table_to_html(table_lines))
    
    return '\n'.join(result)

def escape_html_in_cell(text):
    """셀 내용에서 HTML 특수문자 이스케이프 및 마크다운 처리"""
    # HTML 특수문자 이스케이프
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # 숫자 리스트 마커 변환 (1. 2. 3. 등 -> ①②③ 등)
    text = re.sub(r'^(\d+)\.\s', lambda m: chr(9311 + int(m.group(1))) + ' ', text)
    # 볼드 처리
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 이탤릭 처리
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # 인라인 코드 처리
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def convert_table_to_html(table_lines):
    """마크다운 표를 HTML로 변환"""
    if len(table_lines) < 2:
        return '\n'.join(table_lines)
    
    # 구분선 행 제거 (|:--|:--| 형태)
    filtered_lines = []
    for line in table_lines:
        # 구분선 패턴 체크 (|로 시작하고 :, -, |, 공백만 포함)
        stripped = line.strip()
        if re.match(r'^\|[\s:\-|]+\|$', stripped) and '-' in stripped and not any(c.isalnum() for c in stripped):
            continue  # 구분선 건너뛰기
        filtered_lines.append(line)
    
    if len(filtered_lines) < 1:
        return '\n'.join(table_lines)
    
    html = ['<table style="width: 100%; border-collapse: collapse; margin: 16px 0;">']
    
    for i, line in enumerate(filtered_lines):
        cells = [c.strip() for c in line.strip('|').split('|')]
        
        if i == 0:
            # 헤더 행
            html.append('<tr>')
            for cell in cells:
                cell_escaped = escape_html_in_cell(cell)
                html.append(f'<th style="padding: 10px; border: 1px solid #e0d5c8; background-color: #f0e6d8; font-weight: 600; text-align: left;">{cell_escaped}</th>')
            html.append('</tr>')
        else:
            # 데이터 행
            html.append('<tr>')
            for cell in cells:
                cell_escaped = escape_html_in_cell(cell)
                html.append(f'<td style="padding: 10px; border: 1px solid #e0d5c8; background-color: #faf5ef;">{cell_escaped}</td>')
            html.append('</tr>')
    
    html.append('</table>')
    return '\n'.join(html)

# 파일 합치기
merged_content = []
for i, chapter in enumerate(chapters):
    filepath = os.path.join(source_dir, chapter)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # 코드 블록 스타일 적용
            content = style_code_blocks(content)
            # 표 스타일 적용
            content = style_tables(content)
            merged_content.append(content)
            # 마지막 챕터가 아니면 페이지 구분 추가 (장 사이에만)
            if i < len(chapters) - 1:
                merged_content.append(PAGE_BREAK)
    else:
        print(f"파일 없음: {filepath}")

# 통합 파일 저장
output_path = os.path.join(output_dir, "기억을_잇다_교실을_읽다.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(merged_content))

print(f"통합 파일 생성 완료: {output_path}")
