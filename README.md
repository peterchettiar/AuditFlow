# AuditFlow
> Real-time Detection of Privileged Access Anomalies in Streaming Audit Logs

### ✨ Tagline

_**“Stream. Detect. Protect.”**_

AuditFlow continuously ingests system and cloud audit logs, identifies unauthorized privileged access, and assigns confidence scores using AI-driven anomaly detection — all in real time.

## 📊 Overview

AuditFlow is an open-source data engineering project that integrates **streaming pipelines, cloud audit logs and AI-based scoring** to detect abnormal priviledged access activities.

The system simulates or consumes live audit events (e.g., AWS CloudTrail, Linux auth logs), transforms them into structured datasets, and applies **rule-based + ML** scoring to flag anomalies such as:

- Unauthorized logins or sudo usage
- Unexpected admin policy updates
- Key or role creations outside normal hours
- Access from unfamiliar IPs or regions

`AuditFlow` combines Kafka, Spark, and a modern data warehouse for end-to-end observability.

## 🧩 Environment Setup

Since this is a brand new project, best is to implement everything that we have learnt so far from scratch for practice purposes which includes the setting up of a new VM under a new project from GCP. 

A comprehensive guide for setting up a VM instance on GCP can be found in this [github gist](https://gist.github.com/peterchettiar/6e719cd2bbdb3e6aae4e6d1895670687). But for a summarised version (especially for those that already have a GCP account and google cloud SDK setup), to set up a new project, you have to:
1. Create a new project
    - Go to [cloud console](http://console.cloud.google.com), log into GCP and in the project directory in the top left box click `create new project`
    - Give your project a name, I gave mine `audit-flow`, given its the inspiration of the project.
    - For Location field, leave it as the default.

2. Create `.ssh` key
    - On your local machine, open terminal and go to your `.ssh` folder (create one if its your first time)
    - Run `ssh-keygen -t rsa -f ~/.ssh/audit-flow -C peter_chettiar -b 2048` - this is to generate the SSH key pair to connect to VM using SSH (ignore pass phrase by pressing enter)
    - Now that we have generated the private and public keys, run command `cat audit-flow.pub | pbcopy` to copy the contents of the public key
    - Next we want to input the public key details as a new SSH key into GCP -> Navigate to Compute engine -> Settings -> Metadata -> SSH Keys, and then add copied details. (Remember to enable the compute engine API before doing do)

3. Create VM
    - Type `Create an instance` in your search bar and this would navigate you to the page where you create your instance
    - Give it a name, I’m just going to call it `audit-flow`
    - Set region as `Asia-southeast1-c` - that was for me but pick server closest to your location
    - Machine type, I selected `e2-medium` - simple project so I chose a small and basic machine

4. SSH into VM
    - You can ssh using `ssh -i ~/.ssh/audit-flow peter-chettiar@34.126.89.50` 
    - But this is a cumbersome process, so we can setup a config file to make it easier
  	```bash
	Host audit-flow
		 HostName 34.126.140.229
		 user peter_chettiar
		 IdentityFile ~/.ssh/audit-flow
	```
    - If you have multiple projects, make sure you change the active GCP project using the `gcloud` CLI - run `gcloud config set project PROJECT_ID`
    - Also, it is worth increasing the boot disk space (default given to me was 10GB, not enough to install anaconda on VM) - run `gcloud compute disks resize audit-flow --size=100GB --zone=asia-southeast1-c` to change the boot disk size from 10GB to 100GB
    - Now to simply `ssh audit-flow`!
  
5. Install Anaconda
    - Run `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh` to download anaconda into your VM home directory, after which run `bash Miniconda3-latest-Linux-x86_64.sh` to install anaconda.
    - Remove the installer after installation.
  
6. Uploading google credentials
    - First we need to go to service accounts page and click on the default compute engine service account, and then create a new key for this service account.
    - The key is a .json file that would be downloaded into your local downloads folder
    - What we need to do next is to upload this .json file into a directory in your VM instance. 
    - The .json file contains credentials allowing programmatic access to GCP services, on behalf of a service account.
    - Create a folder called .gc in your home directory, and move the .json file there followed by changing directory into the .gc folder - `mkdir ~/.gc | mv ~/Downloads/audit-flow-474406-401e676e7ab0.json . | cd ~/.gc`
    - Next, from the current working directory run `sftp audit-flow ` to connect to the home directory of the VM instance (make sure you have started instance and have changed the external IP to your config file)
    - Again, in your home directory of your VM instance, create a `.gc` folder and run sftp command in local home directory`put audit-flow-474406-401e676e7ab0.json .gc/` inside the folder to copy the .json file into this new directory from local machine directory
    - Now that’s done we can create an environment variable to specify the path to this google credentials .json file for authentication purposes for google cloud services. For that, in `.bashrc`file write `export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/audit-flow-474406-401e676e7ab0.json`
    - Laslty, run `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS` to activate the service account credentials.
  
7. Clone Github Repository 
    - Run `ssh-keygen -t ed25519 -C "peterchet2308@outlook.com"` in home directory of VM instance to generate SSH keys for GitHub.
    - Copy public key from `.ssh` folder and upload it into Github
    - Then git clone the AuditFlow repository.
    - Please note that if you need to install `git` you need to run `sudo apt install -y git` assuming your OS for your VM is "Debian GNU/Linux".
  
8. Install Docker
    - Run `sudo apt-get install docker.io` to install docker
    - Next, we need to add our user to user group in docker so that we don’t need to run docker commands as sudo user:
        - Run `sudo grouped docker` - create the docker group if it does not exist
        - Run `sudo usermod -aG docker $USER` to add user into group
        - Run `newgrp docker` to update the changes made to group
        - Run `docker run hello-world` to test
     
9. Install Docker-Compose
    - Run `wget https://github.com/docker/compose/releases/download/v2.35.0/docker-compose-linux-x86_64 -O docker-compose` to download the binaries for docker-compose while also changing the output name to docker-compose as well.
    - Next, we change the output into an executable using `chmod +x docker-compose`
    - Now to set the `PATH` for the docker-compose executable - in `.bashrc` file insert `export PATH="${HOME}/bin:${PATH}”`, followed by `source .bashrc` for the changes to take effect
    - Run `docker-compose —-version` to see if the docker-compose command tool works.
  
## 🧾 Dataset: Simulated GCP Audit Logs

This project uses a **synthetic dataset modelled after Google Cloud Platform (GCP) audit logs** as the primary streaming data source. What distinguishes an audit log entry from other log entries is the `protoPayload` field in the log entry. These logs emulate real-world cloud activity events that capture administrative operations across GCP services such as IAM, Compute Engine, Cloud Storage, BigQuery, and KMS.

### Google Cloud Audit Log Types

The different types of audit logs are as follows:

| **Log Type** | **Triggered By** | **Configurable** | **Default State** | **Example Use Case** | **Key Notes** |
|---------------|------------------|------------------|-------------------|----------------------|----------------|
| **Admin Activity** | User-driven configuration or metadata changes | ❌ No | ✅ Always enabled | Creating or deleting VM instances, updating IAM permissions | Logs persist even if the Cloud Logging API is disabled |
| **Data Access** | Read or write operations on resource data or metadata | ✅ Yes | 🚫 Disabled (except BigQuery) | Reading Cloud Storage objects, running BigQuery queries | May generate large log volumes and incur additional costs; doesn’t log public access (`allUsers`, `allAuthenticatedUsers`) |
| **System Event** | Automatic system actions that modify resource configuration | ❌ No | ✅ Always enabled | Autoscaling adds/removes VMs, system-managed configuration updates | Tracks non-user (system) operations; cannot be disabled |
| **Policy Denied** | Access requests denied by IAM or organization policy | ⚙️ Excludable (cannot disable) | ✅ Always enabled | User denied access due to missing permissions or policy restrictions | Useful for security monitoring and policy enforcement; storage incurs cost |

#### Notes
- **Admin Activity** and **System Event** logs are *always written* and cannot be disabled.  
- **Data Access** logs must be *explicitly enabled* per service (except BigQuery).  
- **Policy Denied** logs are *always generated*, but you can exclude them from storage to reduce costs.  
- All audit logs can be routed to **BigQuery**, **Pub/Sub**, or **Cloud Storage** for analysis or long-term archiving.

### Scope and Simulation Notes

This project aims to simulate Google Cloud audit logs for the purpose of building, testing, and learning from a real-time data engineering pipeline. Because we are generating synthetic data rather than pulling from a live production environment, fully replicating the depth and variability of real-world audit activity presents several challenges — including user diversity, resource complexity, and inter-service dependencies.  

Hence, to keep the simulation focused, we will limit the scope to **Admin Activity** audit logs, as it is the category of audit logs that most directly reflect user-driven operations and data interactions across GCP services.

### Targeted GCP Services
To maintain realism while ensuring the dataset remains lightweight and manageable, we will simulate log events only for **commonly used GCP services**, including:
The simulation will emulate audit log activity for a select set of commonly used services that demonstrate realistic patterns of configuration and data access:

| **Service** | **Purpose** | **Example Actions Simulated** |
|--------------|--------------|--------------------------------|
| **Compute Engine** | Infrastructure management | `compute.instances.insert`, `compute.instances.delete`, `compute.instances.get` |
| **BigQuery** | Analytical data operations | `bigquery.jobs.query`, `bigquery.tables.get`, `bigquery.datasets.create` |
| **Cloud IAM** | Identity and access management | `iam.roles.create`, `iam.serviceAccounts.update`, `setIamPolicy` |

These services collectively cover the most common admin-related activities in a Google Cloud environment, providing a realistic yet manageable simulation scope. The services mentioned above are not exhaustive, and there would be more service methods that would be included in the data simulation script. Also, the following is a real-life example of a admin activity audit log (ideally this is what we want to achieve!):

<img width="498" height="536" alt="image" src="https://github.com/user-attachments/assets/b6a62327-8bf8-4367-96aa-f2c7913e33c9" />

### Simulation Design
The simulation will generate log events that loosely follow Google Cloud’s [audit log format]([https://cloud.google.com/logging/docs/audit](https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog)) with key fields such as:
- `timestamp` – when the simulated event occurred  
- `protoPayload.methodName` – API call or action performed  
- `resource.type` – target GCP service or resource  
- `severity` – log level (e.g., INFO, NOTICE, WARNING)  
- `authenticationInfo.principalEmail` – simulated user identity  
- `requestMetadata.callerIp` – pseudo-randomized IP for contextual realism  

Events will be **streamed into Kafka** to mimic the continuous flow of operational logs from GCP into `BigQuery`.  
The focus is on creating a realistic data pipeline that enables testing of:
- **Stream ingestion and transformation**  
- **Data quality validation and schema enforcement**  
- **Real-time monitoring and alerting**  

## ⚙️ Methodology - Python Generator

The [producer.py](https://github.com/peterchettiar/AuditFlow/blob/main/producer/producer.py) script is a synthetic audit-log producer:
> It _creates fake JSON log events in memory_ and sends (produces) them continuously into a kafka topic called `gcp_audit_logs`

Kafka acts as the streaming backbone - a distributed log (message broker) that stores these events for downstream consumers. So you can think of it like this:
```txt
Python generator → Kafka Producer API → Kafka Broker → Topic: gcp_audit_logs → Consumers
```

Let's do a step-by-step breakdown of the generator script:
### 1. Library Setup
```python
from faker import Faker
import orjson as json
from confluent_kafka import Producer
```

- Faker : Creates realistic fake data - IPs, user agents, etc.
- orjson : Python Library that performs way faster than python native JSON library. Helps with the serialization of python objects (i.e. event dictionary) being generated into JSON data.
- confluent_kafka.Producer : Putting data into Kafka with a producer. Producers sends a produce request with records to the log, and each record, as it arrives, is given a special number called _offset_, which is a logical position of that record in the log. A _topic_ is simply a logical construct that names the log.

> Note: We have to use `confluent-kafka` instead of `kafka_streams` as the latter is a Java library.

>[!TIP]
>For those who are new to Kafka, it is a distributed streaming platform that provides a publish-subscribe messaging system. And producers are responsible for publishing messages to a kafka topic.

<img width="512" height="340" alt="image" src="https://github.com/user-attachments/assets/77d3aeb3-9090-43d2-8e4f-628cb316d8e3" />

### 2. Kafka Configuration

```python
BROKER = "kafka:29092"
TOPIC = "gcp_admin_audit_logs"
p = Producer({
    "bootstrap.servers": BROKER,
    "client.id": socket.gethostname(),
    "enable.idempotence": False,
    "acks":"1"
})
```

Essentially what we are trying to do is to pass a dictionary of configurations as argument to the `Producer` API. For a full list and description of the various configurations available for the `Producer` API, please see [here](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html).

>[!NOTE]
>The following is a quick summary of a typical process of publishing events to Kafka topic in the kafka cluster via the `Producer` API:
> 1. Each message being sent to kafka has three elements: Timestamp, Key and Value to form a `ProducerRecord()`
> 2. `Producer` API uses your configured `key.serializer` and `value.serializer` to turn key/value into bytes.
> 3. Producer first computes hash on the key of the message followed by a mod operation to find the partition to produce to into topics first in the `Producer` API first before sending to the same partition in the Kafka topic in batches. This batching mechanism minimises overheads and improves network communication efficiency.
> 4. Kafka topic is partitioned based on Key, and message is added to the respective partition - these partitions help kafka scale by allowing you to add resources and additional partitions as your system handles more and more data.
> 5. Each partition resides in a kafka broker. And each partition has a `Leader` node handling all its read and write requests. `Follower` node hold replicated data of `Leader` nodes enabling fault tolerance in case of data loss. A new leader is elected from the followers if the broker goes down.
> 6. After the messsge is delivered to cluster, producer waits for an ackowledgement from the leader node that it did indeed receive the data. This `acks` setting ensures no data loss and and can be customised in such a way that `Follower` nodes acknowledge as well. But this process results in high latency, as such we can specify `acks=0` for no acknowledgment needed for producer which ensures lowest latency.

<img width="640" height="360" alt="image" src="https://github.com/user-attachments/assets/7c900158-031c-41e1-a6d8-f1aa67cd3055" />


I have used the following producer configuration parameters:
1. `bootstrap.servers` - At a minimum, this parameter should be set as config. It is simply a host/port pair where more often than not is actually a list (e.g. `host1:port1,host2:port2,...`). This list is used to establish the initial connection to the kafka cluster. The Producer API (client application) uses this list to bootstrap and discover the full set of kafka brokers in our cluster (i.e. our kafka cluster can have more than a 100 brokers, hence by specifying a few in our server list our client can initialise a connection to any one of them as a starting point and proceed to discover other brokers in the cluster - clients, producer or consumer APIs, make use of all the servers irrespective of which servers are specified in bootstrap configuration). `BROKER = kafka:29092` - we have spinned up the kafka clusters using docker and hence hostname would be the container name in this case
2. `client.id` - An id string to pass to the server when making requests. The purpose of this is to be able to track the source of requests beyond just ip/port by allowing a logical application name to be included to server-side request logging.
3. `enable.idempotence` - When set to ‘true’, the producer will ensure that exactly one copy of each message is written in the stream. If ‘false’, producer retries due to broker failures, etc., may write duplicates of the retried message in the stream.
4. `acks":"1` - The producer waits for an acknowledgement from leader partition after sending the record. Once the leader partition acknowledges the record, the producer considers it successfully written.

### 3. Define possible event parameters

The following are lookup tables for randomizing realistic values in each log:

1. Service Methods - Google Cloud services that write admin activity logs and the various methods for [ADMIN_WRITE](https://docs.cloud.google.com/compute/docs/logging/audit-logging#permission-type).

```python
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
    ], ...
```

2. Severities - The severity of the event described in the log entry, expressed as one of the standard severity levels listed below.

| Enums | Description |
|-------|-------------|
| `DEFAULT` | 	(0) The log entry has no assigned severity level. |
| `DEBUG` | (100) Debug or trace information. |
| `INFO` | 	(200) Routine information, such as ongoing status or performance. |
| `NOTICE` | (300) Normal but significant events, such as start up, shut down, or a configuration change. |
| `WARNING` | (400) Warning events might cause problems. |
| `ERROR` | (500) Error events are likely to cause problems. |
| `CRITICAL` | (600) Critical events cause more severe problems or outages. |
| `ALERT` | (700) A person must take an action immediately. |
| `EMERGENCY` | (800) One or more systems are unusable. |

For the scope of this project, I've only defined the following:
```python
SEVERITIES = ["INFO", "NOTICE", "WARNING", "ERROR"]
```

Similarly, for `STATUS_CODES`, I've defined it as a list - `[(0, "OK"), (7, "PERMISSION_DENIED"), (5, "NOT_FOUND"), (8, "RESOURCE_EXHAUSTED")]`. But this is by no means the full complete list. For that, you can find it in this [repository](https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto).

`STATUS_WEIGHTS` and `SEVERITY_WEIGHTS` are weights that are mapped to the respective elements in the `STATUS_CODES` and `SEVERITIES` lists respectively. I believe that this step is rather straight-forward explanation. We just want to mimic a production sort of environment where most of the events logged are not critical in nature and are just informative.

### 4. Event Generation

The last component of the python script is the main function called `run()` in which the event is being generated in the most realistic way (I tried my best to mimic a live logger) and sent to the kafka topic. It's packed with a lot of helper functions, hence let's take a look at it one step at a time. 

The overall `run()` function looks like this:
```python
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
```

There are three main parts to the function, let's break it down:
1. **Rate Control Setup**

```python
base_interval = 1.0 / max(rate_per_sec, 1)
last_burst = time.time()
```
- `rate_per_sec` : defines the baseline message rate (e.g. 300 events per second)
- `base_interval` : the average time between two messages
- `last_burst` : timestamp used to track when the last "burst" happened

  > Note: We want to mimic real world load variation, hence we use the variable `burst` to send 20 to 100 messages every 20 to 40 seconds else just one event being sent. In situations like deployments, batch jobs or spike in activity there would be a suddent burst of logs, hence having these steps included would be realistic. Details of how it is being integrated into the function would be described in the next section.

2. **Traffic Pattern Logic (outer while-loop)**

```python
while True:
	# Occasional burst every ~20–40 seconds
	burst = 1
	if bursty and time.time() - last_burst > random.uniform(20, 40):
		burst = random.randint(20, 100)
		last_burst = time.time()

	# Diurnal modulation
	mod = diurnal_weight()
	interval = base_interval / max(0.1, mod)
```

a. Bursty Traffic
	- Every 20 to 40 seconds, the generator sends a short burst of 20-100 events rapidly.
	- Mimics real cloud systems that have sudden bursts of logs (e.g., deployments, batch jobs, spikes in activity).

b. Diurnal Modulation
	- calls `diurnal_weight()` function to scale interval based on the time of day. Essentially we want to create/generate more events per second during peak hours and lesser rate during non-peak hours.
	- Hence, between 7am to 12pm as well as 8pm to 2am was arbitrarily selected as the peak hours of the day.
	- If it’s a busy hour, mod ≈ 1.0 → short intervals → more events/sec.

3. **Message Production Loop (inner for-loop)**

```python
for _ in range(burst):
	event, key = make_admin_activity_event()
	p.produce(
		TOPIC,
		key=key.encode(),
		value=json.dumps(event),
		callback=delivery,
	)
	p.poll(0.5)
	
	sleep_for = interval * (random.uniform(0.5, 1.6) if jitter else 1.0)
	time.sleep(sleep_for)
```

a. Create a new log
	- `make_admin_activity_event()` builds a full JSON record representing one simulated GCP admin activity audit log.
 	- `key` (the user email) ensure the kafka messages with the same user go to the same partition.

b. Send it to Kafka
	- `p.produce(...)` sends the JSON message to the Kafka topic (gcp_admin_audit_logs).
	- `p.poll(0.5)` serves internal callbacks (e.g., delivery reports).

>[!TIP]
>For asynchronous writes, in the produce method we can pass a parameter `callback` if we want to receive notification of delivery success or failure of messge to kafka broker. We pass a function here as it needs to be a callable object, and delivery notification events will only be propogated if `poll()` is invoked. We pass in an argument to `poll()` as a timeout value (i.e. to wait 0.5 milliseconds for a record before returning).

c. Control the timing
	- `sleep_for`: randomizes the pause between sends (via jitter), so the timing isn’t perfectly uniform.
	- If `jitter=True`: small random variation between `0.5×` and `1.6×` the interval.
	- If `jitter=False`: constant interval.

So, this inner loop controls the micro-level timing between individual events.

## ⚙️ Methodology - Docker Compose

Now that we have our `producer.py` file out of the way, we now need to spin up the necessary services via docker to be able to send the generated event/messages to the kafka topic as well as be able to view the data via a user interface. As such, we would need to build three containers; a `Kafka container`, `redpanda container` which is a kafka web UI for visibility of our topic as well as exploring real-time data, and lastly a `python container` that runs our python script and sends messages to kafka.

1. **`broker` - kafka container**

As mentioned we need a `kafka container` which serves as an endpoint for the messages being generated by the `Producer` and into our topic. Given that this is more of a local experimentation, I decided to proceed with the `confluent-local` docker image as it is more lightweight package optimised for local development in which Kafka starts in `KRaft mode` with no configuration setup (`KRaft` is simply a metadata management protocol that replaces the traditional external tool from Apache called `zookeeper` to enable kafka brokers to be more self-sufficient when it comes to managing their internal metadata such as topic configuration, partition assignments, leader elections, etc. as opposed to using a external tool to do so). But if you need to spin up a service suitable for production or perhaps for more advanced experimenation, then you can look at this [confluent-page](https://docs.confluent.io/platform/current/installation/docker/image-reference.html#ak-images) for more suitable kafka images. 

```yaml
broker:
	image: confluentinc/confluent-local:latest
	hostname: broker
	container_name: broker
	ports:
	  - "9092:9092"
	environment:
	  KAFKA_NODE_ID: 1
	  KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT'
	  KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://broker:29092'
	  KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
	  KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
	  KAFKA_PROCESS_ROLES: 'broker,controller'
	  KAFKA_CONTROLLER_QUORUM_VOTERS: '1@broker:29093'
	  KAFKA_LISTENERS: 'PLAINTEXT://broker:29092,CONTROLLER://broker:29093'
	  KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
	  KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
	  KAFKA_LOG_DIRS: '/tmp/kraft-combined-logs'
	
	volumes:
	  - kafka-data:/var/lib/kafka/data
```

The above is extracted from a [confluent-local](https://github.com/confluentinc/kafka-images/blob/master/examples/confluent-local/docker-compose.yml) docker-compose example file. I've just made a few tweaks to make it more suitable for my experiment and to be honest, most of the environment variables do not have to be listed as they hold the default values. Literally all the variables except for `CLUSTER_ID` is listed. I did so, so as to be able to describe what they are meant to do so that you can decide if you want to change the values based on your experiment. The list of environment variables and default values can be found [here]([local/include/etc/confluent/docker/configureDefaults](https://github.com/confluentinc/kafka-images/blob/7.4.x/local/include/etc/confluent/docker/configureDefaults?session_ref=https%3A%2F%2Fgithub.com%2F&url_ref=https%3A%2F%2Fdocs.confluent.io%2Fplatform%2Fcurrent%2Finstallation%2Fdocker%2Fconfig-reference.html).

1. `KAFKA_NODE_ID`
2. `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` : Defines key/value pairs for the security protocol to use, per listener name. In the docker-compose file we had defined `KAFKA_LISTENERS` which is essentially just labels mapped to a port. And the security protocol used in this case is `PLAINTEXT` which simply refers to an unsecured security type.
3. `KAFKA_ADVERTISED_LISTENERS` : A list of listeners with their host/IP and port. This is the metadata that is passed back to clients (producers/consumers). Kafka brokers include their address (hostname + port) in metadata responses. Clients use that to reconnect or to reach the correct partition leader. 
4. `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR` : The minimum number of replicas that must acknowledge a write to transaction topic in order to be considered successful.
5. `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` : The replication factor for the transaction topic (set higher to ensure availability). Internal topic creation will fail until the cluster size meets this replication factor requirement.
> Note: The transaction topic is a internal kafka log called `__transaction_state` that logs all ongoing transactional metadata such as Transaction Status (e.g. `ONGOING`, `PREPARE_COMMIT`, `COMPLETE_COMMIT`, `ABORTED`, etc.).  This is to ensure idempotency by enabling atomic writes to partitions from producers. Hence, the default `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` is 3 (i.e. one leader node and 2 replica nodes) to ensure that this `__transaction_state` log is not lost, but since we are using a single-node cluster, we have to change this value to 1. 
6. 
7. 
