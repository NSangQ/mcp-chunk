import os
import argparse
from typing import List, Dict, Union
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# .env 파일에서 환경 변수 로드
load_dotenv()

class CodeRetriever:
    def __init__(self, persist_directory: str = "code_chunks_db"):
        """
        코드 리트리버 초기화
        
        Args:
            persist_directory (str): Chroma DB 저장 디렉토리
        """
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.persist_directory = persist_directory
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_dict: Dict = None
    ) -> List[Dict[str, Union[str, Dict]]]:
        """
        유사도 기반 코드 검색
        
        Args:
            query (str): 검색 쿼리
            k (int): 반환할 결과 수
            filter_dict (Dict): 메타데이터 기반 필터 (예: {"language": "cpp"})
        
        Returns:
            List[Dict]: 검색 결과 리스트. 각 결과는 코드와 메타데이터를 포함
        """
        docs = self.db.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        results = []
        for doc in docs:
            results.append({
                "code": doc.page_content,
                "metadata": doc.metadata
            })
        
        return results

    def search_by_metadata(
        self,
        metadata_filter: Dict,
        limit: int = 10
    ) -> List[Dict[str, Union[str, Dict]]]:
        """
        메타데이터 기반 코드 검색
        
        Args:
            metadata_filter (Dict): 메타데이터 필터 (예: {"file_name": "student"})
            limit (int): 반환할 최대 결과 수
        
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        results = []
        collection = self.db._collection
        
        docs = collection.get(
            where=metadata_filter,
            limit=limit
        )
        
        for i, doc in enumerate(docs["documents"]):
            results.append({
                "code": doc,
                "metadata": docs["metadatas"][i]
            })
        
        return results

    def get_similar_code(
        self,
        code_snippet: str,
        k: int = 3,
        filter_dict: Dict = None
    ) -> List[Dict[str, Union[str, Dict]]]:
        """
        주어진 코드 스니펫과 유사한 코드 검색
        
        Args:
            code_snippet (str): 코드 스니펫
            k (int): 반환할 결과 수
            filter_dict (Dict): 메타데이터 기반 필터
        
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        return self.similarity_search(code_snippet, k, filter_dict)

def main():
    parser = argparse.ArgumentParser(description='Chroma DB에서 코드 검색')
    parser.add_argument('--query', type=str, help='검색 쿼리')
    parser.add_argument('--db-dir', type=str, default='code_chunks_db',
                      help='Chroma DB 디렉토리 (기본값: code_chunks_db)')
    parser.add_argument('--k', type=int, default=3,
                      help='반환할 결과 수 (기본값: 3)')
    parser.add_argument('--file-name', type=str, help='특정 파일 이름으로 필터링')
    
    args = parser.parse_args()

    # 환경 변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("'.env' 파일을 생성하고 OPENAI_API_KEY를 설정해주세요.")
        return

    # CodeRetriever 인스턴스 생성
    retriever = CodeRetriever(persist_directory=args.db_dir)

    if args.query:
        # 파일 이름 필터 설정
        filter_dict = {"file_name": args.file_name} if args.file_name else None
        
        # 유사도 검색 수행
        results = retriever.similarity_search(
            query=args.query,
            k=args.k,
            filter_dict=filter_dict
        )
        
        # 결과 출력
        print(f"\n검색 쿼리: {args.query}")
        print(f"검색 결과 ({len(results)}개):\n")
        
        for i, result in enumerate(results, 1):
            print(f"=== 결과 {i} ===")
            print(f"파일: {result['metadata'].get('file_name', 'N/A')}")
            print("코드:")
            print(result['code'])
            print()
    
    else:
        print("검색 쿼리를 입력해주세요. (--query 옵션 사용)")
        print("예시: python retriever.py --query '학생 정보를 출력하는 함수'")

if __name__ == "__main__":
    main() 