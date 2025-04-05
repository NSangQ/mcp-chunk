from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re
from pathlib import Path
import json
from datetime import datetime

def extract_includes(content):
    """헤더 파일에서 include 문을 추출합니다."""
    includes = []
    for line in content.split('\n'):
        if line.strip().startswith('#include'):
            includes.append(line.strip())
    return includes

def extract_class_declaration(content):
    """클래스 선언부를 추출합니다."""
    class_pattern = r'class\s+\w+\s*{[^}]*}'
    matches = re.finditer(class_pattern, content, re.DOTALL)
    return [match.group(0) for match in matches]

def inline_cpp_content(header_content, cpp_content):
    """
    헤더와 소스 파일 내용을 인라인화합니다.
    
    Args:
        header_content (str): 헤더 파일 내용
        cpp_content (str): 소스 파일 내용
    
    Returns:
        str: 인라인화된 코드
    """
    # 헤더의 include 문 추출
    includes = extract_includes(header_content)
    
    # 클래스 선언 추출
    class_declarations = extract_class_declaration(header_content)
    
    # 인라인화된 내용 생성
    inline_content = []
    
    # 1. include 문 추가
    inline_content.extend(includes)
    inline_content.append('')
    
    # 2. 클래스 선언 추가
    for decl in class_declarations:
        inline_content.append(decl)
        inline_content.append('')
    
    # 3. 구현부 추가 (include 문 제외)
    cpp_lines = cpp_content.split('\n')
    for line in cpp_lines:
        if not line.strip().startswith('#include'):
            inline_content.append(line)
    
    return '\n'.join(inline_content)

def chunk_cpp_code(cpp_name, chunk_size=1000, chunk_overlap=200):
    """
    C++ 코드를 인라인화하고 청킹하는 함수
    
    Args:
        cpp_name (str): C++ 파일 이름 (확장자 제외)
        chunk_size (int): 각 청크의 최대 크기
        chunk_overlap (int): 청크 간 중복 크기
    
    Returns:
        list: 청킹된 코드 조각들
    """
    # 현재 디렉토리 기준 파일 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    header_path = os.path.join(current_dir, f"{cpp_name}.h")
    cpp_path = os.path.join(current_dir, f"{cpp_name}.cpp")
    
    # 파일 읽기
    with open(header_path, 'r', encoding='utf-8') as f:
        header_content = f.read()
    
    with open(cpp_path, 'r', encoding='utf-8') as f:
        cpp_content = f.read()
    
    # 인라인화
    inlined_code = inline_cpp_content(header_content, cpp_content)
    
    # C++ 코드에 특화된 텍스트 스플리터 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",  # 함수/클래스 간 구분
            "};",    # 클래스 정의 끝
            ") {",   # 함수 정의 시작
            "\n",    # 일반 줄바꿈
            " ",     # 단어 구분
            ""
        ],
        keep_separator=True,
    )
    
    # 코드 청킹
    chunks = text_splitter.split_text(inlined_code)
    return chunks

def find_cpp_files(project_dir):
    """
    프로젝트 디렉토리에서 모든 C++ 파일을 찾습니다.
    
    Args:
        project_dir (str): 프로젝트 루트 디렉토리 경로
    
    Returns:
        list: (header_path, cpp_path) 튜플의 리스트. cpp_path는 None일 수 있음
    """
    cpp_files = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.h'):
                header_path = os.path.join(root, file)
                cpp_path = os.path.join(root, file[:-2] + '.cpp')
                if os.path.exists(cpp_path):
                    cpp_files.append((header_path, cpp_path))
                else:
                    # 헤더 파일만 있는 경우
                    cpp_files.append((header_path, None))
    return cpp_files

def process_project(project_dir, output_dir=None, chunk_size=1000, chunk_overlap=200):
    """
    프로젝트의 모든 C++ 파일을 처리합니다.
    
    Args:
        project_dir (str): 프로젝트 루트 디렉토리 경로
        output_dir (str): 결과를 저장할 디렉토리 경로 (기본값: None)
        chunk_size (int): 각 청크의 최대 크기
        chunk_overlap (int): 청크 간 중복 크기
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_dir, f"chunks_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    cpp_files = find_cpp_files(project_dir)
    results = {}
    
    for header_path, cpp_path in cpp_files:
        try:
            # 파일 읽기
            with open(header_path, 'r', encoding='utf-8') as f:
                header_content = f.read()
            
            # 헤더 파일만 있는 경우
            if cpp_path is None:
                # 헤더 파일만 청킹
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=[
                        "\n\n",  # 함수/클래스 간 구분
                        "};",    # 클래스 정의 끝
                        ") {",   # 함수 정의 시작
                        "\n",    # 일반 줄바꿈
                        " ",     # 단어 구분
                        ""
                    ],
                    keep_separator=True,
                )
                chunks = text_splitter.split_text(header_content)
                
                # 결과 저장
                file_name = os.path.basename(header_path)[:-2]  # .h 제거
                results[file_name] = {
                    'header_path': header_path,
                    'cpp_path': None,
                    'chunks': chunks,
                    'type': 'header_only'
                }
                
                # 개별 파일로 저장
                output_file = os.path.join(output_dir, f"{file_name}_chunks.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'header_path': header_path,
                        'cpp_path': None,
                        'chunks': chunks,
                        'type': 'header_only'
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"처리 완료 (헤더만): {file_name} ({len(chunks)} 청크)")
                continue
            
            # 헤더와 소스 파일이 모두 있는 경우
            with open(cpp_path, 'r', encoding='utf-8') as f:
                cpp_content = f.read()
            
            # 인라인화
            inlined_code = inline_cpp_content(header_content, cpp_content)
            
            # C++ 코드에 특화된 텍스트 스플리터 설정
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=[
                    "\n\n",  # 함수/클래스 간 구분
                    "};",    # 클래스 정의 끝
                    ") {",   # 함수 정의 시작
                    "\n",    # 일반 줄바꿈
                    " ",     # 단어 구분
                    ""
                ],
                keep_separator=True,
            )
            
            # 코드 청킹
            chunks = text_splitter.split_text(inlined_code)
            
            # 결과 저장
            file_name = os.path.basename(header_path)[:-2]  # .h 제거
            results[file_name] = {
                'header_path': header_path,
                'cpp_path': cpp_path,
                'chunks': chunks,
                'type': 'header_and_source'
            }
            
            # 개별 파일로 저장
            output_file = os.path.join(output_dir, f"{file_name}_chunks.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'header_path': header_path,
                    'cpp_path': cpp_path,
                    'chunks': chunks,
                    'type': 'header_and_source'
                }, f, ensure_ascii=False, indent=2)
            
            print(f"처리 완료 (헤더+소스): {file_name} ({len(chunks)} 청크)")
            
        except Exception as e:
            print(f"오류 발생 ({file_name}): {str(e)}")
    
    # 전체 결과 저장
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'project_dir': project_dir,
            'processed_files': len(cpp_files),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n처리 완료: 총 {len(cpp_files)}개 파일")
    print(f"결과 저장 위치: {output_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='C++ 코드 청킹 도구')
    parser.add_argument('--project-dir', type=str, help='프로젝트 루트 디렉토리 경로')
    parser.add_argument('--output-dir', type=str, help='결과를 저장할 디렉토리 경로')
    parser.add_argument('--chunk-size', type=int, default=1000, help='각 청크의 최대 크기')
    parser.add_argument('--chunk-overlap', type=int, default=200, help='청크 간 중복 크기')
    
    args = parser.parse_args()
    
    if args.project_dir:
        process_project(
            args.project_dir,
            args.output_dir,
            args.chunk_size,
            args.chunk_overlap
        )
    else:
        # 기존 단일 파일 처리 로직
        cpp_name = "student"
        try:
            chunks = chunk_cpp_code(cpp_name)
            print(f"\n=== 총 {len(chunks)}개의 청크로 분할됨 ===\n")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"\n=== 청크 {i} ===")
                print(chunk)
                print("\n" + "="*50)
        except FileNotFoundError as e:
            print(f"오류: {cpp_name}.h 또는 {cpp_name}.cpp 파일을 찾을 수 없습니다.")
            print(f"현재 디렉토리: {os.path.dirname(os.path.abspath(__file__))}")

if __name__ == "__main__":
    main() 