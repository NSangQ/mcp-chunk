import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from cpp_chunker import chunk_cpp_code, process_project

# .env 파일에서 환경 변수 로드
load_dotenv()

class CodeEmbedder:
    def __init__(self, persist_directory: str = "code_chunks_db"):
        """
        코드 임베더 초기화
        
        Args:
            persist_directory (str): Chroma DB 저장 디렉토리
        """
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.persist_directory = persist_directory
        self.db = None

    def initialize_db(self):
        """Chroma DB 초기화"""
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def embed_and_store_chunks(self, chunks: List[str], metadata: Dict = None) -> None:
        """
        코드 청크들을 임베딩하고 Chroma DB에 저장
        
        Args:
            chunks (List[str]): 코드 청크 리스트
            metadata (Dict): 각 청크에 대한 메타데이터 (선택사항)
        """
        if self.db is None:
            self.initialize_db()

        # 각 청크에 대한 메타데이터 생성
        metadatas = []
        if metadata:
            metadatas = [metadata for _ in chunks]
        else:
            metadatas = [{"source": "code_chunk"} for _ in chunks]

        # Chroma DB에 저장
        self.db.add_texts(
            texts=chunks,
            metadatas=metadatas
        )
        
        # 변경사항 저장
        self.db.persist()

    def embed_cpp_file(self, cpp_name: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        C++ 파일을 청킹하고 임베딩하여 저장
        
        Args:
            cpp_name (str): C++ 파일 이름 (확장자 제외)
            chunk_size (int): 각 청크의 최대 크기
            chunk_overlap (int): 청크 간 중복 크기
        """
        # 코드 청킹
        chunks = chunk_cpp_code(cpp_name, chunk_size, chunk_overlap)
        
        # 메타데이터 설정
        metadata = {
            "file_name": cpp_name,
            "language": "cpp",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        
        # 임베딩 및 저장
        self.embed_and_store_chunks(chunks, metadata)

    def embed_project(self, project_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        프로젝트 전체를 청킹하고 임베딩하여 저장
        
        Args:
            project_dir (str): 프로젝트 디렉토리 경로
            chunk_size (int): 각 청크의 최대 크기
            chunk_overlap (int): 청크 간 중복 크기
        """
        # 프로젝트 청킹
        chunks_dir = os.path.join(project_dir, "chunks")
        process_project(project_dir, chunks_dir, chunk_size, chunk_overlap)
        
        # 청크 파일들 처리
        for root, _, files in os.walk(chunks_dir):
            for file in files:
                if file.endswith("_chunks.json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        chunks = data["chunks"]
                        metadata = {
                            "file_name": file[:-12],  # _chunks.json 제거
                            "language": "cpp",
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap,
                            "header_path": data["header_path"],
                            "cpp_path": data["cpp_path"],
                            "type": data["type"]
                        }
                        self.embed_and_store_chunks(chunks, metadata)

def main():
    # 환경 변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("'.env' 파일을 생성하고 OPENAI_API_KEY를 설정해주세요.")
        return

    # CodeEmbedder 인스턴스 생성
    embedder = CodeEmbedder()

    # 예제 파일 임베딩
    embedder.embed_cpp_file("student")
    print("student.cpp 파일의 임베딩이 완료되었습니다.")

if __name__ == "__main__":
    main() 