#!/usr/bin/env python3
"""
출판용 변환 스크립트
- PDF 생성 (인쇄용 레이아웃)
- EPUB 생성 (전자책 플랫폼용)
- Word(DOCX) 변환 (출판사 투고용)
- 목차 자동 생성
- 페이지 번호, 머리글/바닥글
"""

import os
import subprocess
import sys
from datetime import datetime

# 설정
BOOK_TITLE = "교사를 위한 옵시디언"
BOOK_SUBTITLE = "꼬꼬무 기록법으로 시작하는 교직 생활 관리"
AUTHOR = "저자명"  # 실제 저자명으로 변경하세요
PUBLISHER = ""
LANGUAGE = "ko-KR"
DATE = datetime.now().strftime("%Y-%m-%d")

# 파일 순서 (출판 순서대로)
FILE_ORDER = [
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

def check_pandoc():
    """Pandoc 설치 확인"""
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        print(f"✓ Pandoc 설치됨: {result.stdout.split(chr(10))[0]}")
        return True
    except FileNotFoundError:
        print("✗ Pandoc이 설치되어 있지 않습니다.")
        print("  설치 방법: brew install pandoc")
        return False

def check_latex():
    """LaTeX 설치 확인 (PDF 생성용)"""
    try:
        result = subprocess.run(["xelatex", "--version"], capture_output=True, text=True)
        print(f"✓ XeLaTeX 설치됨")
        return True
    except FileNotFoundError:
        print("⚠ XeLaTeX이 설치되어 있지 않습니다. PDF 생성이 제한됩니다.")
        print("  설치 방법: brew install --cask mactex-no-gui")
        return False

def get_script_dir():
    """스크립트 디렉토리 반환"""
    return os.path.dirname(os.path.abspath(__file__))

def get_md_files(source_dir="수정본"):
    """마크다운 파일 목록 반환 (순서대로)"""
    script_dir = get_script_dir()
    md_dir = os.path.join(script_dir, source_dir)
    
    files = []
    for filename in FILE_ORDER:
        filepath = os.path.join(md_dir, filename)
        if os.path.exists(filepath):
            files.append(filepath)
        else:
            print(f"⚠ 파일 없음: {filename}")
    
    return files

def create_output_dir(subdir=""):
    """출력 디렉토리 생성"""
    script_dir = get_script_dir()
    if subdir:
        output_dir = os.path.join(script_dir, "출판물", subdir)
    else:
        output_dir = os.path.join(script_dir, "출판물")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def create_metadata_yaml(output_dir):
    """Pandoc 메타데이터 YAML 파일 생성"""
    metadata = f"""---
title: "{BOOK_TITLE}"
subtitle: "{BOOK_SUBTITLE}"
author: "{AUTHOR}"
date: "{DATE}"
lang: "{LANGUAGE}"
toc: true
toc-title: "목차"
toc-depth: 2
numbersections: false
documentclass: book
papersize: a5
fontsize: 11pt
linestretch: 1.5
geometry:
  - top=25mm
  - bottom=25mm
  - left=20mm
  - right=20mm
mainfont: "Noto Sans KR"
sansfont: "Noto Sans KR"
monofont: "D2Coding"
header-includes:
  - |
    \\usepackage{{fancyhdr}}
    \\pagestyle{{fancy}}
    \\fancyhead[LE,RO]{{\\thepage}}
    \\fancyhead[RE]{{\\leftmark}}
    \\fancyhead[LO]{{{BOOK_TITLE}}}
    \\fancyfoot[C]{{}}
    \\renewcommand{{\\headrulewidth}}{{0.4pt}}
---
"""
    
    metadata_path = os.path.join(output_dir, "metadata.yaml")
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(metadata)
    
    return metadata_path

def create_epub_css(output_dir):
    """EPUB용 CSS 파일 생성"""
    css = """
/* EPUB 스타일 */
body {
    font-family: "Noto Sans KR", sans-serif;
    line-height: 1.8;
    text-align: justify;
}

h1 {
    font-size: 1.8em;
    border-bottom: 2px solid #4A6C6F;
    padding-bottom: 10px;
    margin-top: 2em;
}

h2 {
    font-size: 1.4em;
    color: #4A6C6F;
    margin-top: 1.5em;
}

h3 {
    font-size: 1.2em;
    color: #4A6C6F;
}

blockquote {
    background-color: #F5F3EF;
    padding: 15px 20px;
    border-left: 4px solid #4A6C6F;
    margin: 20px 0;
    font-style: italic;
}

code {
    background-color: #F0E5DE;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: monospace;
}

pre {
    background-color: #3A3A3A;
    color: #FFFFFF;
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
}

pre code {
    background-color: transparent;
    color: #FFFFFF;
}

pre code * {
    color: #FFFFFF !important;
    background-color: transparent !important;
}

pre a, pre code a {
    color: #FFFFFF !important;
    text-decoration: underline;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

th, td {
    padding: 10px;
    border-bottom: 1px solid #E0E0E0;
    text-align: left;
}

th {
    background-color: #EBEBEB;
    font-weight: bold;
}

/* 특수 박스 */
.tip-box {
    background-color: #F0E5DE;
    padding: 15px;
    border-left: 5px solid #C4A16E;
    margin: 20px 0;
}

.journey-box {
    background-color: #E8F4E8;
    padding: 15px;
    border-left: 5px solid #4CAF50;
    margin: 20px 0;
}
"""
    
    css_path = os.path.join(output_dir, "epub.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    
    return css_path

def merge_markdown_files(md_files, output_dir):
    """마크다운 파일들을 하나로 병합"""
    merged_content = []
    
    for filepath in md_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            merged_content.append(content)
            merged_content.append("\n\n\\newpage\n\n")  # 페이지 구분
    
    merged_path = os.path.join(output_dir, "merged.md")
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write("\n".join(merged_content))
    
    return merged_path

def build_pdf(md_files, output_dir, metadata_path):
    """PDF 생성 (XeLaTeX 사용)"""
    print("\n📄 PDF 생성 중 (XeLaTeX)...")
    
    output_path = os.path.join(output_dir, f"{BOOK_TITLE}.pdf")
    
    cmd = [
        "pandoc",
        *md_files,
        "-o", output_path,
        "--metadata-file", metadata_path,
        "--pdf-engine=xelatex",
        "--toc",
        "--toc-depth=2",
        "-V", "toc-title=목차",
        "-V", f"title={BOOK_TITLE}",
        "-V", f"author={AUTHOR}",
        "-V", "documentclass=book",
        "-V", "papersize=a5",
        "-V", "fontsize=11pt",
        "-V", "linestretch=1.5",
        "-V", "geometry:top=25mm,bottom=25mm,left=20mm,right=20mm",
        "-V", "mainfont=Noto Sans KR",
        "-V", "sansfont=Noto Sans KR",
        "-V", "monofont=D2Coding",
        "--highlight-style=tango",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PDF 생성 완료: {output_path}")
            return output_path
        else:
            print(f"✗ PDF 생성 실패: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ PDF 생성 오류: {e}")
        return None

def build_pdf_weasyprint(html_path, output_dir):
    """PDF 생성 (WeasyPrint 사용 - XeLaTeX 대안)"""
    print("\n📄 PDF 생성 중 (WeasyPrint)...")
    
    output_path = os.path.join(output_dir, f"{BOOK_TITLE}.pdf")
    
    cmd = [
        "weasyprint",
        html_path,
        output_path,
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PDF 생성 완료: {output_path}")
            return output_path
        else:
            print(f"✗ PDF 생성 실패: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ PDF 생성 오류: {e}")
        return None

def build_epub(md_files, output_dir, css_path):
    """EPUB 생성"""
    print("\n📱 EPUB 생성 중...")
    
    output_path = os.path.join(output_dir, f"{BOOK_TITLE}.epub")
    
    cmd = [
        "pandoc",
        *md_files,
        "-o", output_path,
        "--toc",
        "--toc-depth=2",
        f"--metadata=title:{BOOK_TITLE}",
        f"--metadata=author:{AUTHOR}",
        f"--metadata=lang:{LANGUAGE}",
        f"--css={css_path}",
        "--epub-chapter-level=1",
    ]
    
    # 표지 이미지가 있으면 추가
    script_dir = get_script_dir()
    cover_path = os.path.join(script_dir, "cover.jpg")
    if os.path.exists(cover_path):
        cmd.append(f"--epub-cover-image={cover_path}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ EPUB 생성 완료: {output_path}")
            return output_path
        else:
            print(f"✗ EPUB 생성 실패: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ EPUB 생성 오류: {e}")
        return None

def build_docx(md_files, output_dir):
    """Word(DOCX) 생성"""
    print("\n📝 Word(DOCX) 생성 중...")
    
    output_path = os.path.join(output_dir, f"{BOOK_TITLE}.docx")
    
    cmd = [
        "pandoc",
        *md_files,
        "-o", output_path,
        "--toc",
        "--toc-depth=2",
        f"--metadata=title:{BOOK_TITLE}",
        f"--metadata=author:{AUTHOR}",
        "--reference-doc=" if False else "",  # 템플릿이 있으면 사용
    ]
    
    # 빈 문자열 제거
    cmd = [c for c in cmd if c]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Word(DOCX) 생성 완료: {output_path}")
            return output_path
        else:
            print(f"✗ Word(DOCX) 생성 실패: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Word(DOCX) 생성 오류: {e}")
        return None

def build_html(md_files, output_dir, css_path):
    """HTML 생성 (HWP 변환용)"""
    print("\n🌐 HTML 생성 중 (HWP 변환용)...")
    
    output_path = os.path.join(output_dir, f"{BOOK_TITLE}.html")
    
    cmd = [
        "pandoc",
        *md_files,
        "-o", output_path,
        "--standalone",
        "--toc",
        "--toc-depth=2",
        f"--metadata=title:{BOOK_TITLE}",
        f"--metadata=author:{AUTHOR}",
        f"--css={css_path}",
        "--embed-resources",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ HTML 생성 완료: {output_path}")
            print("  💡 HWP 변환: 한글에서 HTML 파일을 열어 저장하세요.")
            return output_path
        else:
            print(f"✗ HTML 생성 실패: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ HTML 생성 오류: {e}")
        return None

def generate_toc(md_files, output_dir):
    """목차 파일 생성"""
    print("\n📑 목차 생성 중...")
    
    toc_lines = [
        f"# {BOOK_TITLE}",
        f"## {BOOK_SUBTITLE}",
        "",
        f"**저자:** {AUTHOR}",
        f"**생성일:** {DATE}",
        "",
        "---",
        "",
        "# 목차",
        "",
    ]
    
    chapter_num = 0
    for filepath in md_files:
        filename = os.path.basename(filepath)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 첫 번째 h1 제목 찾기
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                
                if "프롤로그" in filename:
                    toc_lines.append(f"- **프롤로그:** {title}")
                elif "에필로그" in filename:
                    toc_lines.append(f"- **에필로그:** {title}")
                elif "부록" in filename:
                    toc_lines.append(f"- **부록:** {title}")
                elif "제" in filename and "장" in filename:
                    chapter_num += 1
                    toc_lines.append(f"- **제{chapter_num}장:** {title}")
                else:
                    toc_lines.append(f"- {title}")
                break
    
    toc_path = os.path.join(output_dir, "목차.md")
    with open(toc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(toc_lines))
    
    print(f"✓ 목차 생성 완료: {toc_path}")
    return toc_path

def print_summary(output_dir):
    """생성된 파일 요약"""
    print("\n" + "=" * 50)
    print("📚 출판물 생성 완료!")
    print("=" * 50)
    print(f"\n📁 출력 폴더: {output_dir}")
    print("\n생성된 파일:")
    
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        size = os.path.getsize(filepath)
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
        print(f"  - {filename} ({size_str})")
    
    print("\n💡 다음 단계:")
    print("  1. PDF: 인쇄소에 전달하거나 전자책으로 배포")
    print("  2. EPUB: 리디북스, 교보문고 등에 업로드")
    print("  3. DOCX: 출판사 투고용 원고로 사용")
    print("  4. HTML: 한글(HWP)에서 열어 HWP로 저장")

def build_book(source_dir="수정본", output_subdir="", title_suffix=""):
    """출판물 빌드 함수"""
    book_title = BOOK_TITLE + title_suffix
    
    print("=" * 50)
    print(f"📚 {book_title} - 출판용 변환 스크립트")
    print("=" * 50)
    
    # 환경 확인
    print("\n🔍 환경 확인 중...")
    has_pandoc = check_pandoc()
    has_latex = check_latex()
    
    if not has_pandoc:
        print("\n❌ Pandoc이 필요합니다. 설치 후 다시 실행하세요.")
        print("   brew install pandoc")
        return False
    
    # 파일 준비
    md_files = get_md_files(source_dir)
    print(f"\n📄 마크다운 파일 {len(md_files)}개 발견 ({source_dir})")
    
    # 출력 디렉토리 생성
    output_dir = create_output_dir(output_subdir)
    print(f"📁 출력 폴더: {output_dir}")
    
    # 메타데이터 및 CSS 생성
    metadata_path = create_metadata_yaml(output_dir)
    css_path = create_epub_css(output_dir)
    
    # 목차 생성
    generate_toc(md_files, output_dir)
    
    # 각 형식으로 변환
    results = {}
    
    # EPUB
    results["EPUB"] = build_epub(md_files, output_dir, css_path)
    
    # Word (DOCX)
    results["DOCX"] = build_docx(md_files, output_dir)
    
    # HTML (HWP 변환용)
    results["HTML"] = build_html(md_files, output_dir, css_path)
    
    # PDF (WeasyPrint 사용 - HTML에서 변환)
    if results["HTML"]:
        results["PDF"] = build_pdf_weasyprint(results["HTML"], output_dir)
    
    # 요약 출력
    print_summary(output_dir)
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="출판물 생성 스크립트")
    parser.add_argument("--abridged", action="store_true", help="축약본 출판물 생성")
    parser.add_argument("--full", action="store_true", help="원본 출판물 생성")
    parser.add_argument("--all", action="store_true", help="원본 + 축약본 모두 생성")
    args = parser.parse_args()
    
    # 기본값: 원본만 생성
    if not args.abridged and not args.full and not args.all:
        args.full = True
    
    if args.all or args.full:
        print("\n" + "=" * 60)
        print("📚 원본 출판물 생성")
        print("=" * 60)
        build_book(source_dir="수정본", output_subdir="원본", title_suffix="")
    
    if args.all or args.abridged:
        print("\n" + "=" * 60)
        print("⚡ 축약본 출판물 생성")
        print("=" * 60)
        build_book(source_dir="수정본_축약", output_subdir="축약본", title_suffix=" (축약본)")

if __name__ == "__main__":
    main()
