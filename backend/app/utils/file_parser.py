"""
FileParseTool
textPDF、Markdown、TXTFiletext
"""

import os
from pathlib import Path
from typing import List, Optional


def _read_text_with_fallback(file_path: str) -> str:
    """
    ReadtextFile，UTF-8FailtextEncoding。
    
    text：
    1. text UTF-8 Decode
    2. text charset_normalizer textEncoding
    3. text chardet textEncoding
    4. text UTF-8 + errors='replace' text
    
    Args:
        file_path: FilePath
        
    Returns:
        DecodetextContent
    """
    data = Path(file_path).read_bytes()
    
    # text UTF-8
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # text charset_normalizer textEncoding
    encoding = None
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data).best()
        if best and best.encoding:
            encoding = best.encoding
    except Exception:
        pass
    
    # text chardet
    if not encoding:
        try:
            import chardet
            result = chardet.detect(data)
            encoding = result.get('encoding') if result else None
        except Exception:
            pass
    
    # text：text UTF-8 + replace
    if not encoding:
        encoding = 'utf-8'
    
    return data.decode(encoding, errors='replace')


class FileParser:
    """FileParsetext"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt'}
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        textFiletext
        
        Args:
            file_path: FilePath
            
        Returns:
            textContent
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Filetext: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"textFileFormat: {suffix}")
        
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.md', '.markdown'}:
            return cls._extract_from_md(file_path)
        elif suffix == '.txt':
            return cls._extract_from_txt(file_path)
        
        raise ValueError(f"textProcessing/HandletextFileFormat: {suffix}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """textPDFtext"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("textPyMuPDF: pip install PyMuPDF")
        
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        """textMarkdowntext，textEncodingtext"""
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """textTXTtext，textEncodingtext"""
        return _read_text_with_fallback(file_path)
    
    @classmethod
    def extract_from_multiple(cls, file_paths: List[str]) -> str:
        """
        textFiletextMerge
        
        Args:
            file_paths: FilePathList
            
        Returns:
            Mergetext
        """
        all_texts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                text = cls.extract_text(file_path)
                filename = Path(file_path).name
                all_texts.append(f"=== Documentation {i}: {filename} ===\n{text}")
            except Exception as e:
                all_texts.append(f"=== Documentation {i}: {file_path} (textFail: {str(e)}) ===")
        
        return "\n\n".join(all_texts)


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[str]:
    """
    textSplittext
    
    Args:
        text: text
        chunk_size: textChartext
        overlap: textChartext
        
    Returns:
        textList
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # textEdgetextSplit
        if end < len(text):
            # Querytext
            for sep in ['。', '！', '？', '.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # text
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

