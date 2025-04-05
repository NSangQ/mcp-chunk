import os
import re

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

def inline_cpp_files(header_path, cpp_path, output_path):
    """
    헤더 파일과 소스 파일을 하나의 파일로 인라인화합니다.
    
    Args:
        header_path (str): 헤더 파일 경로
        cpp_path (str): 소스 파일 경로
        output_path (str): 출력 파일 경로
    """
    # 파일 읽기
    with open(header_path, 'r', encoding='utf-8') as f:
        header_content = f.read()
    
    with open(cpp_path, 'r', encoding='utf-8') as f:
        cpp_content = f.read()
    
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
    
    # 파일 작성
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(inline_content))

def main():
    # 현재 디렉토리 기준 파일 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    header_file = os.path.join(current_dir, "student.h")
    cpp_file = os.path.join(current_dir, "student.cpp")
    output_file = os.path.join(current_dir, "student_inlined.cpp")
    
    if os.path.exists(header_file) and os.path.exists(cpp_file):
        inline_cpp_files(header_file, cpp_file, output_file)
        print(f"인라인화 완료: {output_file}")
    else:
        print("헤더 파일 또는 소스 파일을 찾을 수 없습니다.")
        print(f"찾는 파일 경로:")
        print(f"헤더: {header_file}")
        print(f"소스: {cpp_file}")

if __name__ == "__main__":
    main() 