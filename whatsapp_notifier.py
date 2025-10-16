#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real WhatsApp Notification System using WAHA API
Sends automatic notifications for missing documents
"""

import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

class WhatsAppNotifier:
    def __init__(self, waha_api_url: str = "http://localhost:3000",
                 target_number: str = "6289620055378",
                 api_key: str = None):
        self.waha_api_url = waha_api_url.rstrip('/')
        self.target_number = target_number
        self.session_name = "default"
        self.api_key = api_key

    def test_connection(self) -> Dict:
        """Test WAHA API connection"""
        try:
            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key

            response = requests.get(f"{self.waha_api_url}/api/sessions",
                                  headers=headers, timeout=10)

            if response.status_code == 200:
                sessions = response.json()
                # Check if session exists
                active_sessions = [s for s in sessions if s.get('status') == 'WORKING']
                return {
                    'success': True,
                    'connected': True,
                    'active_sessions': len(active_sessions),
                    'message': 'WAHA API connected successfully'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'connected': False,
                    'message': 'WAHA API authentication failed - Check API key or WAHA configuration'
                }
            else:
                return {
                    'success': False,
                    'connected': False,
                    'message': f'WAHA API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'connected': False,
                'message': f'Cannot connect to WAHA API: {str(e)}. Is WAHA running on {self.waha_api_url}?'
            }

    def send_message(self, message: str, target_number: Optional[str] = None) -> Dict:
        """Send WhatsApp message via WAHA API"""
        try:
            # Use provided number or default target
            recipient = target_number or self.target_number

            # Remove + if present (WAHA expects format without +)
            if recipient.startswith('+'):
                recipient = recipient[1:]

            payload = {
                "chatId": f"{recipient}@c.us",
                "text": message,
                "session": self.session_name
            }

            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key

            # Send message
            response = requests.post(
                f"{self.waha_api_url}/api/sendText",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                result = response.json()
                # Handle different response formats
                if isinstance(result, dict) and 'id' in result:
                    message_id = result.get('id')
                elif isinstance(result, dict) and '_data' in result:
                    message_id = result['_data'].get('id', {}).get('id', 'unknown')
                else:
                    message_id = 'sent'

                return {
                    'success': True,
                    'message_id': message_id,
                    'status': 'sent',
                    'recipient': recipient,
                    'message': 'Message sent successfully via WAHA'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'WAHA API authentication failed - Check API key',
                    'recipient': recipient
                }
            else:
                return {
                    'success': False,
                    'error': f'WAHA API error: {response.status_code} - {response.text}',
                    'recipient': recipient
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'recipient': recipient
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'recipient': recipient
            }

    def format_missing_documents_message(self, company_name: str,
                                       checklist_type: str,
                                       missing_docs: List[str],
                                       completion_percentage: float) -> str:
        """Format WhatsApp message for missing documents in Indonesian"""

        # Header with requested format
        tanggal = datetime.now().strftime('%d/%m/%Y')
        message = f"Dokumen Kekurangan {checklist_type} {company_name} per {tanggal}\n\n"

        # Missing documents list
        if missing_docs:
            for i, doc in enumerate(missing_docs, 1):
                message += f"{i}. {doc}\n"
        else:
            message += "✅ Semua dokumen lengkap!"

        return message

    def send_missing_documents_notification(self,
                                          company_name: str,
                                          checklist_type: str,
                                          missing_docs: List[str],
                                          completion_percentage: float,
                                          target_number: Optional[str] = None) -> Dict:
        """Send automatic notification for missing documents"""

        # Skip if no missing documents
        if not missing_docs:
            return {
                'success': True,
                'message': 'No missing documents to notify',
                'sent': False
            }

        # Format message
        message = self.format_missing_documents_message(
            company_name, checklist_type, missing_docs, completion_percentage
        )

        # Send message
        result = self.send_message(message, target_number)

        # Add additional info
        if result['success']:
            result.update({
                'notification_type': 'missing_documents',
                'company_name': company_name,
                'checklist_type': checklist_type,
                'missing_count': len(missing_docs),
                'completion_percentage': completion_percentage,
                'sent': True
            })

        return result

    def send_test_message(self, target_number: Optional[str] = None) -> Dict:
        """Send a test message in Indonesian"""
        test_message = "Dokumen Kekurangan Test Notification PT TEST COMPANY per "
        test_message += datetime.now().strftime('%d/%m/%Y') + "\n\n"
        test_message += "1. Dokumen Test 1\n"
        test_message += "2. Dokumen Test 2\n"
        test_message += "3. Dokumen Test 3\n\n"
        test_message += "*Ini adalah pesan test dari sistem*"

        result = self.send_message(test_message, target_number)

        if result['success']:
            result.update({
                'notification_type': 'test',
                'sent': True
            })

        return result

# Global notifier instance
_whatsapp_notifier = None

def get_whatsapp_notifier(waha_api_url: str = "http://localhost:3000",
                         target_number: str = "6289620055378",
                         api_key: str = None) -> WhatsAppNotifier:
    """Get or create WhatsApp notifier instance"""
    global _whatsapp_notifier
    # Always create new instance when different parameters are provided
    if (_whatsapp_notifier is None or
        _whatsapp_notifier.waha_api_url != waha_api_url or
        _whatsapp_notifier.target_number != target_number or
        _whatsapp_notifier.api_key != api_key):
        _whatsapp_notifier = WhatsAppNotifier(waha_api_url, target_number, api_key)
    return _whatsapp_notifier

def auto_send_missing_documents(company_name: str,
                               checklist_type: str,
                               missing_docs: List[str],
                               completion_percentage: float,
                               target_number: Optional[str] = None) -> Dict:
    """Automatically send missing documents notification"""
    notifier = get_whatsapp_notifier()
    return notifier.send_missing_documents_notification(
        company_name, checklist_type, missing_docs, completion_percentage, target_number
    )

def test_whatsapp_connection(target_number: Optional[str] = None) -> Dict:
    """Test WhatsApp connection and send test message"""
    notifier = get_whatsapp_notifier()

    # Test connection first
    connection_test = notifier.test_connection()
    if not connection_test['connected']:
        return connection_test

    # Send test message
    message_test = notifier.send_test_message(target_number)

    return {
        'connection': connection_test,
        'message': message_test,
        'overall_success': connection_test['success'] and message_test['success']
    }