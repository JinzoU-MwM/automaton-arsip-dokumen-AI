"""
WAHA Notifier module for sending WhatsApp notifications
Handles real-time notifications to admin about document processing results
"""

import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from app.config import Config

logger = logging.getLogger(__name__)


class WAHANotifier:
    """
    WhatsApp notification handler using WAHA API
    Sends formatted messages to admin about document processing
    """

    def __init__(self):
        """Initialize WAHA notifier with configuration"""
        self.api_url = Config.WAHA_API_URL
        self.api_key = Config.WAHA_API_KEY
        self.admin_number = Config.ADMIN_WHATSAPP_NUMBER
        self.timeout = 30

    def send_upload_notification(self, company_name: str, job_type: str,
                                file_name: str, completeness_result: Dict[str, Any]) -> bool:
        """
        Send notification about successful file upload and completeness check

        Args:
            company_name: Name of the company
            job_type: Type of job/work
            file_name: Name of uploaded file
            completeness_result: Document completeness check result

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            message = self._format_upload_message(
                company_name, job_type, file_name, completeness_result
            )
            return self._send_message(message)

        except Exception as e:
            logger.error(f"Failed to send upload notification: {str(e)}")
            return False

    def send_error_notification(self, error_message: str, context: Dict[str, Any] = None) -> bool:
        """
        Send error notification to admin

        Args:
            error_message: Error description
            context: Additional context information

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            message = self._format_error_message(error_message, context)
            return self._send_message(message)

        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")
            return False

    def send_completion_notification(self, company_name: str,
                                   completeness_result: Dict[str, Any]) -> bool:
        """
        Send notification about document completeness status

        Args:
            company_name: Name of the company
            completeness_result: Document completeness check result

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            message = self._format_completion_message(company_name, completeness_result)
            return self._send_message(message)

        except Exception as e:
            logger.error(f"Failed to send completion notification: {str(e)}")
            return False

    def _send_message(self, message: str) -> bool:
        """
        Send message via WAHA API

        Args:
            message: Message content to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            url = f"{self.api_url}/api/sendText"
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }

            payload = {
                'chatId': f"{self.admin_number}@c.us",
                'text': message,
                'session': 'default'
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            logger.info(f"WhatsApp notification sent to {self.admin_number}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"WAHA API request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return False

    def _format_upload_message(self, company_name: str, job_type: str,
                              file_name: str, completeness_result: Dict[str, Any]) -> str:
        """
        Format upload notification message

        Args:
            company_name: Name of the company
            job_type: Type of job/work
            file_name: Name of uploaded file
            completeness_result: Document completeness result

        Returns:
            Formatted message string
        """
        status_emoji = "✅" if completeness_result.get('status') == 'complete' else "⚠️"
        completion_pct = completeness_result.get('completion_percentage', 0)
        missing_docs = completeness_result.get('missing_documents', [])

        message = f"""📂 *Upload Dokumen Legalitas*

🏢 *Perusahaan:* {company_name}
⚙️ *Pekerjaan:* {job_type}
📄 *File:* {file_name}
{status_emoji} *Kelengkapan:* {completion_pct}%

📅 *Waktu:* {datetime.now().strftime('%d %B %Y %H:%M')}"""

        if missing_docs:
            message += f"\n\n❌ *Dokumen Kurang:* {', '.join(missing_docs)}"
        else:
            message += "\n\n✅ *Semua dokumen lengkap!*"

        message += "\n\n_Sistem Otomasi Legal Dokumen_"

        return message

    def _format_error_message(self, error_message: str, context: Dict[str, Any] = None) -> str:
        """
        Format error notification message

        Args:
            error_message: Error description
            context: Additional context information

        Returns:
            Formatted error message
        """
        message = f"""⚠️ *Error Sistem Legal Dokumen*

🚨 *Pesan:* {error_message}
📅 *Waktu:* {datetime.now().strftime('%d %B %Y %H:%M')}"""

        if context:
            message += "\n\n*Detail:*"
            for key, value in context.items():
                message += f"\n• {key.replace('_', ' ').title()}: {value}"

        message += "\n\n_Silakan periksa sistem untuk detail lebih lanjut._"

        return message

    def _format_completion_message(self, company_name: str,
                                  completeness_result: Dict[str, Any]) -> str:
        """
        Format document completion status message

        Args:
            company_name: Name of the company
            completeness_result: Document completeness result

        Returns:
            Formatted completion message
        """
        status = completeness_result.get('status', 'unknown')
        completion_pct = completeness_result.get('completion_percentage', 0)
        present_docs = completeness_result.get('present_documents', [])
        missing_docs = completeness_result.get('missing_documents', [])

        # Status emoji mapping
        status_emojis = {
            'complete': '🎉',
            'mostly_complete': '✅',
            'partially_complete': '⚠️',
            'incomplete': '❌',
            'error': '🚨'
        }

        emoji = status_emojis.get(status, '📋')

        message = f"""{emoji} *Update Kelengkapan Dokumen*

🏢 *Perusahaan:* {company_name}
📊 *Status:* {status.replace('_', ' ').title()}
📈 *Persentase:* {completion_pct}%
📅 *Update:* {datetime.now().strftime('%d %B %Y %H:%M')}"""

        if present_docs:
            message += f"\n\n✅ *Dokumen Ada ({len(present_docs)}):*"
            message += f"\n{', '.join(present_docs)}"

        if missing_docs:
            message += f"\n\n❌ *Dokumen Kurang ({len(missing_docs)}):*"
            message += f"\n{', '.join(missing_docs)}"

        if status == 'complete':
            message += "\n\n🎊 *Selamat! Semua dokumen legalitas sudah lengkap.*"
        elif status == 'error':
            message += "\n\n⚠️ *Terjadi kesalahan saat memeriksa dokumen.*"

        message += "\n\n_Sistem Otomasi Legal Dokumen_"

        return message

    def test_connection(self) -> bool:
        """
        Test connection to WAHA API

        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = f"{self.api_url}/api/sessions"
            headers = {'x-api-key': self.api_key}

            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            # If we get here, the connection is successful
            logger.info("Successfully connected to WAHA")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to WAHA: {str(e)}")
            return False

    def send_test_message(self) -> bool:
        """
        Send a test message to verify WAHA configuration

        Returns:
            True if test message sent successfully, False otherwise
        """
        message = f"""🧪 *Test Notifikasi Legal Dokumen*

✅ *Sistem aktif dan berfungsi normal*
📅 *Test time:* {datetime.now().strftime('%d %B %Y %H:%M:%S')}

_Sistem Otomasi Legal Dokumen v1.0_"""

        result = self._send_message(message)
        if result:
            logger.info("Test message sent successfully")
        else:
            logger.error("Failed to send test message")

        return result


class NotificationManager:
    """
    High-level notification manager that orchestrates different types of notifications
    """

    def __init__(self):
        """Initialize notification manager"""
        self.waha_notifier = WAHANotifier()

    def notify_file_processed(self, company_name: str, job_type: str,
                            file_name: str, completeness_result: Dict[str, Any]) -> bool:
        """
        Send comprehensive notification after file processing

        Args:
            company_name: Name of the company
            job_type: Type of job/work
            file_name: Name of processed file
            completeness_result: Document completeness result

        Returns:
            True if notifications sent successfully, False otherwise
        """
        try:
            # Send upload notification
            upload_success = self.waha_notifier.send_upload_notification(
                company_name, job_type, file_name, completeness_result
            )

            # If there are critical missing documents, send additional alert
            critical_missing = self._get_critical_missing_documents(completeness_result)
            if critical_missing:
                self.waha_notifier.send_error_notification(
                    f"Dokumen krusial kurang: {', '.join(critical_missing)}",
                    {
                        'company': company_name,
                        'job_type': job_type,
                        'missing_critical': critical_missing
                    }
                )

            return upload_success

        except Exception as e:
            logger.error(f"Failed to send file processed notifications: {str(e)}")
            return False

    def _get_critical_missing_documents(self, completeness_result: Dict[str, Any]) -> list:
        """
        Extract critical missing documents from completeness result

        Args:
            completeness_result: Document completeness result

        Returns:
            List of critical missing document types
        """
        critical_docs = ['Akta', 'NIB', 'NPWP', 'KTP Pengurus']
        missing_docs = completeness_result.get('missing_documents', [])
        return [doc for doc in missing_docs if doc in critical_docs]

    def notify_system_error(self, error_message: str, context: Dict[str, Any] = None) -> bool:
        """
        Send system error notification

        Args:
            error_message: Error description
            context: Additional context information

        Returns:
            True if notification sent successfully, False otherwise
        """
        return self.waha_notifier.send_error_notification(error_message, context)

    def test_all_notifications(self) -> Dict[str, bool]:
        """
        Test all notification systems

        Returns:
            Dict with test results for each notification type
        """
        results = {}

        # Test WAHA connection
        results['waha_connection'] = self.waha_notifier.test_connection()

        # Test WAHA message
        if results['waha_connection']:
            results['waha_message'] = self.waha_notifier.send_test_message()
        else:
            results['waha_message'] = False

        return results


# Example usage and testing
if __name__ == "__main__":
    def test_notifications():
        """Test notification systems"""
        try:
            # Initialize notification manager
            notification_manager = NotificationManager()

            # Test all notifications
            test_results = notification_manager.test_all_notifications()

            print("Notification Test Results:")
            for test_name, result in test_results.items():
                status = "✅" if result else "❌"
                print(f"{status} {test_name}: {'Passed' if result else 'Failed'}")

            # Example usage with mock data
            mock_completeness = {
                'status': 'partially_complete',
                'completion_percentage': 75.0,
                'present_documents': ['Akta', 'NIB', 'NPWP'],
                'missing_documents': ['IATA', 'Pajak']
            }

            # Send example notification
            success = notification_manager.notify_file_processed(
                "PT Test Company",
                "Pengurusan Izin PPIU",
                "test_document.pdf",
                mock_completeness
            )

            print(f"\nExample notification sent: {'✅' if success else '❌'}")

        except Exception as e:
            print(f"Test failed: {str(e)}")

    test_notifications()