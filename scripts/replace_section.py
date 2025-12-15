#!/usr/bin/env python3
"""
수정본 폴더의 '이 장을 마치면' 섹션을 수정본_축약 폴더의 내용으로 교체하는 스크립트
"""
import os
import re
import unicodedata
from pathlib import Path

def extract_section(content, section_name):
    """특정 섹션의 내용을 추출 (섹션 헤더 포함, 다음 ## 전까지)"""
    # 섹션 시작 찾기
    lines = content.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('## ') and section_name in line:
            start_idx = i
        elif start_idx is not None and line.strip().startswith('## '):
            end_idx = i
            break
    
    if start_idx is None:
        return None
    
    if end_idx is None:
        end_idx = len(lines)
    
    section_lines = lines[start_idx:end_idx]
    # 끝의 빈 줄 제거
    while section_lines and section_lines[-1].strip() == '':
        section_lines.pop()
    
    return '\n'.join(section_lines)

def replace_section(content, section_name, new_section_content):
    """특정 섹션을 새 내용으로 교체"""
    lines = content.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('## ') and section_name in line:
            start_idx = i
        elif start_idx is not None and line.strip().startswith('## '):
            end_idx = i
            break
    
    if start_idx is None:
        return content
    
    if end_idx is None:
        end_idx = len(lines)
    
    # 새 섹션으로 교체
    new_lines = lines[:start_idx] + [new_section_content, ''] + lines[end_idx:]
    return '\n'.join(new_lines)

def main():
    # 스크립트 위치 기준으로 경로 설정
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    source_dir = base_dir / '수정본_축약'
    target_dir = base_dir / '수정본'
    
    print(f"Base dir: {base_dir}")
    print(f"Source dir exists: {source_dir.exists()}")
    print(f"Target dir exists: {target_dir.exists()}")
    
    section_name = '이 장을 마치면'
    
    # 파일 목록 (한글 유니코드 정규화 - NFC)
    def normalize_name(name):
        return unicodedata.normalize('NFC', name.strip())
    
    source_file_map = {normalize_name(f.name): f for f in source_dir.glob('*.md')}
    target_file_map = {normalize_name(f.name): f for f in target_dir.glob('*.md')}
    
    # 공통 파일 찾기 (정규화된 이름 기준)
    common_names = set(source_file_map.keys()) & set(target_file_map.keys())
    
    updated_count = 0
    
    print(f"Source files: {len(source_file_map)}")
    print(f"Target files: {len(target_file_map)}")
    print(f"Common files: {len(common_names)}")
    
    for filename in sorted(common_names):
        source_path = source_file_map[filename]
        target_path = target_file_map[filename]
        
        print(f"\nProcessing: {filename}")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        with open(target_path, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # 축약본에서 섹션 추출
        new_section = extract_section(source_content, section_name)
        
        if new_section is None:
            print(f"  Skip: 축약본에 '{section_name}' 섹션 없음")
            continue
        
        print(f"  Found in source: {len(new_section)} chars")
        
        # 원본에 해당 섹션이 있는지 확인
        old_section = extract_section(target_content, section_name)
        
        if old_section is None:
            print(f"  Skip: 원본에 '{section_name}' 섹션 없음")
            continue
        
        print(f"  Found in target: {len(old_section)} chars")
        
        # 섹션 교체
        updated_content = replace_section(target_content, section_name, new_section)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"  Updated!")
        updated_count += 1
    
    print(f"\nTotal updated: {updated_count} files")

if __name__ == '__main__':
    main()
