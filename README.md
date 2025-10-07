# AuditFlow
> Real-time Detection of Privileged Access Anomalies in Streaming Audit Logs

### ✨ Tagline

_**“Stream. Detect. Protect.”**_

AuditFlow continuously ingests system and cloud audit logs, identifies unauthorized privileged access, and assigns confidence scores using AI-driven anomaly detection — all in real time.

## 📊 Overview

AuditFlow is an open-source data engineering project that integrates **streaming pipelines, cloud audit logs and AI-based scoring** to detect abnormal priviledged access activities.

The system simulates or consumes live audit events (e.g., AWS CloudTrail, Linux auth logs), transforms them into structured datasets, and applies **rule-based + ML** scoring to flag anomalies such as:
	•	Unauthorized logins or sudo usage
	•	Unexpected admin policy updates
	•	Key or role creations outside normal hours
	•	Access from unfamiliar IPs or regions

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
    - Then git clone DEZoomcamp repo
