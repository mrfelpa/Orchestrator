from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
import psutil
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
import threading
from datetime import timedelta, datetime
from enum import Enum
import logging
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class MetricsData:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    last_updated: datetime

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    IBM = "ibm"

class CacheManager:
  
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()

    def get(self, key: str) -> Any:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return value
                else:
                    del self.cache[key]
            return None

    def set(self, key: str, value: Any):
        with self.lock:
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            self.cache[key] = (value, datetime.now())

class MultiCloudOrchestrator:
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics: Dict[str, MetricsData] = {}
        self.retry_config = {
            'stop': stop_after_attempt(3),
            'wait': wait_exponential(multiplier=1, min=4, max=10)
        }
        self.credentials = {}  
        self.clients = {}  

    @retry(**self.retry_config)
    def _initialize_clients(self):
        for provider in self.credentials:
            try:
                self._validate_provider_credentials(provider)
                logger.info(f"Client initialized for {provider}")
            except Exception as e:
                logger.error(f"Error initializing client for {provider}: {str(e)}")
                raise  

    def _validate_provider_credentials(self, provider: CloudProvider) -> None:
        required_fields = {
            CloudProvider.AWS: ['access_key', 'secret_key', 'region'],
            CloudProvider.AZURE: ['tenant_id', 'client_id', 'client_secret', 'subscription_id'],
            CloudProvider.GCP: ['project_id', 'key_file'],
            CloudProvider.ORACLE: ['user', 'private_key', 'tenancy', 'region'],
            CloudProvider.IBM: ['api_key']
        }

        if provider not in required_fields:
            raise ValueError(f"Unsupported provider: {provider}")

        missing_fields = [field for field in required_fields[provider] if field not in self.credentials.get(provider, {})]

        if missing_fields:
            raise ValueError(f"Missing required fields for {provider}: {', '.join(missing_fields)}")

    @lru_cache(maxsize=128)
    def get_resource_details(self, provider: CloudProvider, resource_id: str) -> dict:
        cache_key = f"{provider}:{resource_id}"
        cached_data = self.cache_manager.get(cache_key)

        if cached_data:
            return cached_data

        details = self._fetch_resource_details(provider, resource_id)
        self.cache_manager.set(cache_key, details)

        return details

    @retry(**self.retry_config)
    def _fetch_resource_details(self, provider: CloudProvider, resource_id: str) -> dict:
        try:
            if provider == CloudProvider.AWS and resource_id.startswith('i-'):
                response = self.clients[provider]['ec2'].describe_instances(InstanceIds=[resource_id])
                return response['Reservations'][0]['Instances'][0]
            elif provider == CloudProvider.AZURE:
                pass
            elif provider == CloudProvider.GCP:
                pass
            elif provider == CloudProvider.ORACLE:
                pass
            elif provider == CloudProvider.IBM:
                pass
            else:
                raise NotImplementedError(f"Fetch logic for {provider} is not implemented.")
        except Exception as e:
            logger.error(f"Error fetching resource details: {str(e)}")
            raise

    def collect_metrics(self, provider: CloudProvider) -> MetricsData:
        try:
            metrics = MetricsData(
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                last_updated=datetime.now()
            )
            self.metrics[provider.value] = metrics
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            raise

    def _validate_resource_exists(self, provider: CloudProvider, resource_id: str) -> bool:
        try:
            self.get_resource_details(provider, resource_id)
            return True
        except Exception as e:
            logger.error(f"Resource {resource_id} not found in provider {provider}: {str(e)}")
            return False

orchestrator = MultiCloudOrchestrator()

app = typer.Typer()
console = Console()

@app.command()
def monitor(
    provider: Optional[CloudProvider] = typer.Option(None, help="Specific provider to monitor"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Refresh metrics in real-time")
):
    try:
        providers = [provider] if provider else list(CloudProvider)

        while True:
            table = Table(title="Resource Monitoring Dashboard")
            table.add_column("Provider", style="cyan", justify="center")
            table.add_column("Active Resources", style="green", justify="center")
            table.add_column("CPU %", style="yellow", justify="center")
            table.add_column("Memory %", style="yellow", justify="center")
            table.add_column("Disk %", style="yellow", justify="center")
            table.add_column("Est. Cost (USD)", style="red", justify="center")

            for p in providers:
                if orchestrator._validate_provider_credentials(p):
                    metrics = orchestrator.collect_metrics(p)
                    active_resources_count = 10  

                    table.add_row(
                        p.value,
                        str(active_resources_count),
                        f"{metrics.cpu_percent:.1f}%",
                        f"{metrics.memory_percent:.1f}%",
                        f"{metrics.disk_usage:.1f}%",
                        "$100.00"  
                    )

            console.clear()
            console.print(Panel(table, title="Live Cloud Resource Monitoring", title_align="left"))

            if not refresh:
                break

            for _ in track(range(5), description="[cyan]Refreshing in seconds..."):
                time.sleep(1)

    except Exception as e:
        console.print(f"[red]Error in monitoring: {str(e)}[/red]")

if __name__ == "__main__":
    app()
