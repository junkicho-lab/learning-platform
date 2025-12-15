#!/usr/bin/env python3
"""
수정본_축약 폴더의 마크다운 파일들을 출판용 파일(EPUB, PDF, DOCX)로 변환하는 스크립트
출력: 출판물(3판) 폴더
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

def merge_markdown_files(source_dir, output_file):
    """마크다운 파일들을 하나로 합치기"""
    file_order = get_file_order()
    
    # 폴더 내 파일 맵 생성 (정규화된 이름 -> 실제 경로)
    file_map = {}
    for f in source_dir.glob('*.md'):
        normalized = normalize_name(f.name)
        file_map[normalized] = f
    
    merged_content = []
    
    # 메타데이터 추가
    merged_content.append('---')
    merged_content.append('title: "옵시디언으로 교실 기록하기"')
    merged_content.append('subtitle: "바쁜 선생님을 위한 실용 가이드 (축약본)"')
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
            merged_content.append('\n\\newpage\n')  # 페이지 구분
            print(f"  Added: {filename}")
        else:
            print(f"  Not found: {filename}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_content))
    
    return output_file

def convert_to_formats(merged_md, output_dir, base_name):
    """다양한 형식으로 변환"""
    results = {}
    
    # EPUB 변환
    epub_file = output_dir / f'{base_name}.epub'
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(epub_file),
        '--toc',
        '--toc-depth=2',
        '--epub-chapter-level=1',
        '-f', 'markdown+smart'
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
    
    # HTML 변환 (PDF 변환용)
    html_file = output_dir / f'{base_name}.html'
    cmd = [
        'pandoc', str(merged_md),
        '-o', str(html_file),
        '--toc',
        '--toc-depth=2',
        '-f', 'markdown+smart',
        '--standalone',
        '--self-contained',
        '-c', 'https://cdn.jsdelivr.net/npm/water.css@2/out/water.css'
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        results['html'] = html_file
        print(f"  Created: {html_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"  HTML Error: {e.stderr.decode()}")
    
    # PDF 변환 (weasyprint 사용)
    pdf_file = output_dir / f'{base_name}.pdf'
    try:
        cmd = ['weasyprint', str(html_file), str(pdf_file)]
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
    
    # 수정본_축약 폴더 사용
    source_dir = base_dir / '수정본_축약'
    output_dir = base_dir / '출판물(3판)'
    output_dir.mkdir(exist_ok=True)
    
    print("=== 축약본 출판 변환 (3판) ===")
    print(f"소스: {source_dir}")
    print(f"출력: {output_dir}")
    
    print("\n1. 마크다운 파일 병합 중...")
    merged_md = output_dir / '옵시디언으로_교실_기록하기.md'
    merge_markdown_files(source_dir, merged_md)
    
    print("\n2. 출판 형식으로 변환 중...")
    convert_to_formats(merged_md, output_dir, '옵시디언으로_교실_기록하기')
    
    print("\n=== 완료 ===")
    print(f"출력 폴더: {output_dir}")
    print("\n※ HWP 형식은 DOCX 파일을 한글에서 열어 저장하세요.")

if __name__ == '__main__':
    main()
