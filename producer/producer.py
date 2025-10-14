import time, random, uuid, socket
from datetime import datetime, timezone
from typing import Dict, Any

from faker import Faker
import orjson as json
from confluent_kafka import Producer

fake = Faker()

BROKER = "kafka:29092"
TOPIC = "gcp_audit_logs"
PROJECTS = [f"demo-{i:03d}" for i in range(1, 6)]  # projects/demo-001 … demo-005
ENVS = ["dev", "stg", "prod"]

# A small but realistic set of services/methods that generate Admin Activity logs
SERVICES_METHODS = {
    "iam.googleapis.com": [
        "SetIamPolicy",
        "CreateServiceAccount",
        "DeleteServiceAccount",
        "UndeleteServiceAccount",
        "UpdateServiceAccount",
        "CreateRole",
        "UpdateRole",
        "DeleteRole",
        "GrantServiceAccountKey",
    ],
    "compute.googleapis.com": [
        "v1.compute.instances.insert",
        "v1.compute.instances.delete",
        "v1.compute.instances.setMetadata",
        "v1.compute.disks.createSnapshot",
        "v1.compute.firewalls.insert",
        "v1.compute.firewalls.patch",
    ],
    "storage.googleapis.com": [
        "storage.buckets.create",
        "storage.buckets.delete",
        "storage.buckets.setIamPolicy",
        "storage.objects.update",
    ],
    "cloudresourcemanager.googleapis.com": [
        "SetIamPolicy",
        "CreateProject",
        "DeleteProject",
        "UndeleteProject",
        "UpdateProject",
    ],
    "container.googleapis.com": [
        "io.k8s.core.v1.namespaces.create",
        "io.k8s.core.v1.namespaces.delete",
        "io.k8s.apps.v1.deployments.patch",
        "google.container.v1.ClusterManager.CreateCluster",
        "google.container.v1.ClusterManager.UpdateCluster",
    ],
    "bigquery.googleapis.com": [
        "google.cloud.bigquery.v2.JobService.InsertJob",
        "google.cloud.bigquery.v2.DatasetService.InsertDataset",
        "google.cloud.bigquery.v2.DatasetService.PatchDataset",
        "google.cloud.bigquery.v2.TableService.InsertTable",
        "google.cloud.bigquery.v2.TableService.PatchTable",
    ],
    "kms.googleapis.com": [
        "UpdateCryptoKeyPrimaryVersion",
        "CreateCryptoKey",
        "DestroyCryptoKeyVersion",
        "RestoreCryptoKeyVersion",
        "SetIamPolicy",
    ],
}

SEVERITIES = ["INFO", "NOTICE", "WARNING", "ERROR"]
# google.rpc.Code: 0 OK, 5 NOT_FOUND, 7 PERMISSION_DENIED, 8 RESOURCE_EXHAUSTED
STATUS_CODES = [(0, "OK"), (7, "PERMISSION_DENIED"), (5, "NOT_FOUND"), (8, "RESOURCE_EXHAUSTED")]
STATUS_WEIGHTS = [0.91, 0.05, 0.03, 0.01]
SEVERITY_WEIGHTS = [0.72, 0.15, 0.09, 0.04]

p = Producer({
    "bootstrap.servers": BROKER,
    "client.id": socket.gethostname(),
    "enable.idempotence": False,
    "acks":"1"
})

def pick_service_and_method():
    service = random.choice(list(SERVICES_METHODS.keys()))
    method = random.choice(SERVICES_METHODS[service])
    return service, method

def make_resource_name(service: str, project: str) -> str:
    # Minimal heuristics to make resourceNames look right per service
    if service == "compute.googleapis.com":
        return f"projects/{project}/zones/{random.choice(['us-central1-a','asia-southeast1-b','europe-west1-c'])}/instances/vm-{random.randint(1,9999)}"
    if service == "storage.googleapis.com":
        return f"projects/_/buckets/bucket-{random.randint(1,200)}"
    if service == "iam.googleapis.com":
        return f"projects/{project}/serviceAccounts/sa-{random.randint(1,300)}@{project}.iam.gserviceaccount.com"
    if service == "cloudresourcemanager.googleapis.com":
        return f"projects/{project}"
    if service == "container.googleapis.com":
        return f"projects/{project}/locations/{random.choice(['us-central1','asia-southeast1'])}/clusters/cluster-{random.randint(1,40)}"
    if service == "bigquery.googleapis.com":
        return f"projects/{project}/datasets/ds_{random.randint(1,80)}/tables/t_{random.randint(1,800)}"
    if service == "kms.googleapis.com":
        return f"projects/{project}/locations/global/keyRings/kr-1/cryptoKeys/key-{random.randint(1,20)}"
    return f"projects/{project}/resources/{uuid.uuid4()}"

def diurnal_weight() -> float:
    """Return a multiplier to mimic daily traffic patterns (UTC hour)."""
    hour = datetime.now(timezone.utc).hour
    # Busy during 07–12 UTC and 20–02 UTC (example)
    if 7 <= hour <= 12 or hour >= 20 or hour <= 2:
        return random.uniform(0.8, 1.2)
    return random.uniform(0.2, 0.6)

def make_admin_activity_event() -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    project = random.choice(PROJECTS)
    env = random.choice(ENVS)
    service, method = pick_service_and_method()
    resource = make_resource_name(service, project)

    code, code_label = random.choices(STATUS_CODES, weights=STATUS_WEIGHTS, k=1)[0]
    severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS, k=1)[0]

    principal = random.choice([
        f"alice@{project}.example.com",
        f"bob@{project}.example.com",
        f"svc-{random.randint(1,30):02d}@{project}.iam.gserviceaccount.com",
        f"platform-admin@example.com",
    ])

    request_id = str(uuid.uuid4())

    event = {
        "insertId": request_id[:16],  # GCP often has insertId for dedupe
        "logName": f"projects/{project}/logs/cloudaudit.googleapis.com%2Factivity",
        "resource": {
            "type": "audited_resource",
            "labels": {"project_id": project, "service": service, "env": env},
        },
        "timestamp": now,
        "severity": severity,
        "receiveTimestamp": now,
        "protoPayload": {
            "@type": "type.googleapis.com/google.cloud.audit.AuditLog",
            "serviceName": service,
            "methodName": method,
            "resourceName": resource,
            "authenticationInfo": {
                "principalEmail": principal
            },
            "requestMetadata": {
                "callerIp": fake.ipv4_public(),
                "callerSuppliedUserAgent": fake.user_agent(),
                "requestAttributes": {"time": now},
            },
            "request": {
                # Small, service-agnostic request stub (safe fields)
                "requestId": request_id,
                "labels": {"env": env},
            },
            "response": {
                # Not always present in real logs, but useful for demo
                "result": "ACK" if code == 0 else "NACK",
            },
            "status": {
                "code": code,           # 0==OK
                "message": code_label,  # human-friendly
            },
            "numResponseItems": 1
        },
        "trace": f"projects/{project}/traces/{uuid.uuid4()}",
        "labels": {
            "compute.googleapis.com/resource_name": resource.split("/")[-1]
        }
    }
    return event, principal  # use principal as Kafka key for locality

def delivery(err, msg):
    if err:
        print("❌ delivery failed:", err)

def run(rate_per_sec: int = 300, jitter: bool = True, bursty: bool = True):
    """
    rate_per_sec: base send rate
    jitter: randomize inter-message sleep
    bursty: occasionally send mini-bursts
    """
    base_interval = 1.0 / max(rate_per_sec, 1)
    last_burst = time.time()
    while True:
        # Occasional burst every ~20–40 seconds
        burst = 1
        if bursty and time.time() - last_burst > random.uniform(20, 40):
            burst = random.randint(20, 100)
            last_burst = time.time()

        # Diurnal modulation
        mod = diurnal_weight()
        interval = base_interval / max(0.1, mod)

        for _ in range(burst):
            event, key = make_admin_activity_event()
            p.produce(
                TOPIC,
                key=key.encode(),
                value=json.dumps(event),
                on_delivery=delivery,
            )
            p.poll(0.5)

            sleep_for = interval * (random.uniform(0.5, 1.6) if jitter else 1.0)
            time.sleep(sleep_for)

if __name__ == "__main__":
    # Tune this up/down depending on your laptop & broker
    run(rate_per_sec=250, jitter=True, bursty=True)