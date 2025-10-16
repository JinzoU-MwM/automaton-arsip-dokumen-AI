"""
Enhanced WAHA Notifier module for sending WhatsApp notifications
Handles real-time notifications to admin about document processing results
with checklist-based message templates and enhanced formatting
"""

import requests
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import time

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
        self.templates = Config.WHATSAPP_TEMPLATES
        self.notification_settings = Config.NOTIFICATION_SETTINGS
        self._last_notifications = {}  # Track last notifications to avoid spam

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

    def send_checklist_notification(self, company_name: str, checklist_result: Dict,
                                   recipient_number: str = None) -> bool:
        """
        Send checklist evaluation result notification using template system

        Args:
            company_name: Name of the company
            checklist_result: Checklist evaluation result from ChecklistManager
            recipient_number: Optional recipient number (defaults to admin)

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            target_number = recipient_number or self.admin_number

            # Check rate limiting
            if self._is_rate_limited(f"checklist_{company_name}"):
                logger.info(f"Checklist notification for {company_name} rate limited")
                return False

            # Determine template based on completion status
            if checklist_result.get("status") == "complete":
                template_name = "checklist_complete"
            else:
                template_name = "checklist_incomplete"

            # Format message using template
            message = self._format_template_message(template_name, company_name, checklist_result)

            success = self._send_message_to_number(message, target_number)

            if success:
                self._update_notification_timestamp(f"checklist_{company_name}")
                logger.info(f"Checklist notification sent for {company_name}")

            return success

        except Exception as e:
            logger.error(f"Failed to send checklist notification: {str(e)}")
            return False

    def send_processing_started_notification(self, company_name: str,
                                           recipient_number: str = None) -> bool:
        """
        Send notification when document processing starts

        Args:
            company_name: Name of the company
            recipient_number: Optional recipient number (defaults to admin)

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            target_number = recipient_number or self.admin_number

            # Check rate limiting
            if self._is_rate_limited(f"processing_{company_name}"):
                return False

            message = self.templates["processing_started"].format(company_name=company_name)

            success = self._send_message_to_number(message, target_number)

            if success:
                self._update_notification_timestamp(f"processing_{company_name}")

            return success

        except Exception as e:
            logger.error(f"Failed to send processing started notification: {str(e)}")
            return False

    def send_processing_error_notification(self, company_name: str, error_message: str,
                                         recipient_number: str = None) -> bool:
        """
        Send notification when processing fails

        Args:
            company_name: Name of the company
            error_message: Error description
            recipient_number: Optional recipient number (defaults to admin)

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            target_number = recipient_number or self.admin_number

            message = self.templates["processing_error"].format(
                company_name=company_name,
                error_message=error_message
            )

            return self._send_message_to_number(message, target_number)

        except Exception as e:
            logger.error(f"Failed to send processing error notification: {str(e)}")
            return False

    def send_batch_notifications(self, notifications: List[Dict]) -> Dict[str, bool]:
        """
        Send multiple notifications in batch

        Args:
            notifications: List of notification dictionaries with keys:
                - type: 'checklist', 'processing_started', 'processing_error'
                - company_name: str
                - data: Dict (additional data for the notification)
                - recipient_number: str (optional)

        Returns:
            Dict with notification results
        """
        results = {}

        for i, notification in enumerate(notifications):
            try:
                notif_type = notification.get('type')
                company_name = notification.get('company_name')
                data = notification.get('data', {})
                recipient_number = notification.get('recipient_number')

                if notif_type == 'checklist':
                    success = self.send_checklist_notification(company_name, data, recipient_number)
                elif notif_type == 'processing_started':
                    success = self.send_processing_started_notification(company_name, recipient_number)
                elif notif_type == 'processing_error':
                    error_msg = data.get('error_message', 'Unknown error')
                    success = self.send_processing_error_notification(company_name, error_msg, recipient_number)
                else:
                    success = False
                    logger.warning(f"Unknown notification type: {notif_type}")

                results[f"notification_{i}"] = success

                # Add delay between notifications to avoid rate limiting
                if i < len(notifications) - 1:
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error sending batch notification {i}: {str(e)}")
                results[f"notification_{i}"] = False

        return results

    def _send_message_to_number(self, message: str, phone_number: str) -> bool:
        """
        Send message to specific phone number

        Args:
            message: Message content
            phone_number: Target phone number

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
                'chatId': f"{phone_number}@c.us",
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
            logger.info(f"WhatsApp message sent to {phone_number}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"WAHA API request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return False

    def _format_template_message(self, template_name: str, company_name: str,
                               checklist_result: Dict) -> str:
        """
        Format message using template system

        Args:
            template_name: Name of the template to use
            company_name: Name of the company
            checklist_result: Checklist evaluation result

        Returns:
            Formatted message string
        """
        if template_name not in self.templates:
            logger.warning(f"Template {template_name} not found, using default format")
            return self._format_default_checklist_message(company_name, checklist_result)

        template = self.templates[template_name]

        # Extract required data for template
        completion_percentage = checklist_result.get("completion_percentage", 0)
        found_docs = checklist_result.get("found_documents", [])
        missing_docs = checklist_result.get("missing_documents", [])

        # Format available documents
        available_docs_text = ""
        if found_docs:
            available_docs_text = "\n".join([
                f"• {doc['required']}" for doc in found_docs[:5]  # Limit to 5 items
            ])
            if len(found_docs) > 5:
                available_docs_text += f"\n• ... dan {len(found_docs) - 5} dokumen lainnya"

        # Format missing documents
        missing_docs_text = ""
        if missing_docs:
            missing_docs_text = "\n".join([
                f"• {doc}" for doc in missing_docs[:5]  # Limit to 5 items
            ])
            if len(missing_docs) > 5:
                missing_docs_text += f"\n• ... dan {len(missing_docs) - 5} dokumen lainnya"

        # Fill template
        try:
            message = template.format(
                company_name=company_name,
                completion_percentage=completion_percentage,
                available_docs=available_docs_text,
                missing_docs=missing_docs_text,
                total_found=len(found_docs),
                total_missing=len(missing_docs),
                status=checklist_result.get("status", "unknown")
            )

            # Add footer if not already present
            if "_Sistem Otomasi Legal Dokumen_" not in message:
                message += "\n\n_Sistem Otomasi Legal Dokumen_"

            return message

        except KeyError as e:
            logger.error(f"Template formatting error: missing key {str(e)}")
            return self._format_default_checklist_message(company_name, checklist_result)

    def _format_default_checklist_message(self, company_name: str, checklist_result: Dict) -> str:
        """
        Default message formatting if template fails

        Args:
            company_name: Name of the company
            checklist_result: Checklist evaluation result

        Returns:
            Formatted message string
        """
        completion_percentage = checklist_result.get("completion_percentage", 0)
        status = checklist_result.get("status", "unknown")
        found_count = checklist_result.get("total_found", 0)
        total_required = checklist_result.get("total_required", 0)

        status_emojis = {
            "complete": "🎉",
            "nearly_complete": "📋",
            "partial": "⚠️",
            "incomplete": "❌"
        }

        emoji = status_emojis.get(status, "📋")

        message = f"""{emoji} *Hasil Pengecekan Dokumen PT {company_name}*

📊 *Status:* {status.replace('_', ' ').title()}
📈 *Kelengkapan:* {completion_percentage}% ({found_count}/{total_required} dokumen)

📅 *Waktu:* {datetime.now().strftime('%d %B %Y %H:%M')}

_Sistem Otomasi Legal Dokumen_"""

        return message

    def _is_rate_limited(self, notification_key: str) -> bool:
        """
        Check if notification should be rate limited

        Args:
            notification_key: Unique key for the notification type

        Returns:
            True if rate limited, False otherwise
        """
        if not self.notification_settings.get("auto_send_checklist_results", True):
            return True

        delay_minutes = self.notification_settings.get("notification_delay_minutes", 1)

        if notification_key in self._last_notifications:
            last_time = self._last_notifications[notification_key]
            time_diff = datetime.now() - last_time

            if time_diff < timedelta(minutes=delay_minutes):
                return True

        return False

    def _update_notification_timestamp(self, notification_key: str):
        """
        Update the timestamp for the last sent notification

        Args:
            notification_key: Unique key for the notification type
        """
        self._last_notifications[notification_key] = datetime.now()

    def retry_failed_notifications(self, failed_notifications: List[Dict],
                                  max_retries: int = None) -> Dict[str, bool]:
        """
        Retry failed notifications with exponential backoff

        Args:
            failed_notifications: List of failed notification dictionaries
            max_retries: Maximum number of retries (defaults to config)

        Returns:
            Dict with retry results
        """
        if max_retries is None:
            max_retries = self.notification_settings.get("max_retries", 3)

        results = {}

        for i, notification in enumerate(failed_notifications):
            success = False

            for attempt in range(max_retries):
                try:
                    # Exponential backoff: wait 2^attempt seconds
                    if attempt > 0:
                        time.sleep(2 ** attempt)

                    notif_type = notification.get('type')
                    company_name = notification.get('company_name')
                    data = notification.get('data', {})
                    recipient_number = notification.get('recipient_number')

                    if notif_type == 'checklist':
                        success = self.send_checklist_notification(company_name, data, recipient_number)
                    elif notif_type == 'processing_started':
                        success = self.send_processing_started_notification(company_name, recipient_number)
                    elif notif_type == 'processing_error':
                        error_msg = data.get('error_message', 'Unknown error')
                        success = self.send_processing_error_notification(company_name, error_msg, recipient_number)

                    if success:
                        break

                except Exception as e:
                    logger.error(f"Retry {attempt + 1} failed for notification {i}: {str(e)}")

            results[f"retry_notification_{i}"] = success

        return results


class EnhancedNotificationManager:
    """
    High-level notification manager that orchestrates different types of notifications
    """

    def __init__(self):
        """Initialize notification manager"""
        self.waha_notifier = WAHANotifier()

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