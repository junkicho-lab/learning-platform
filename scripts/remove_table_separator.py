#!/usr/bin/env python3
"""
마크다운 파일에서 표의 두 번째 줄(구분선)을 삭제하는 스크립트
예: |:--|:--|:--| 형태의 줄 삭제
"""
import re
import unicodedata
from pathlib import Path

def remove_table_separators(content):
    """마크다운 표의 구분선(두 번째 줄) 삭제"""
    # 표 구분선 패턴: |로 시작하고 :, -, |, 공백으로만 구성된 줄
    # 예: |:--|:--|, |---|---|, | :-- | :-- |
    pattern = r'^\|[\s:|\-]+\|[\s]*$'
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # 구분선 패턴에 매칭되면 스킵
        if re.match(pattern, line.strip()):
            continue
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def process_file(file_path):
    """파일 처리"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = remove_table_separators(content)
    
    if content != new_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    folders = ['수정본', '수정본_축약']
    
    total_updated = 0
    
    for folder_name in folders:
        folder_path = base_dir / folder_name
        if not folder_path.exists():
            print(f"Folder not found: {folder_name}")
            continue
        
        print(f"\n=== {folder_name} ===")
        
        for md_file in sorted(folder_path.glob('*.md')):
            if process_file(md_file):
                print(f"  Updated: {md_file.name}")
                total_updated += 1
            else:
                print(f"  No change: {md_file.name}")
    
    print(f"\nTotal updated: {total_updated} files")

if __name__ == '__main__':
    main()
