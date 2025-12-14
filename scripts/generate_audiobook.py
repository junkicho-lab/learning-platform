#!/usr/bin/env python3
"""
마크다운 파일을 오디오북(MP3)으로 변환하는 스크립트

사용 방법:
1. Google Cloud TTS 사용 시:
   pip install google-cloud-texttospeech
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   python generate_audiobook.py --provider google

2. macOS 내장 TTS 사용 시 (무료, 설치 불필요):
   python generate_audiobook.py --provider macos

3. gTTS 사용 시 (무료, 인터넷 필요):
   pip install gtts
   python generate_audiobook.py --provider gtts
"""

import os
import re
import argparse
import subprocess
from pathlib import Path

# 챕터 파일 목록
CHAPTERS = [
    ("P00_프롤로그.md", "00_프롤로그"),
    ("제1장_수정본.md", "01_제1장"),
    ("제2장_수정본.md", "02_제2장"),
    ("제3장_수정본.md", "03_제3장"),
    ("제4장_수정본.md", "04_제4장"),
    ("제5장_수정본.md", "05_제5장"),
    ("제6장_수정본.md", "06_제6장"),
    ("제7장_수정본.md", "07_제7장"),
    ("제8장_수정본.md", "08_제8장"),
    ("제9장_수정본.md", "09_제9장"),
    ("제10장_수정본.md", "10_제10장"),
    ("제11장_수정본.md", "11_제11장"),
    ("제12장_수정본.md", "12_제12장"),
    ("제13장_수정본.md", "13_제13장"),
    ("P01_에필로그.md", "14_에필로그"),
    ("P02_부록.md", "15_부록"),
]

def clean_markdown(text):
    """마크다운에서 텍스트만 추출"""
    # 코드 블록 제거
    text = re.sub(r'```[\s\S]*?```', '(코드 생략)', text)
    
    # 인라인 코드 제거
    text = re.sub(r'`[^`]+`', '', text)
    
    # 이미지 제거
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    
    # 링크 텍스트만 남기기
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 옵시디언 링크 처리
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    
    # 헤더 마크 제거
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 볼드/이탤릭 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # 테이블 간소화
    text = re.sub(r'\|[^\n]+\|', '(표 내용)', text)
    text = re.sub(r'\|?:?-+:?\|?', '', text)
    
    # 수평선 제거
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    
    # 인용문 마크 제거
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # 리스트 마크 제거
    text = re.sub(r'^[\s]*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 연속 공백/줄바꿈 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()

def tts_macos(text, output_path, voice="Yuna"):
    """macOS 내장 TTS 사용 (무료)"""
    # AIFF로 먼저 생성 후 MP3로 변환
    aiff_path = output_path.replace('.mp3', '.aiff')
    
    # say 명령어로 음성 생성
    cmd = ['say', '-v', voice, '-o', aiff_path, text]
    subprocess.run(cmd, check=True)
    
    # ffmpeg으로 MP3 변환 (설치되어 있는 경우)
    try:
        subprocess.run([
            'ffmpeg', '-i', aiff_path, '-acodec', 'libmp3lame', 
            '-ab', '128k', '-y', output_path
        ], check=True, capture_output=True)
        os.remove(aiff_path)
    except FileNotFoundError:
        print(f"  ⚠️ ffmpeg 없음. AIFF 파일로 저장: {aiff_path}")
        return aiff_path
    
    return output_path

def tts_gtts(text, output_path):
    """Google TTS (gTTS) 사용 - 무료, 인터넷 필요"""
    try:
        from gtts import gTTS
    except ImportError:
        print("gTTS가 설치되지 않았습니다. pip install gtts 실행 후 다시 시도하세요.")
        return None
    
    # 텍스트가 너무 길면 분할
    max_len = 5000
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    
    if len(chunks) == 1:
        tts = gTTS(text=text, lang='ko')
        tts.save(output_path)
    else:
        # 여러 청크를 합치기
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        
        for i, chunk in enumerate(chunks):
            temp_path = f"{output_path}.part{i}.mp3"
            tts = gTTS(text=chunk, lang='ko')
            tts.save(temp_path)
            combined += AudioSegment.from_mp3(temp_path)
            os.remove(temp_path)
        
        combined.export(output_path, format="mp3")
    
    return output_path

def tts_google_cloud(text, output_path):
    """Google Cloud TTS 사용 - 고품질, API 키 필요"""
    try:
        from google.cloud import texttospeech
    except ImportError:
        print("google-cloud-texttospeech가 설치되지 않았습니다.")
        return None
    
    client = texttospeech.TextToSpeechClient()
    
    # 텍스트가 너무 길면 분할 (5000바이트 제한)
    max_bytes = 4500
    chunks = []
    current_chunk = ""
    
    for sentence in text.split('.'):
        if len((current_chunk + sentence + '.').encode('utf-8')) < max_bytes:
            current_chunk += sentence + '.'
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence + '.'
    if current_chunk:
        chunks.append(current_chunk)
    
    audio_contents = []
    
    for chunk in chunks:
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Wavenet-A",  # 여성 음성
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        audio_contents.append(response.audio_content)
    
    # 오디오 합치기
    with open(output_path, 'wb') as out:
        for content in audio_contents:
            out.write(content)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='마크다운을 오디오북으로 변환')
    parser.add_argument('--provider', choices=['macos', 'gtts', 'google'], 
                        default='macos', help='TTS 제공자 선택')
    parser.add_argument('--output', default='audiobook', help='출력 폴더명')
    parser.add_argument('--chapter', type=int, help='특정 챕터만 변환 (0-15)')
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    md_dir = script_dir / '수정본'
    output_dir = script_dir / args.output
    output_dir.mkdir(exist_ok=True)
    
    # TTS 함수 선택
    tts_func = {
        'macos': tts_macos,
        'gtts': tts_gtts,
        'google': tts_google_cloud,
    }[args.provider]
    
    chapters_to_process = [CHAPTERS[args.chapter]] if args.chapter is not None else CHAPTERS
    
    print(f"🎙️ 오디오북 생성 시작 (TTS: {args.provider})")
    print(f"📁 출력 폴더: {output_dir}")
    print("-" * 50)
    
    for filename, output_name in chapters_to_process:
        md_path = md_dir / filename
        output_path = output_dir / f"{output_name}.mp3"
        
        if not md_path.exists():
            print(f"⚠️ 파일 없음: {filename}")
            continue
        
        print(f"📖 처리 중: {filename}")
        
        # 마크다운 읽기 및 정리
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        text = clean_markdown(md_content)
        print(f"   텍스트 길이: {len(text)} 자")
        
        # TTS 변환
        try:
            if args.provider == 'macos':
                result = tts_func(text, str(output_path))
            else:
                result = tts_func(text, str(output_path))
            
            if result:
                print(f"   ✅ 완료: {result}")
            else:
                print(f"   ❌ 실패")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("-" * 50)
    print(f"🎉 오디오북 생성 완료!")
    print(f"📁 파일 위치: {output_dir}")

if __name__ == "__main__":
    main()
