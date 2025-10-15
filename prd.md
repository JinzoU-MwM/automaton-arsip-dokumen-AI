🧩 PRD: AI-Driven Legal Document Automation System

(Integrasi Google Drive + WAHA + Local AI Agent)

📘 1. Overview

Sistem ini adalah AI-based automation agent yang bertugas mengelola dokumen legal perusahaan dari folder lokal, mengunggahnya ke Google Drive sesuai struktur yang telah ditentukan, memeriksa kelengkapan dokumen, dan mengirim notifikasi WhatsApp via WAHA secara real-time.
Seluruh proses dijalankan otomatis dengan dukungan local AI agent (Ollama) untuk pemrosesan instruksi natural language.

🧭 2. Goals
Tujuan	Penjelasan
📁 Otomatisasi Arsip Legalitas	Semua file di folder lokal diatur otomatis ke Drive sesuai perusahaan & jenis dokumen.
🧠 AI Command Understanding	Sistem memahami perintah natural seperti “Ini untuk PT JNI, pekerjaan izin PPIU”.
🔍 Pengecekan Kelengkapan	Sistem mendeteksi kekurangan dokumen wajib (Laporan Keuangan, Bank Garansi, IATA, Pajak).
💬 Notifikasi WA	Sistem mengirim laporan hasil ke WA admin melalui WAHA API secara real-time.
🪄 Kolaborasi Multi-AI	Dokumentasi & struktur kode kompatibel dengan Claude Code Superpowers, GPT-5, Copilot, dan Replit AI.
🏗️ 3. Architecture Overview
🧩 Komponen Utama
Komponen	Fungsi	Teknologi
Local Folder Watcher	Memantau folder Download Legalitas untuk file baru	Python watchdog
AI Command Parser	Menginterpretasi perintah pengguna untuk menentukan perusahaan & pekerjaan	Ollama (LLaMA3 / Mistral / Phi-3)
Google Drive Manager	Membuat folder perusahaan & subfolder, serta upload file	Google Drive API
Document Completeness Checker	Memastikan semua dokumen wajib ada	Python Custom Logic
WAHA Notifier	Mengirim pesan WA hasil pemeriksaan ke admin	WAHA API (/api/sendText)
Data Logger (Optional)	Menyimpan hasil proses ke Google Sheet / PostgreSQL	Google Sheet API / psycopg2
⚙️ 4. Workflow Diagram (High-Level)
User → Command → AI Parser → Drive Organizer
                              ↓
                        Completeness Checker
                              ↓
                    WAHA Notifier → Admin
                              ↓
                      (Optional) Logger

📂 5. Folder & File Structure (GitHub Repo)
ai-legal-automation/
├── app/
│   ├── watcher.py            # Folder watcher + event handler
│   ├── drive_manager.py      # Upload, folder creation, document check
│   ├── ai_parser.py          # Ollama local command interpreter
│   ├── notifier.py           # WAHA message sender
│   ├── main.py               # Orchestrator entrypoint
│   └── config.py             # API keys, folder IDs, admin numbers
│
├── docs/
│   ├── PRD.md                # Dokumen ini (PRD untuk AI tools)
│   ├── Claude-Integration.md # Petunjuk integrasi Claude Code Superpowers
│   └── API_Specs.md          # Spesifikasi endpoint WAHA & Drive
│
├── service_account.json      # Google Drive credentials (ignored by .gitignore)
├── requirements.txt
├── README.md
└── .env.example

🧩 6. Document Categories
Nama Folder	Keterangan
Akta	Dokumen pendirian perusahaan
NIB	Nomor Induk Berusaha
NPWP	Pajak badan usaha
KTP Pengurus	Identitas pengurus
Laporan Keuangan	Neraca, laba rugi, dsb
Bank Garansi / Surety Bond	Dokumen jaminan bank / asuransi
IATA	Dokumen lisensi / sertifikat IATA
Pajak	SPT, bukti bayar, faktur, dsb
🤖 7. AI Interaction Protocol
Input

Command contoh:

“Ini untuk PT Jaminan Nasional Indonesia, pekerjaan pengurusan izin PPIU.”

Folder Source:

D:/Download Legalitas

Output
{
  "company": "PT Jaminan Nasional Indonesia",
  "job_type": "pengurusan izin PPIU",
  "missing_documents": ["IATA", "Pajak"],
  "drive_upload_status": "success",
  "notification_status": "sent"
}

🧠 8. AI Parser Specification (Ollama Integration)
Task	Model	Prompt Template
Extract company name	LLaMA3 / Phi-3	“Extract company name and job type from the following sentence: {{user_input}}. Respond only in JSON.”
Output Format	JSON	{ "company": "PT ...", "job_type": "..." }
🔗 9. WAHA Integration

Endpoint:
POST /api/sendText

Headers:

x-api-key: <WAHA_API_KEY>
Content-Type: application/json


Body:

{
  "receiver": "6281234567890",
  "message": "📂 Upload PT JNI selesai. ⚠️ Kekurangan: IATA, Pajak"
}

🧾 10. Google Drive API Integration

Membuat folder perusahaan jika belum ada

Membuat subfolder kategori (Akta, NIB, NPWP, dst)

Upload file ke subfolder sesuai kategori

Cek apakah tiap kategori memiliki minimal 1 file

📧 11. Output Notification Format (via WA)

📄 Update Legalitas PT Jaminan Nasional Indonesia
⚙️ Pekerjaan: Pengurusan Izin PPIU
❌ Kekurangan: IATA, Pajak
📅 Update: 15 Oktober 2025

🪄 12. Future Enhancements

Integrasi OCR (untuk membaca isi dokumen)

Dashboard Web (Streamlit)

Multi-tenant mode untuk tiap perusahaan (SaaS)

AI summarizer untuk laporan legalitas otomatis

Voice Command support

📘 13. Claude Code Superpowers Integration Guide

File: docs/Claude-Integration.md

# 🤝 Claude Code Superpowers Integration

This repository supports the **Claude Code Superpowers** plugin for AI-assisted development.

## 🔧 Setup Steps

1. **Enable Claude Code Superpowers** in your Claude app or VS Code extension.
2. **Clone this repo**:
   ```bash
   git clone https://github.com/<your-org>/ai-legal-automation.git
   cd ai-legal-automation


Ensure the following files exist:

docs/PRD.md

docs/API_Specs.md

app/main.py

requirements.txt

Claude Context Configuration:
Claude Code automatically reads context from /docs/PRD.md and /docs/API_Specs.md
Use the command palette:

@Claude expand main.py or @Claude explain drive_manager.py

GitHub Repo Integration:
Ensure repo has:

ai_collaboration:
  enabled: true
  context_files:
    - docs/PRD.md
    - docs/API_Specs.md

🧠 Usage Examples

Ask Claude:
“@Claude optimize upload_to_drive() for async upload”

Ask GPT-5:
“@GPT refactor ai_parser.py to support multi-language input”

Ask Copilot:
“@Copilot auto-complete Drive folder creation loop”


---

## 🧾 14. File `requirements.txt`


google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
requests
watchdog
ollama
python-dotenv