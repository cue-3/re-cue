"""
CommunicationPatternDetector - Analysis component.
"""

import re
from pathlib import Path

from ...utils import log_info


class CommunicationPatternDetector:
    """Detects communication patterns between system components."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose

        # Communication pattern definitions
        self.rest_patterns = [
            r"RestTemplate|WebClient|@FeignClient",
            r"HttpClient|OkHttpClient",
            r"@RestController.*@RequestMapping",
            r"retrofit2?\.",
        ]

        self.messaging_patterns = [
            r"@RabbitListener|@KafkaListener|@JmsListener",
            r"RabbitTemplate|KafkaTemplate|JmsTemplate",
            r"@SendTo|@MessageMapping",
            r"MessageProducer|MessageConsumer",
        ]

        self.database_patterns = [
            r"@Repository|@Entity|@Table",
            r"JdbcTemplate|JpaRepository",
            r"EntityManager|SessionFactory",
            r"@Query\(",
        ]

        self.event_patterns = [
            r"@EventListener|@EventHandler",
            r"ApplicationEventPublisher",
            r"@DomainEvent|@TransactionalEventListener",
            r"EventBus|EventPublisher",
        ]

    def detect_communication_patterns(self, java_files):
        """Detect all communication patterns in the codebase."""
        communications = []

        for java_file in java_files:
            try:
                content = java_file.read_text()

                # Detect REST communications
                rest_comms = self._detect_rest_communications(java_file, content)
                communications.extend(rest_comms)

                # Detect messaging
                messaging_comms = self._detect_messaging_communications(java_file, content)
                communications.extend(messaging_comms)

                # Detect database interactions
                db_comms = self._detect_database_communications(java_file, content)
                communications.extend(db_comms)

                # Detect event-driven patterns
                event_comms = self._detect_event_communications(java_file, content)
                communications.extend(event_comms)

            except Exception:
                continue

        return communications

    def _detect_rest_communications(self, java_file, content):
        """Detect REST API calls between services."""
        communications = []

        for pattern in self.rest_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Try to extract target URL
                url_pattern = r'["\']https?://([^/"\'\s]+)[^"\']*["\']'
                urls = re.findall(url_pattern, content)

                for url in urls:
                    if not any(local in url for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
                        communications.append(
                            {
                                "source": java_file.stem,
                                "target": url,
                                "type": "rest_call",
                                "mechanism": "HTTP/REST",
                                "file": java_file.name,
                            }
                        )
                        if self.verbose:
                            log_info(f"  Found REST call: {java_file.stem} → {url}", self.verbose)

                # Also detect service-to-service calls via service names
                feign_match = re.search(
                    r'@FeignClient\([^)]*name\s*=\s*["\']([^"\']+)["\']', content
                )
                if feign_match:
                    service_name = feign_match.group(1)
                    communications.append(
                        {
                            "source": java_file.stem,
                            "target": service_name,
                            "type": "service_call",
                            "mechanism": "Feign/REST",
                            "file": java_file.name,
                        }
                    )
                    if self.verbose:
                        log_info(
                            f"  Found Feign client: {java_file.stem} → {service_name}", self.verbose
                        )

        return communications

    def _detect_messaging_communications(self, java_file, content):
        """Detect message queue communications."""
        communications = []

        for pattern in self.messaging_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract queue/topic names
                queue_pattern = r'[@(](?:queue|destination|topic)\s*=\s*["\']([^"\']+)["\']'
                queues = re.findall(queue_pattern, content, re.IGNORECASE)

                for queue in queues:
                    communications.append(
                        {
                            "source": java_file.stem,
                            "target": queue,
                            "type": "message_queue",
                            "mechanism": "Message Queue",
                            "file": java_file.name,
                        }
                    )
                    if self.verbose:
                        log_info(f"  Found message queue: {java_file.stem} → {queue}", self.verbose)

        return communications

    def _detect_database_communications(self, java_file, content):
        """Detect database interactions."""
        communications = []

        for pattern in self.database_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract entity/table names
                table_match = re.search(r'@Table\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
                if table_match:
                    table_name = table_match.group(1)
                    communications.append(
                        {
                            "source": java_file.stem,
                            "target": f"Table: {table_name}",
                            "type": "database_access",
                            "mechanism": "JPA/JDBC",
                            "file": java_file.name,
                        }
                    )

        return communications

    def _detect_event_communications(self, java_file, content):
        """Detect event-driven communications."""
        communications = []

        for pattern in self.event_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract event types
                event_pattern = r"@EventListener\([^)]*([A-Z]\w+Event)[^)]*\)"
                events = re.findall(event_pattern, content)

                for event in events:
                    communications.append(
                        {
                            "source": java_file.stem,
                            "target": event,
                            "type": "event_driven",
                            "mechanism": "Event Bus",
                            "file": java_file.name,
                        }
                    )
                    if self.verbose:
                        log_info(
                            f"  Found event listener: {java_file.stem} → {event}", self.verbose
                        )

        return communications
