"""
textProcessing/HandleService
"""

from typing import List, Optional
from ..utils.file_parser import FileParser, split_text_into_chunks


class TextProcessor:
    """textProcessing/Handletext"""
    
    @staticmethod
    def extract_from_files(file_paths: List[str]) -> str:
        """textFiletext"""
        return FileParser.extract_from_multiple(file_paths)
    
    @staticmethod
    def split_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Splittext
        
        Args:
            text: text
            chunk_size: text
            overlap: text
            
        Returns:
            textList
        """
        return split_text_into_chunks(text, chunk_size, overlap)
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        textProcessing/Handletext
        - Removetext
        - text
        
        Args:
            text: text
            
        Returns:
            Processing/Handletext
        """
        import re
        
        # text
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Removetext（text）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Removetext
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def get_text_stats(text: str) -> dict:
        """GettextStatisticsInformation"""
        return {
            "total_chars": len(text),
            "total_lines": text.count('\n') + 1,
            "total_words": len(text.split()),
        }

