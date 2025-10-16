import os
import re
import fitz
import pytesseract
from PIL import Image
import cv2
import numpy as np
from google.cloud import vision
import magic
import json
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentClassifier:
    """
    Enhanced document classifier with OCR support for Indonesian legal documents.
    Combines filename-based classification with content analysis using OCR.
    """

    def __init__(self, use_google_vision=False):
        self.use_google_vision = use_google_vision

        # Initialize Google Vision client if enabled
        if use_google_vision:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Vision API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Vision: {e}")
                self.use_google_vision = False

        # Document categories with keywords for content-based classification
        self.document_categories = {
            'Akta dan SK Kemenkumham': {
                'keywords': [
                    'akta pendirian', 'akta perubahan', 'kemenkumham', 'sk',
                    'surat keputusan', 'pengesahan', 'notaris', 'akta notaris',
                    'anggaran dasar', 'ad/art', 'perubahan anggaran dasar'
                ],
                'patterns': [
                    r'akta.*pendirian',
                    r'surat.*keputusan.*kemenkumham',
                    r'pengesahan.*kemenkumham',
                    r'notaris.*nomor'
                ]
            },
            'NIB dan NPWP': {
                'keywords': [
                    'nib', 'nomor induk berusaha', 'npwp', 'nomor pokok wajib pajak',
                    'wajib pajak', 'pkp', 'pengusaha kena pajak', 'nib perusahaan'
                ],
                'patterns': [
                    r'nib\s*:?\s*\d+',
                    r'npwp\s*:?\s*[\d.]+',
                    r'nomor.*induk.*usaha',
                    r'nomor.*pokok.*wajib.*pajak'
                ]
            },
            'KTP Pengurus': {
                'keywords': [
                    'ktp', 'kartu tanda penduduk', 'nik', 'nomor induk kependudukan',
                    'identitas', 'direktur', 'komisaris', 'pengurus'
                ],
                'patterns': [
                    r'nik\s*:?\s*[\d-]+',
                    r'kartu.*tanda.*penduduk',
                    r'ktp.*direktur',
                    r'identitas.*pengurus'
                ]
            },
            'Laporan Keuangan': {
                'keywords': [
                    'laporan keuangan', 'neraca', 'laba rugi', 'spt', 'surat pemberitahuan tahunan',
                    'mutasi rekening', 'laporan audit', 'audited', 'tahun buku',
                    'balance sheet', 'income statement', 'cash flow'
                ],
                'patterns': [
                    r'laporan.*keuangan',
                    r'neraca.*per.*\d{4}',
                    r'laba.*rugi',
                    r'spt.*tahunan',
                    r'mutasi.*rekening'
                ]
            },
            'Dokumen Lainnya': {
                'keywords': [],
                'patterns': []
            }
        }

        # File type categories
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        self.pdf_extensions = {'.pdf'}
        self.office_extensions = {'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract or Google Vision API."""
        try:
            if self.use_google_vision:
                return self._extract_text_google_vision(image_path)
            else:
                return self._extract_text_tesseract(image_path)
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return ""

    def _extract_text_tesseract(self, image_path: str) -> str:
        """Extract text using Tesseract OCR."""
        try:
            # Preprocess image for better OCR accuracy
            image = cv2.imread(image_path)
            if image is None:
                return ""

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Noise removal
            kernel = np.ones((1,1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Perform OCR
            custom_config = r'--oem 3 --psm 6 -l ind+eng'
            text = pytesseract.image_to_string(processed, config=custom_config)

            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    def _extract_text_google_vision(self, image_path: str) -> str:
        """Extract text using Google Vision API."""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.vision_client.document_text_detection(image=image)

            if response.error.message:
                logger.error(f"Google Vision API error: {response.error.message}")
                return ""

            return response.full_text_annotation.text
        except Exception as e:
            logger.error(f"Google Vision API failed: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""

    def extract_text_from_document(self, file_path: str) -> str:
        """Extract text from various document types."""
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext in self.image_extensions:
                return self.extract_text_from_image(file_path)
            elif file_ext in self.pdf_extensions:
                return self.extract_text_from_pdf(file_path)
            elif file_ext in self.office_extensions:
                # For Office documents, try to extract text if possible
                # This is a simplified approach - you might want to use python-docx, openpyxl etc.
                logger.warning(f"Office document text extraction not fully implemented: {file_path}")
                return ""
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return ""

    def classify_by_content(self, text: str, filename: str = "") -> Dict:
        """Classify document based on content analysis."""
        if not text:
            return {
                'category': 'Dokumen Lainnya',
                'confidence': 0.0,
                'reason': 'No text extracted',
                'method': 'content_analysis'
            }

        text_lower = text.lower()
        scores = {}

        for category, config in self.document_categories.items():
            if category == 'Dokumen Lainnya':
                continue

            score = 0
            keyword_matches = []
            pattern_matches = []

            # Check keyword matches
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 1
                    keyword_matches.append(keyword)

            # Check pattern matches
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    score += 2  # Give more weight to pattern matches
                    pattern_matches.append(pattern)

            if score > 0:
                scores[category] = {
                    'score': score,
                    'keywords': keyword_matches,
                    'patterns': pattern_matches
                }

        # Determine best match
        if scores:
            best_category = max(scores.keys(), key=lambda k: scores[k]['score'])
            confidence = min(scores[best_category]['score'] / 5.0, 1.0)  # Normalize to 0-1

            return {
                'category': best_category,
                'confidence': confidence,
                'reason': f"Matched keywords: {', '.join(scores[best_category]['keywords'])}",
                'method': 'content_analysis',
                'details': scores[best_category]
            }
        else:
            return {
                'category': 'Dokumen Lainnya',
                'confidence': 0.0,
                'reason': 'No matching keywords found',
                'method': 'content_analysis'
            }

    def classify_by_filename(self, filename: str) -> Dict:
        """Classify document based on filename (fallback method)."""
        filename_lower = filename.lower()

        # Filename patterns for each category
        filename_patterns = {
            'Akta dan SK Kemenkumham': [
                r'akta.*pendirian', r'akta.*perubahan', r'sk.*kemenkumham',
                r'pengesahan.*kemenkumham', r'notaris'
            ],
            'NIB dan NPWP': [
                r'nib', r'npwp', r'nomor.*induk.*usaha', r'nomor.*pokok.*wajib.*pajak'
            ],
            'KTP Pengurus': [
                r'ktp.*pengurus', r'ktp.*direktur', r'identitas.*pengurus'
            ],
            'Laporan Keuangan': [
                r'laporan.*keuangan', r'neraca', r'laba.*rugi', r'spt.*tahunan',
                r'mutasi.*rekening', r'audit'
            ]
        }

        for category, patterns in filename_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return {
                        'category': category,
                        'confidence': 0.7,  # Medium confidence for filename-based
                        'reason': f"Filename pattern matched: {pattern}",
                        'method': 'filename_analysis'
                    }

        return {
            'category': 'Dokumen Lainnya',
            'confidence': 0.3,
            'reason': 'No filename pattern matched',
            'method': 'filename_analysis'
        }

    def classify_document(self, file_path: str) -> Dict:
        """
        Main classification method that combines content and filename analysis.
        """
        try:
            filename = os.path.basename(file_path)

            # First try content-based classification
            text = self.extract_text_from_document(file_path)
            content_result = self.classify_by_content(text, filename)

            # If content analysis has low confidence, also check filename
            if content_result['confidence'] < 0.5:
                filename_result = self.classify_by_filename(filename)

                # Choose the result with higher confidence
                if filename_result['confidence'] > content_result['confidence']:
                    final_result = filename_result
                    final_result['fallback_method'] = 'filename_analysis'
                else:
                    final_result = content_result
                    final_result['fallback_method'] = None
            else:
                final_result = content_result
                final_result['fallback_method'] = None

            # Add additional metadata
            final_result.update({
                'file_path': file_path,
                'filename': filename,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'text_length': len(text) if text else 0,
                'classification_timestamp': self._get_timestamp()
            })

            return final_result

        except Exception as e:
            logger.error(f"Error classifying document {file_path}: {e}")
            return {
                'category': 'Dokumen Lainnya',
                'confidence': 0.0,
                'reason': f'Classification error: {str(e)}',
                'method': 'error',
                'file_path': file_path,
                'filename': os.path.basename(file_path)
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def batch_classify(self, file_paths: List[str]) -> List[Dict]:
        """Classify multiple documents."""
        results = []

        for file_path in file_paths:
            logger.info(f"Classifying: {file_path}")
            result = self.classify_document(file_path)
            results.append(result)

        return results

    def get_classification_summary(self, results: List[Dict]) -> Dict:
        """Get summary statistics for classification results."""
        categories = {}
        confidences = []

        for result in results:
            category = result['category']
            confidence = result['confidence']

            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            confidences.append(confidence)

        return {
            'total_documents': len(results),
            'categories': categories,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'classification_methods': list(set(r['method'] for r in results))
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize classifier
    classifier = DocumentClassifier(use_google_vision=False)

    # Test classification
    test_file = "example_document.pdf"
    if os.path.exists(test_file):
        result = classifier.classify_document(test_file)
        print(f"Classification result: {json.dumps(result, indent=2)}")
    else:
        print(f"Test file {test_file} not found")