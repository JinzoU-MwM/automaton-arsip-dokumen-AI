"""
Configuration module for AI Legal Document Automation System
Loads settings from environment variables and provides configuration constants
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class containing all system settings"""

    # Folder Configuration
    WATCH_FOLDER = os.getenv("WATCH_FOLDER", "D:/Download Legalitas")

    # Google Drive Configuration
    GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "service_account.json")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    # Ollama AI Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    # WAHA Configuration
    WAHA_API_URL = os.getenv("WAHA_API_URL", "http://localhost:3000")
    WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
    ADMIN_WHATSAPP_NUMBER = os.getenv("ADMIN_WHATSAPP_NUMBER", "")

    # Enhanced Document Categories (from new-features.md)
    DOCUMENT_CATEGORIES = {
        "Akta dan SK Kemenkumham": [
            "akta pendirian", "akta perubahan", "sk kemenkumham", "surat keputusan",
            "pengesahan", "notaris", "akta notaris", "anggaran dasar", "ad/art",
            "perubahan anggaran dasar", "kemenkumham", "pendirian hingga perubahan terakhir"
        ],
        "NIB dan NPWP": [
            "nib", "nomor induk berusaha", "npwp", "nomor pokok wajib pajak",
            "wajib pajak", "pkp", "pengusaha kena pajak", "nib perusahaan",
            "npwp perusahaan"
        ],
        "KTP Pengurus": [
            "ktp", "kartu tanda penduduk", "nik", "nomor induk kependudukan",
            "identitas", "direktur", "komisaris", "pengurus", "ktp pengurus",
            "npwp pengurus", "identitas direktur"
        ],
        "Laporan Keuangan": [
            "laporan keuangan", "neraca", "laba rugi", "spt", "surat pemberitahuan tahunan",
            "mutasi rekening", "laporan audit", "audited", "tahun buku",
            "balance sheet", "income statement", "cash flow", "laporan keuangan 2 tahun",
            "neraca laba rugi", "spt tahunan"
        ],
        "Bank Garansi / Surety Bond": ["bank garansi", "surety bond", "jaminan", "asuransi"],
        "IATA": ["iata", "lisensi", "sertifikat iata"],
        "Pajak": ["spt", "bukti bayar", "faktur", "pajak", "ppn", "pph", "skt", "skf fiskal"],
        "Dokumen Lainnya": []  # Default category
    }

    # Checklist Templates Configuration
    CHECKLIST_TEMPLATES = {
        "BG PIHK PT": {
            "description": "Bank Garansi Penyelenggara Ibadah Haji Khusus - Perseroan Terbatas",
            "required_documents": [
                "Akta dan SK Kemenkumham Pendirian Hingga Perubahan Terakhir",
                "KTP NPWP Pengurus",
                "NPWP Perusahaan",
                "NIB Perusahaan",
                "Laporan Keuangan 2 Tahun",
                "SKT / SKF (Fiskal)",
                "SK PIHK / SK PPIU",
                "Sertifikat Akreditasi PPIU",
                "Lampiran Manifest 1000 Jamaah (Untuk PPIU < 3 Tahun)",
                "Nomor Telepon Direktur dan Nama Ibu Kandung",
                "Kop Surat dan Stempel Perusahaan"
            ],
            "total_required": 11
        },
        "BG PPIU PT": {
            "description": "Bank Garansi Penyelenggara Perjalanan Ibadah Umroh - Perseroan Terbatas",
            "required_documents": [
                "Akta dan SK Kemenkumham Pendirian Hingga Perubahan Terakhir",
                "KTP NPWP Pengurus",
                "NPWP Perusahaan",
                "NIB Perusahaan",
                "Laporan Keuangan 2 Tahun",
                "SKT / SKF (Fiskal)",
                "Rekom / SK PPIU",
                "Nomor Telepon Direktur dan Nama Ibu Kandung",
                "Kop Surat dan Stempel Perusahaan"
            ],
            "total_required": 9
        },
        "Laporan Keuangan": {
            "description": "Laporan Keuangan Perusahaan",
            "required_documents": [
                "Kop Surat",
                "Contoh Stempel",
                "NIB",
                "NPWP Perusahaan",
                "Akta + SK Pendirian",
                "Akta + SK Perubahan",
                "KTP Pengurus",
                "NPWP Pengurus",
                "Mutasi Rekening 2024 Full",
                "Mutasi Rekening 2025 (Jan-Jul)",
                "Foto Kantor (Interior, Eksterior, Aktivitas, Logo)",
                "Sampling Invoice Hotel & Tiket Jamaah 2024",
                "Laporan Keuangan 2023 (Audited jika ada)",
                "Neraca Laba Rugi / SPT Tahun 2024",
                "Nomor Meteran Listrik Kantor"
            ],
            "total_required": 15
        }
    }

    # Document Classification Settings
    DOCUMENT_CLASSIFICATION = {
        "use_google_vision": os.getenv("USE_GOOGLE_VISION", "false").lower() == "true",
        "confidence_threshold": float(os.getenv("CLASSIFICATION_CONFIDENCE_THRESHOLD", "0.6")),
        "ocr_language": os.getenv("OCR_LANGUAGE", "ind+eng"),
        "fallback_to_filename": os.getenv("FALLBACK_TO_FILENAME", "true").lower() == "true",
        "classification_timeout": int(os.getenv("CLASSIFICATION_TIMEOUT", "30"))
    }

    # Required Documents for Completeness Check (Legacy - will be replaced by checklist system)
    REQUIRED_DOCUMENTS = [
        "Akta",
        "NIB",
        "NPWP",
        "KTP Pengurus",
        "Laporan Keuangan",
        "Bank Garansi / Surety Bond",
        "IATA",
        "Pajak"
    ]

    # WhatsApp Notification Templates
    WHATSAPP_TEMPLATES = {
        "checklist_complete": """Halo, berikut hasil pengecekan dokumen PT {company_name}:

✅ Dokumen lengkap:
{available_docs}

📊 Kelengkapan: {completion_percentage}%

🎉 Semua dokumen yang diperlukan telah tersedia! Terima kasih 🙏""",

        "checklist_incomplete": """Halo, berikut hasil pengecekan dokumen PT {company_name}:

✅ Dokumen tersedia:
{available_docs}

❌ Dokumen yang belum ditemukan:
{missing_docs}

📊 Kelengkapan: {completion_percentage}%

Mohon segera dilengkapi. Terima kasih 🙏""",

        "processing_started": """📂 Memproses dokumen untuk PT {company_name}...

Sedang melakukan klasifikasi dan pengecekan kelengkapan dokumen. Hasil akan dikirimkan setelah proses selesai.

⏱️ Estimasi waktu: 2-5 menit""",

        "processing_error": """❌ Terjadi kesalahan saat memproses dokumen PT {company_name}:

Error: {error_message}

Silakan periksa dokumen dan coba kembali. Jika masalah berlanjut, hubungi administrator."""
    }

    # Notification Settings
    NOTIFICATION_SETTINGS = {
        "auto_send_checklist_results": os.getenv("AUTO_SEND_CHECKLIST_RESULTS", "true").lower() == "true",
        "notification_delay_minutes": int(os.getenv("NOTIFICATION_DELAY_MINUTES", "1")),
        "max_retries": int(os.getenv("NOTIFICATION_MAX_RETRIES", "3")),
        "admin_notification_on_error": os.getenv("ADMIN_NOTIFICATION_ON_ERROR", "true").lower() == "true"
    }

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/legal_automation.log")

    @classmethod
    def validate(cls):
        """Validate required configuration settings"""
        missing_vars = []

        if not cls.WAHA_API_KEY:
            missing_vars.append("WAHA_API_KEY")
        if not cls.ADMIN_WHATSAPP_NUMBER:
            missing_vars.append("ADMIN_WHATSAPP_NUMBER")
        if not cls.GOOGLE_DRIVE_FOLDER_ID:
            missing_vars.append("GOOGLE_DRIVE_FOLDER_ID")

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return True