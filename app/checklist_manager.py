"""
Checklist Evaluation System
Manages document checklist templates and evaluates document completeness
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import re
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)

class ChecklistManager:
    """
    Manages document checklist evaluation with flexible template support
    """

    def __init__(self, config):
        self.config = config
        self.checklist_templates = config.CHECKLIST_TEMPLATES
        self.document_categories = config.DOCUMENT_CATEGORIES

        # Document mapping for better matching
        self.category_mappings = {
            # Main categories to specific checklist items
            "Akta dan SK Kemenkumham": [
                "Akta dan SK Kemenkumham Pendirian Hingga Perubahan Terakhir",
                "Akta + SK Pendirian",
                "Akta + SK Perubahan"
            ],
            "NIB dan NPWP": [
                "NIB Perusahaan",
                "NPWP Perusahaan",
                "NIB",
                "NPWP Perusahaan"
            ],
            "KTP Pengurus": [
                "KTP NPWP Pengurus",
                "KTP Pengurus",
                "NPWP Pengurus",
                "Nomor Telepon Direktur dan Nama Ibu Kandung"
            ],
            "Laporan Keuangan": [
                "Laporan Keuangan 2 Tahun",
                "Neraca Laba Rugi / SPT Tahun 2024",
                "Laporan Keuangan 2023 (Audited jika ada)",
                "Mutasi Rekening 2024 Full",
                "Mutasi Rekening 2025 (Jan-Jul)"
            ],
            "Dokumen Lainnya": [
                "Kop Surat dan Stempel Perusahaan",
                "Kop Surat",
                "Contoh Stempel",
                "SKT / SKF (Fiskal)",
                "SK PIHK / SK PPIU",
                "Sertifikat Akreditasi PPIU",
                "Lampiran Manifest 1000 Jamaah (Untuk PPIU < 3 Tahun)",
                "Rekom / SK PPIU",
                "Foto Kantor (Interior, Eksterior, Aktivitas, Logo)",
                "Sampling Invoice Hotel & Tiket Jamaah 2024",
                "Nomor Meteran Listrik Kantor"
            ]
        }

    def fuzzy_match_document(self, available_categories: List[str], required_doc: str) -> Tuple[bool, float, str]:
        """
        Use fuzzy matching to find if a required document is available
        Returns: (is_match, confidence_score, matched_category)
        """
        best_match = None
        best_score = 0
        best_category = None

        for category in available_categories:
            # Direct string matching
            direct_score = fuzz.ratio(required_doc.lower(), category.lower())
            if direct_score > best_score:
                best_score = direct_score
                best_match = required_doc
                best_category = category

            # Partial matching
            partial_score = fuzz.partial_ratio(required_doc.lower(), category.lower())
            if partial_score > best_score:
                best_score = partial_score
                best_match = required_doc
                best_category = category

            # Token sort matching (good for reordered words)
            token_score = fuzz.token_sort_ratio(required_doc.lower(), category.lower())
            if token_score > best_score:
                best_score = token_score
                best_match = required_doc
                best_category = category

        return (best_score >= 60, best_score / 100.0, best_category or "")

    def evaluate_checklist(self, checklist_type: str, available_documents: List[Dict]) -> Dict:
        """
        Evaluate document completeness against a checklist template

        Args:
            checklist_type: Type of checklist (e.g., "BG PIHK PT")
            available_documents: List of classified document dictionaries

        Returns:
            Dictionary with evaluation results
        """
        if checklist_type not in self.checklist_templates:
            return {
                "error": f"Checklist template '{checklist_type}' not found",
                "available_templates": list(self.checklist_templates.keys())
            }

        template = self.checklist_templates[checklist_type]
        required_docs = template["required_documents"]
        total_required = template["total_required"]

        # Extract available document categories
        available_categories = []
        available_files = []

        for doc in available_documents:
            if isinstance(doc, dict) and 'category' in doc:
                available_categories.append(doc['category'])
                available_files.append(doc)
            elif isinstance(doc, str):
                available_categories.append(doc)
                available_files.append({'category': doc, 'filename': doc})

        # Evaluate each required document
        found_documents = []
        missing_documents = []
        document_matches = {}
        total_confidence = 0
        matched_count = 0

        for required_doc in required_docs:
            is_found, confidence, matched_category = self.fuzzy_match_document(available_categories, required_doc)

            if is_found:
                # Find the actual document(s) that match
                matching_files = [
                    doc for doc in available_files
                    if doc['category'] == matched_category or required_doc.lower() in doc.get('filename', '').lower()
                ]

                found_documents.append({
                    "required": required_doc,
                    "matched_category": matched_category,
                    "confidence": confidence,
                    "files": matching_files[:3]  # Limit to 3 files per requirement
                })

                document_matches[required_doc] = {
                    "found": True,
                    "confidence": confidence,
                    "matched_files": [f.get('filename', f.get('file_path', '')) for f in matching_files]
                }

                total_confidence += confidence
                matched_count += 1
            else:
                missing_documents.append(required_doc)
                document_matches[required_doc] = {
                    "found": False,
                    "confidence": 0.0,
                    "matched_files": []
                }

        # Calculate completion statistics
        completion_percentage = (matched_count / total_required) * 100 if total_required > 0 else 0
        average_confidence = total_confidence / matched_count if matched_count > 0 else 0

        # Determine overall status
        if completion_percentage == 100:
            status = "complete"
            status_message = "🎉 Semua dokumen lengkap!"
        elif completion_percentage >= 80:
            status = "nearly_complete"
            status_message = "📋 Hampir lengkap, hanya beberapa dokumen lagi"
        elif completion_percentage >= 50:
            status = "partial"
            status_message = "📝 Beberapa dokumen sudah tersedia"
        else:
            status = "incomplete"
            status_message = "❌ Masih banyak dokumen yang diperlukan"

        return {
            "checklist_type": checklist_type,
            "checklist_description": template["description"],
            "evaluation_timestamp": datetime.now().isoformat(),
            "total_required": total_required,
            "total_found": matched_count,
            "completion_percentage": round(completion_percentage, 1),
            "average_confidence": round(average_confidence, 2),
            "status": status,
            "status_message": status_message,
            "found_documents": found_documents,
            "missing_documents": missing_documents,
            "document_matches": document_matches,
            "available_categories_count": len(set(available_categories)),
            "available_documents_count": len(available_files)
        }

    def get_best_checklist_match(self, available_documents: List[Dict]) -> Dict:
        """
        Determine the most appropriate checklist template based on available documents
        """
        results = {}

        for checklist_type in self.checklist_templates.keys():
            evaluation = self.evaluate_checklist(checklist_type, available_documents)

            if "error" not in evaluation:
                # Calculate a score for template matching
                score = (
                    evaluation["completion_percentage"] * 0.7 +  # 70% weight on completion
                    evaluation["average_confidence"] * 100 * 0.3  # 30% weight on confidence
                )

                results[checklist_type] = {
                    "score": score,
                    "evaluation": evaluation
                }

        if not results:
            return {
                "recommended_checklist": None,
                "reason": "No suitable checklist template found",
                "all_results": {}
            }

        # Find best match
        best_checklist = max(results.keys(), key=lambda k: results[k]["score"])
        best_score = results[best_checklist]["score"]

        # Determine confidence level
        if best_score >= 80:
            confidence_level = "high"
        elif best_score >= 60:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return {
            "recommended_checklist": best_checklist,
            "confidence_level": confidence_level,
            "score": round(best_score, 1),
            "evaluation": results[best_checklist]["evaluation"],
            "reason": f"Best match with {best_score:.1f}% confidence",
            "all_results": {k: {"score": round(v["score"], 1)} for k, v in results.items()}
        }

    def generate_missing_document_summary(self, evaluation_result: Dict) -> str:
        """
        Generate a human-readable summary of missing documents
        """
        if evaluation_result["status"] == "complete":
            return "✅ Semua dokumen yang diperlukan telah tersedia."

        missing_docs = evaluation_result["missing_documents"]
        if not missing_docs:
            return "✅ Tidak ada dokumen yang hilang."

        summary = f"❌ Dokumen yang belum ditemukan ({len(missing_docs)}):\n"
        for i, doc in enumerate(missing_docs, 1):
            summary += f"{i}. {doc}\n"

        return summary.strip()

    def generate_available_document_summary(self, evaluation_result: Dict) -> str:
        """
        Generate a human-readable summary of available documents
        """
        found_docs = evaluation_result["found_documents"]
        if not found_docs:
            return "❌ Tidak ada dokumen yang ditemukan."

        summary = f"✅ Dokumen tersedia ({len(found_docs)}):\n"
        for i, doc in enumerate(found_docs, 1):
            confidence_emoji = "🟢" if doc["confidence"] >= 0.8 else "🟡" if doc["confidence"] >= 0.6 else "🔴"
            summary += f"{i}. {doc['required']} {confidence_emoji}\n"

        return summary.strip()

    def create_checklist_report(self, evaluation_result: Dict, company_name: str = "Perusahaan") -> Dict:
        """
        Create a comprehensive checklist report
        """
        return {
            "company_name": company_name,
            "report_type": "checklist_evaluation",
            "generated_at": datetime.now().isoformat(),
            "checklist_info": {
                "type": evaluation_result["checklist_type"],
                "description": evaluation_result["checklist_description"],
                "total_required": evaluation_result["total_required"],
                "total_found": evaluation_result["total_found"]
            },
            "completion_status": {
                "percentage": evaluation_result["completion_percentage"],
                "status": evaluation_result["status"],
                "message": evaluation_result["status_message"]
            },
            "documents": {
                "available": self.generate_available_document_summary(evaluation_result),
                "missing": self.generate_missing_document_summary(evaluation_result),
                "detailed_matches": evaluation_result["document_matches"]
            },
            "quality_metrics": {
                "average_confidence": evaluation_result["average_confidence"],
                "unique_categories": evaluation_result["available_categories_count"],
                "total_files_processed": evaluation_result["available_documents_count"]
            },
            "recommendations": self._generate_recommendations(evaluation_result)
        }

    def _generate_recommendations(self, evaluation_result: Dict) -> List[str]:
        """
        Generate recommendations based on evaluation results
        """
        recommendations = []
        completion_pct = evaluation_result["completion_percentage"]
        missing_docs = evaluation_result["missing_documents"]

        if completion_pct == 100:
            recommendations.append("🎉 Semua dokumen lengkap! Siap untuk proses berikutnya.")
        else:
            if completion_pct >= 80:
                recommendations.append("📋 Hampir selesai! Sediakan dokumen-dokumen yang tersisa.")
            elif completion_pct >= 50:
                recommendations.append("📝 Progress bagus! Fokus pada dokumen-dokumen utama yang masih hilang.")
            else:
                recommendations.append("⚠️ Masih banyak dokumen yang diperlukan. Prioritaskan dokumen-dokumen esensial.")

            # Specific recommendations based on missing documents
            critical_docs = [
                "Akta dan SK Kemenkumham",
                "NPWP Perusahaan",
                "NIB Perusahaan",
                "KTP Pengurus"
            ]

            missing_critical = [doc for doc in missing_docs if any(critical in doc for critical in critical_docs)]
            if missing_critical:
                recommendations.append("🔴 Prioritaskan dokumen-dokumen krusial: " + ", ".join(missing_critical[:3]))

            # Check for financial documents
            missing_financial = [doc for doc in missing_docs if "Keuangan" in doc or "Laporan" in doc or "Mutasi" in doc]
            if missing_financial:
                recommendations.append("💰 Siapkan dokumen keuangan dan mutasi rekening.")

        return recommendations

    def save_evaluation_result(self, evaluation_result: Dict, company_name: str, output_dir: str = "evaluations") -> str:
        """
        Save evaluation result to file
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"checklist_{company_name}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(evaluation_result, f, ensure_ascii=False, indent=2)

            logger.info(f"Evaluation result saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving evaluation result: {e}")
            return ""

    def get_checklist_statistics(self, all_evaluations: List[Dict]) -> Dict:
        """
        Generate statistics from multiple evaluations
        """
        if not all_evaluations:
            return {"error": "No evaluations provided"}

        total_evaluations = len(all_evaluations)
        total_complete = sum(1 for e in all_evaluations if e.get("status") == "complete")
        total_nearly_complete = sum(1 for e in all_evaluations if e.get("status") == "nearly_complete")
        total_partial = sum(1 for e in all_evaluations if e.get("status") == "partial")
        total_incomplete = sum(1 for e in all_evaluations if e.get("status") == "incomplete")

        avg_completion = sum(e.get("completion_percentage", 0) for e in all_evaluations) / total_evaluations
        avg_confidence = sum(e.get("average_confidence", 0) for e in all_evaluations) / total_evaluations

        # Most common missing documents
        all_missing = []
        for eval_result in all_evaluations:
            all_missing.extend(eval_result.get("missing_documents", []))

        missing_frequency = {}
        for doc in all_missing:
            missing_frequency[doc] = missing_frequency.get(doc, 0) + 1

        return {
            "total_evaluations": total_evaluations,
            "completion_distribution": {
                "complete": total_complete,
                "nearly_complete": total_nearly_complete,
                "partial": total_partial,
                "incomplete": total_incomplete
            },
            "average_completion_percentage": round(avg_completion, 1),
            "average_confidence": round(avg_confidence, 2),
            "most_common_missing": sorted(missing_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "generated_at": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    from config import Config

    config = Config()
    manager = ChecklistManager(config)

    # Example documents
    example_docs = [
        {"category": "Akta dan SK Kemenkumham", "filename": "akta_pendirian.pdf"},
        {"category": "NIB dan NPWP", "filename": "nib_company.pdf"},
        {"category": "KTP Pengurus", "filename": "ktp_direktur.jpg"},
        {"category": "Laporan Keuangan", "filename": "laporan_keuangan_2023.pdf"},
    ]

    # Evaluate against different checklist types
    for checklist_type in config.CHECKLIST_TEMPLATES.keys():
        result = manager.evaluate_checklist(checklist_type, example_docs)
        print(f"\n=== {checklist_type} ===")
        print(f"Completion: {result['completion_percentage']}%")
        print(f"Status: {result['status']}")
        print(f"Found: {len(result['found_documents'])}")
        print(f"Missing: {len(result['missing_documents'])}")