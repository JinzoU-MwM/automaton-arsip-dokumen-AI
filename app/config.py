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

    # Document Categories
    DOCUMENT_CATEGORIES = {
        "Akta": ["akta", "pendirian", "perubahan", "anggaran dasar"],
        "NIB": ["nib", "nomor induk berusaha", "nomor induk"],
        "NPWP": ["npwp", "nomor pokok wajib pajak", "pajak"],
        "KTP Pengurus": ["ktp", "identitas", "pengurus", "direktur"],
        "Laporan Keuangan": ["laporan keuangan", "neraca", "laba rugi", "keuangan"],
        "Bank Garansi / Surety Bond": ["bank garansi", "surety bond", "jaminan", "asuransi"],
        "IATA": ["iata", "lisensi", "sertifikat iata"],
        "Pajak": ["spt", "bukti bayar", "faktur", "pajak", "ppn", "pph"]
    }

    # Required Documents for Completeness Check
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