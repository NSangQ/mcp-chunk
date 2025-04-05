# C++ Code Chunker

LangChain을 사용하여 C++ 코드를 청킹하고 임베딩하는 도구입니다.

## 설치 방법

1. Python 3.8 이상이 필요합니다.
2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```
3. OpenAI API 키 설정:
   - `.env.example` 파일을 `.env`로 복사
   - `.env` 파일에서 `OPENAI_API_KEY`를 실제 API 키로 설정

## 사용 방법

### 단일 파일 처리
1. 코드 청킹만 수행:
```bash
python cpp_chunker.py
```

2. 코드 청킹 및 임베딩:
```bash
python embedder.py
```

### 프로젝트 전체 처리
1. 코드 청킹만 수행:
```bash
python cpp_chunker.py --project-dir /path/to/project
```

2. 코드 청킹 및 임베딩:
```bash
python embedder.py --project-dir /path/to/project
```

#### 추가 옵션
- `--output-dir`: 결과를 저장할 디렉토리 경로 (기본값: 프로젝트 디렉토리 내 chunks_타임스탬프)
- `--chunk-size`: 각 청크의 최대 크기 (기본값: 1000)
- `--chunk-overlap`: 청크 간 중복 크기 (기본값: 200)
- `--db-dir`: Chroma DB 저장 디렉토리 (기본값: code_chunks_db)

## 기능

- C++ 코드를 의미 있는 단위로 청킹
- OpenAI의 text-embedding-3-small 모델을 사용한 코드 임베딩
- Chroma DB를 사용한 벡터 저장소 구현
- 단일 파일 또는 프로젝트 전체 처리 지원
- 헤더 파일만 있는 경우도 처리 가능
- 청크 크기와 중복 크기 조절 가능
- UTF-8 인코딩 지원
- 결과를 JSON 형식으로 저장
- 처리 결과 요약 제공

## 출력 형식

각 C++ 파일에 대해 다음 정보가 JSON 형식으로 저장됩니다:
- 헤더 파일 경로
- 소스 파일 경로 (헤더만 있는 경우 None)
- 파일 타입 ('header_only' 또는 'header_and_source')
- 청킹된 코드 조각들

임베딩된 코드는 Chroma DB에 저장되며, 다음 메타데이터와 함께 저장됩니다:
- 파일 이름
- 프로그래밍 언어
- 청크 크기
- 청크 중복 크기
- 소스 파일 정보

## 파일 타입

1. 헤더+소스 파일 (header_and_source)
   - 헤더 파일(.h)과 소스 파일(.cpp)이 모두 존재하는 경우
   - 두 파일의 내용을 인라인화하여 청킹

2. 헤더만 있는 파일 (header_only)
   - 헤더 파일(.h)만 존재하고 소스 파일(.cpp)이 없는 경우
   - 헤더 파일의 내용만 청킹

## 설정

`chunk_cpp_code` 함수에서 다음 매개변수를 조정할 수 있습니다:
- `chunk_size`: 각 청크의 최대 크기 (기본값: 1000)
- `chunk_overlap`: 청크 간 중복 크기 (기본값: 200)

## 임베딩 설정

`CodeEmbedder` 클래스에서 다음 설정을 조정할 수 있습니다:
- `persist_directory`: Chroma DB 저장 위치
- `model`: 임베딩 모델 (기본값: text-embedding-3-small) 