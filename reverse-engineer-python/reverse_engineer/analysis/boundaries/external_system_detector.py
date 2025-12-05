"""
ExternalSystemDetector - Analysis component.
"""

import re
from pathlib import Path
from typing import Any, Optional

from ...utils import log_info


class ExternalSystemDetector:
    """Detects external systems and third-party integrations."""

    def __init__(self, verbose: bool = False):
        """Initialize the external system detector."""
        self.verbose = verbose

        # Patterns for detecting external system integrations
        self.integration_patterns = {
            "rest_client": re.compile(
                r"@RestTemplate|WebClient|RestClient|HttpClient|OkHttpClient", re.IGNORECASE
            ),
            "message_queue": re.compile(
                r"@RabbitListener|@KafkaListener|@JmsListener|MessageProducer|@Queue", re.IGNORECASE
            ),
            "database_external": re.compile(r"jdbc:[^:]+://([^/:]+)", re.IGNORECASE),
            "web_service": re.compile(
                r"@WebServiceClient|@Service.*Client|SoapClient", re.IGNORECASE
            ),
            "cache_system": re.compile(
                r"@Cacheable|RedisTemplate|JedisPool|HazelcastInstance", re.IGNORECASE
            ),
            "payment_gateway": re.compile(
                r"stripe|paypal|square|braintree|worldpay", re.IGNORECASE
            ),
            "notification": re.compile(r"twilio|sendgrid|mailgun|sns|ses", re.IGNORECASE),
            "cloud_services": re.compile(r"amazonaws|azure|gcp|firebase|cloudinary", re.IGNORECASE),
        }

        # URL patterns for common services
        self.url_patterns = {
            "stripe": re.compile(r"api\.stripe\.com", re.IGNORECASE),
            "paypal": re.compile(r"api\.paypal\.com|api\.sandbox\.paypal\.com", re.IGNORECASE),
            "twilio": re.compile(r"api\.twilio\.com", re.IGNORECASE),
            "sendgrid": re.compile(r"api\.sendgrid\.com", re.IGNORECASE),
            "aws": re.compile(r"amazonaws\.com", re.IGNORECASE),
            "github": re.compile(r"api\.github\.com", re.IGNORECASE),
            "slack": re.compile(r"hooks\.slack\.com|slack\.com/api", re.IGNORECASE),
            "google": re.compile(r"googleapis\.com", re.IGNORECASE),
        }

    def detect_external_systems(
        self, java_files: list[Path], config_files: Optional[list[Path]] = None
    ) -> list[dict[str, Any]]:
        """Detect external systems from Java files and configuration."""
        external_systems = []

        # Analyze Java files
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")
                systems = self._analyze_java_file(content, java_file)
                external_systems.extend(systems)

            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze {java_file.name}: {e}")
                continue

        # Analyze configuration files if provided
        if config_files:
            for config_file in config_files:
                try:
                    content = config_file.read_text(encoding="utf-8")
                    systems = self._analyze_config_file(content, config_file)
                    external_systems.extend(systems)

                except Exception as e:
                    if self.verbose:
                        log_info(f"Warning: Could not analyze config {config_file.name}: {e}")
                    continue

        # Deduplicate external systems
        unique_systems = []
        system_names_seen = set()

        for system in external_systems:
            if system["name"] not in system_names_seen:
                system_names_seen.add(system["name"])
                unique_systems.append(system)
            else:
                # Merge evidence
                existing = next(s for s in unique_systems if s["name"] == system["name"])
                for evidence in system["identified_from"]:
                    if evidence not in existing["identified_from"]:
                        existing["identified_from"].append(evidence)

        return unique_systems

    def _analyze_java_file(self, content: str, java_file: Path) -> list[dict[str, Any]]:
        """Analyze Java file for external system integrations."""
        systems = []

        # Check for REST client patterns
        if self.integration_patterns["rest_client"].search(content):
            # Extract URLs to identify specific services
            url_pattern = re.compile(r'["\']https?://([^/"\']+)[^"\']*["\']')
            urls = url_pattern.findall(content)

            for url in urls:
                system_name = self._infer_system_name_from_url(url)
                if system_name:
                    systems.append(
                        {
                            "name": system_name,
                            "type": "external_system",
                            "access_level": "api_integration",
                            "integration_type": "rest_api",
                            "identified_from": [f"REST client in {java_file.name}"],
                        }
                    )
                    if self.verbose:
                        log_info(f"  Found external REST API: {system_name} in {java_file.name}")

        # Check for message queue integrations
        if self.integration_patterns["message_queue"].search(content):
            queue_names = re.findall(r'queue\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            for queue in queue_names:
                system_name = f"Message Queue ({queue})"
                systems.append(
                    {
                        "name": system_name,
                        "type": "external_system",
                        "access_level": "api_integration",
                        "integration_type": "message_queue",
                        "identified_from": [f"Message queue in {java_file.name}"],
                    }
                )
                if self.verbose:
                    log_info(f"  Found message queue: {system_name} in {java_file.name}")

        # Check for external database connections
        db_matches = self.integration_patterns["database_external"].findall(content)
        for db_host in db_matches:
            if not any(local in db_host.lower() for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
                system_name = f"External Database ({db_host})"
                systems.append(
                    {
                        "name": system_name,
                        "type": "external_system",
                        "access_level": "api_integration",
                        "integration_type": "database",
                        "identified_from": [f"Database connection in {java_file.name}"],
                    }
                )
                if self.verbose:
                    log_info(f"  Found external database: {system_name} in {java_file.name}")

        # Check for specific service patterns
        for service_type, pattern in self.integration_patterns.items():
            if service_type in ["payment_gateway", "notification", "cloud_services"]:
                if pattern.search(content):
                    system_name = f"{service_type.replace('_', ' ').title()} Service"
                    systems.append(
                        {
                            "name": system_name,
                            "type": "external_system",
                            "access_level": "api_integration",
                            "integration_type": service_type,
                            "identified_from": [f"{service_type} pattern in {java_file.name}"],
                        }
                    )
                    if self.verbose:
                        log_info(f"  Found {service_type}: {system_name} in {java_file.name}")

        return systems

    def _analyze_config_file(self, content: str, config_file: Path) -> list[dict[str, Any]]:
        """Analyze configuration files for external system references."""
        systems = []

        # Look for external URLs in configuration
        url_pattern = re.compile(r'["\']?https?://([^/"\']+)[^"\']*["\']?')
        urls = url_pattern.findall(content)

        for url in urls:
            if not any(local in url.lower() for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
                system_name = self._infer_system_name_from_url(url)
                if system_name:
                    systems.append(
                        {
                            "name": system_name,
                            "type": "external_system",
                            "access_level": "api_integration",
                            "integration_type": "configuration",
                            "identified_from": [f"Configuration in {config_file.name}"],
                        }
                    )
                    if self.verbose:
                        log_info(
                            f"  Found external system in config: {system_name} in {config_file.name}"
                        )

        # Look for database connection strings
        db_pattern = re.compile(r"jdbc:[^:]+://([^/:]+)", re.IGNORECASE)
        db_hosts = db_pattern.findall(content)

        for db_host in db_hosts:
            if not any(local in db_host.lower() for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
                system_name = f"External Database ({db_host})"
                systems.append(
                    {
                        "name": system_name,
                        "type": "external_system",
                        "access_level": "api_integration",
                        "integration_type": "database",
                        "identified_from": [f"Database config in {config_file.name}"],
                    }
                )
                if self.verbose:
                    log_info(
                        f"  Found external database in config: {system_name} in {config_file.name}"
                    )

        return systems

    def _infer_system_name_from_url(self, url: str) -> Optional[str]:
        """Infer system name from URL."""
        url.lower()

        # Check against known service patterns
        for service, pattern in self.url_patterns.items():
            if pattern.search(url):
                return self._get_service_display_name(service)

        # Generic domain-based naming
        if "." in url:
            domain_parts = url.split(".")

            # Handle common patterns like api.service.com -> Service API
            if len(domain_parts) >= 2:
                if domain_parts[0] == "api":
                    service_name = domain_parts[1].title()
                    return f"{service_name} API"
                else:
                    # Use the main domain name
                    main_domain = domain_parts[-2] if len(domain_parts) > 1 else domain_parts[0]
                    return f"{main_domain.title()} Service"

        return None

    def _get_service_display_name(self, service: str) -> str:
        """Get display name for known services."""
        service_names = {
            "stripe": "Stripe Payment Gateway",
            "paypal": "PayPal Payment Gateway",
            "twilio": "Twilio SMS Service",
            "sendgrid": "SendGrid Email Service",
            "aws": "AWS Services",
            "github": "GitHub API",
            "slack": "Slack Integration",
            "google": "Google APIs",
        }

        return service_names.get(service, f"{service.title()} Service")
