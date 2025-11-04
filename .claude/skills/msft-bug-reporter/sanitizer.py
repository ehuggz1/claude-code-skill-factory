"""
Sanitizer Module

Advanced text sanitization for public disclosure of bug reports.

This module handles removal of:
- PII (emails, names, IP addresses)
- Internal URLs and file paths
- Credentials and secrets (API keys, passwords, tokens)
- Azure resource identifiers (subscription IDs, resource names)

All sanitization actions are logged for transparency and review.
"""

from typing import Dict, Any, List, Tuple
import re
from datetime import datetime


class Sanitizer:
    """
    Handles comprehensive text sanitization for public bug report disclosure.

    This class provides pattern-based sanitization with detailed logging
    of all redaction actions taken.
    """

    def __init__(self):
        """Initialize sanitizer with compiled regex patterns."""
        # PII Patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.ipv4_pattern = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )
        self.ipv6_pattern = re.compile(
            r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        )

        # Internal URL/Path Patterns
        self.internal_url_pattern = re.compile(
            r'https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|[\w-]+\.internal|[\w-]+\.local|[\w-]+\.corp)[^\s]*',
            re.IGNORECASE
        )
        self.windows_path_pattern = re.compile(
            r'[A-Z]:\\(?:[^\s<>:"|?*\\]+\\)*[^\s<>:"|?*\\]*',
            re.IGNORECASE
        )
        self.unc_path_pattern = re.compile(
            r'\\\\[^\s\\]+(?:\\[^\s\\]+)*'
        )
        self.unix_internal_path_pattern = re.compile(
            r'/(?:home|opt|usr|var|internal|corp)/[^\s]*'
        )

        # Credential/Secret Patterns
        self.api_key_pattern = re.compile(
            r'\b(?:api[_-]?key|apikey|access[_-]?key)["\s:=]+([A-Za-z0-9_\-]{20,})',
            re.IGNORECASE
        )
        self.password_pattern = re.compile(
            r'\b(?:password|passwd|pwd)["\s:=]+([^\s"\'<>]+)',
            re.IGNORECASE
        )
        self.bearer_token_pattern = re.compile(
            r'\b(?:Bearer|Token)["\s:=]+([A-Za-z0-9_\-\.]+)',
            re.IGNORECASE
        )
        self.jwt_pattern = re.compile(
            r'\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'
        )
        self.connection_string_pattern = re.compile(
            r'(?:Server|Data Source|Host|Database|User ID|Password|Uid|Pwd|Integrated Security)=[^;]+(?:;|$)',
            re.IGNORECASE
        )
        self.secret_key_pattern = re.compile(
            r'\b(?:secret[_-]?key|client[_-]?secret)["\s:=]+([A-Za-z0-9_\-]{20,})',
            re.IGNORECASE
        )

        # Azure Resource Patterns
        self.azure_subscription_pattern = re.compile(
            r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            re.IGNORECASE
        )
        self.azure_resource_group_pattern = re.compile(
            r'\bresourceGroups/([A-Za-z0-9_-]+)',
            re.IGNORECASE
        )
        self.azure_resource_name_pattern = re.compile(
            r'\.(?:azurewebsites|blob\.core\.windows|database\.windows|vault\.azure|servicebus\.windows|redis\.cache\.windows)\.net',
            re.IGNORECASE
        )
        self.azure_storage_account_pattern = re.compile(
            r'\b[a-z0-9]{3,24}\.blob\.core\.windows\.net\b',
            re.IGNORECASE
        )

        # Tracking
        self.sanitization_log: List[str] = []
        self.private_data: Dict[str, List[str]] = {
            'emails': [],
            'ip_addresses': [],
            'internal_urls': [],
            'file_paths': [],
            'credentials': [],
            'azure_subscriptions': [],
            'azure_resources': []
        }

    def sanitize_text(self, text: str, preserve_private_data: bool = True) -> Tuple[str, List[str]]:
        """
        Sanitize a single text string, removing all sensitive information.

        Args:
            text: Input text to sanitize
            preserve_private_data: If True, store removed data for private report

        Returns:
            Tuple of (sanitized_text, sanitization_log)

        Examples:
            >>> sanitizer = Sanitizer()
            >>> sanitized, log = sanitizer.sanitize_text("Contact user@company.com at 192.168.1.1")
            >>> print(sanitized)
            "Contact [REDACTED-EMAIL] at [REDACTED-IP]"
        """
        if not text:
            return text, []

        self.sanitization_log = []
        sanitized = text

        # Sanitize in order of specificity (most specific first)

        # 1. Credentials and Secrets
        sanitized = self._sanitize_credentials(sanitized, preserve_private_data)

        # 2. Azure Resources
        sanitized = self._sanitize_azure_resources(sanitized, preserve_private_data)

        # 3. Internal URLs and Paths
        sanitized = self._sanitize_urls_and_paths(sanitized, preserve_private_data)

        # 4. PII
        sanitized = self._sanitize_pii(sanitized, preserve_private_data)

        return sanitized, self.sanitization_log.copy()

    def sanitize_jira_data(self, jira_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Sanitize an entire JIRA data dictionary.

        Args:
            jira_data: JIRA data dictionary from jira_fetcher

        Returns:
            Tuple of (sanitized_jira_data, combined_sanitization_log)
        """
        sanitized_data = {}
        all_logs = []

        for key, value in jira_data.items():
            if isinstance(value, str):
                sanitized_value, log = self.sanitize_text(value)
                sanitized_data[key] = sanitized_value
                all_logs.extend(log)
            elif isinstance(value, dict):
                sanitized_value, log = self.sanitize_jira_data(value)
                sanitized_data[key] = sanitized_value
                all_logs.extend(log)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item, log = self.sanitize_text(item)
                        sanitized_list.append(sanitized_item)
                        all_logs.extend(log)
                    elif isinstance(item, dict):
                        sanitized_item, log = self.sanitize_jira_data(item)
                        sanitized_list.append(sanitized_item)
                        all_logs.extend(log)
                    else:
                        sanitized_list.append(item)
                sanitized_data[key] = sanitized_list
            else:
                sanitized_data[key] = value

        return sanitized_data, all_logs

    def _sanitize_credentials(self, text: str, preserve: bool) -> str:
        """Sanitize credentials and secrets."""
        sanitized = text

        # JWT tokens
        jwt_matches = self.jwt_pattern.findall(sanitized)
        if jwt_matches:
            self.sanitization_log.append(f"Removed {len(jwt_matches)} JWT token(s)")
            if preserve:
                self.private_data['credentials'].extend(jwt_matches)
            sanitized = self.jwt_pattern.sub('[REDACTED-JWT-TOKEN]', sanitized)

        # API keys
        api_key_matches = self.api_key_pattern.findall(sanitized)
        if api_key_matches:
            self.sanitization_log.append(f"Removed {len(api_key_matches)} API key(s)")
            if preserve:
                self.private_data['credentials'].extend(api_key_matches)
            sanitized = self.api_key_pattern.sub(r'\1[REDACTED-API-KEY]', sanitized)

        # Secret keys
        secret_matches = self.secret_key_pattern.findall(sanitized)
        if secret_matches:
            self.sanitization_log.append(f"Removed {len(secret_matches)} secret key(s)")
            if preserve:
                self.private_data['credentials'].extend(secret_matches)
            sanitized = self.secret_key_pattern.sub(r'\1[REDACTED-SECRET]', sanitized)

        # Bearer tokens
        bearer_matches = self.bearer_token_pattern.findall(sanitized)
        if bearer_matches:
            self.sanitization_log.append(f"Removed {len(bearer_matches)} bearer token(s)")
            if preserve:
                self.private_data['credentials'].extend(bearer_matches)
            sanitized = self.bearer_token_pattern.sub(r'\1[REDACTED-TOKEN]', sanitized)

        # Passwords
        password_matches = self.password_pattern.findall(sanitized)
        if password_matches:
            self.sanitization_log.append(f"Removed {len(password_matches)} password(s)")
            if preserve:
                self.private_data['credentials'].extend(password_matches)
            sanitized = self.password_pattern.sub(r'\1[REDACTED-PASSWORD]', sanitized)

        # Connection strings
        conn_str_matches = self.connection_string_pattern.findall(sanitized)
        if conn_str_matches:
            self.sanitization_log.append(f"Removed {len(conn_str_matches)} connection string component(s)")
            if preserve:
                self.private_data['credentials'].extend(conn_str_matches)
            sanitized = self.connection_string_pattern.sub('[REDACTED-CONNECTION-STRING];', sanitized)

        return sanitized

    def _sanitize_azure_resources(self, text: str, preserve: bool) -> str:
        """Sanitize Azure resource identifiers."""
        sanitized = text

        # Azure subscription IDs (GUIDs)
        subscription_matches = self.azure_subscription_pattern.findall(sanitized)
        if subscription_matches:
            self.sanitization_log.append(f"Removed {len(subscription_matches)} Azure subscription ID(s)")
            if preserve:
                self.private_data['azure_subscriptions'].extend(subscription_matches)
            sanitized = self.azure_subscription_pattern.sub('[REDACTED-AZURE-SUBSCRIPTION-ID]', sanitized)

        # Azure resource group names
        rg_matches = self.azure_resource_group_pattern.findall(sanitized)
        if rg_matches:
            self.sanitization_log.append(f"Removed {len(rg_matches)} Azure resource group name(s)")
            if preserve:
                self.private_data['azure_resources'].extend([f"resourceGroups/{rg}" for rg in rg_matches])
            sanitized = self.azure_resource_group_pattern.sub(r'resourceGroups/[REDACTED-RESOURCE-GROUP]', sanitized)

        # Azure storage accounts
        storage_matches = self.azure_storage_account_pattern.findall(sanitized)
        if storage_matches:
            self.sanitization_log.append(f"Removed {len(storage_matches)} Azure storage account name(s)")
            if preserve:
                self.private_data['azure_resources'].extend(storage_matches)
            sanitized = self.azure_storage_account_pattern.sub('[REDACTED-STORAGE].blob.core.windows.net', sanitized)

        # Generic Azure resource URLs
        azure_resource_matches = self.azure_resource_name_pattern.findall(sanitized)
        if azure_resource_matches:
            self.sanitization_log.append(f"Removed {len(azure_resource_matches)} Azure resource URL(s)")
            if preserve:
                self.private_data['azure_resources'].extend(azure_resource_matches)
            sanitized = self.azure_resource_name_pattern.sub('.[REDACTED-AZURE-RESOURCE].net', sanitized)

        return sanitized

    def _sanitize_urls_and_paths(self, text: str, preserve: bool) -> str:
        """Sanitize internal URLs and file paths."""
        sanitized = text

        # Internal URLs
        internal_url_matches = self.internal_url_pattern.findall(sanitized)
        if internal_url_matches:
            self.sanitization_log.append(f"Removed {len(internal_url_matches)} internal URL(s)")
            if preserve:
                self.private_data['internal_urls'].extend(internal_url_matches)
            sanitized = self.internal_url_pattern.sub('[REDACTED-INTERNAL-URL]', sanitized)

        # Windows file paths
        windows_path_matches = self.windows_path_pattern.findall(sanitized)
        if windows_path_matches:
            self.sanitization_log.append(f"Removed {len(windows_path_matches)} Windows file path(s)")
            if preserve:
                self.private_data['file_paths'].extend(windows_path_matches)
            sanitized = self.windows_path_pattern.sub('[REDACTED-WINDOWS-PATH]', sanitized)

        # UNC paths
        unc_path_matches = self.unc_path_pattern.findall(sanitized)
        if unc_path_matches:
            self.sanitization_log.append(f"Removed {len(unc_path_matches)} UNC path(s)")
            if preserve:
                self.private_data['file_paths'].extend(unc_path_matches)
            sanitized = self.unc_path_pattern.sub('[REDACTED-UNC-PATH]', sanitized)

        # Unix internal paths
        unix_path_matches = self.unix_internal_path_pattern.findall(sanitized)
        if unix_path_matches:
            self.sanitization_log.append(f"Removed {len(unix_path_matches)} Unix internal path(s)")
            if preserve:
                self.private_data['file_paths'].extend(unix_path_matches)
            sanitized = self.unix_internal_path_pattern.sub('[REDACTED-UNIX-PATH]', sanitized)

        return sanitized

    def _sanitize_pii(self, text: str, preserve: bool) -> str:
        """Sanitize personally identifiable information."""
        sanitized = text

        # Email addresses
        email_matches = self.email_pattern.findall(sanitized)
        if email_matches:
            self.sanitization_log.append(f"Removed {len(email_matches)} email address(es)")
            if preserve:
                self.private_data['emails'].extend(email_matches)
            sanitized = self.email_pattern.sub('[REDACTED-EMAIL]', sanitized)

        # IPv4 addresses (exclude common non-sensitive ones like 127.0.0.1)
        ipv4_matches = [ip for ip in self.ipv4_pattern.findall(sanitized)
                        if ip not in ['127.0.0.1', '0.0.0.0', '255.255.255.255']]
        if ipv4_matches:
            self.sanitization_log.append(f"Removed {len(ipv4_matches)} IP address(es)")
            if preserve:
                self.private_data['ip_addresses'].extend(ipv4_matches)
            for ip in ipv4_matches:
                sanitized = sanitized.replace(ip, '[REDACTED-IP]')

        # IPv6 addresses
        ipv6_matches = self.ipv6_pattern.findall(sanitized)
        if ipv6_matches:
            self.sanitization_log.append(f"Removed {len(ipv6_matches)} IPv6 address(es)")
            if preserve:
                self.private_data['ip_addresses'].extend(ipv6_matches)
            sanitized = self.ipv6_pattern.sub('[REDACTED-IPV6]', sanitized)

        return sanitized

    def get_private_data(self) -> Dict[str, List[str]]:
        """
        Get all private data that was removed during sanitization.

        Returns:
            Dictionary categorizing all removed private information
        """
        return self.private_data.copy()

    def reset(self):
        """Reset sanitization log and private data tracking."""
        self.sanitization_log = []
        self.private_data = {
            'emails': [],
            'ip_addresses': [],
            'internal_urls': [],
            'file_paths': [],
            'credentials': [],
            'azure_subscriptions': [],
            'azure_resources': []
        }

    def get_sanitization_summary(self) -> str:
        """
        Get a human-readable summary of sanitization actions.

        Returns:
            Formatted summary string
        """
        if not self.sanitization_log:
            return "No sanitization performed"

        summary_lines = ["Sanitization Summary:", ""]
        for log_entry in self.sanitization_log:
            summary_lines.append(f"  - {log_entry}")

        total_items = sum(len(items) for items in self.private_data.values())
        summary_lines.append("")
        summary_lines.append(f"Total items redacted: {total_items}")

        return "\n".join(summary_lines)


# Convenience function
def sanitize_for_public_disclosure(text: str) -> Tuple[str, str]:
    """
    Convenience function to sanitize text for public disclosure.

    Args:
        text: Input text to sanitize

    Returns:
        Tuple of (sanitized_text, sanitization_summary)
    """
    sanitizer = Sanitizer()
    sanitized_text, _ = sanitizer.sanitize_text(text)
    summary = sanitizer.get_sanitization_summary()
    return sanitized_text, summary
