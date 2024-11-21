# Main Features

- Multi-Cloud Management: AWS, Azure, GCP, Oracle Cloud and IBM Cloud
- Thread-safe cache system with configurable TTL
- Retry pattern implementation with exponential backoff
- Collect and display CPU, memory and disk metrics in real time
- Robust credential validation system per provider

# Pré-requisitos

- Python 3.8 or higher
- Dependencies listed in requirements.txt

# Installation

Clone the repository:

          git clone https://github.com/mrfelpa/Orchestrator.git

          
        cd Orchestrator

Install dependencies:

      pip install -r requirements.txt

- Make sure you are using a virtual environment to avoid conflicts with other libraries installed on the system.

# Settings

- Create a config.json configuration file in the format below:

          {
            "aws": {
                "access_key": "YOUR_ACCESS_KEY",
                "secret_key": "YOUR_SECRET_KEY",
                "region": "YOUR_REGION"
            },
            "azure": {
                "tenant_id": "YOUR_TENANT_ID",
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "subscription_id": "YOUR_SUBSCRIPTION_ID"
            },
            "gcp": {
                "project_id": "YOUR_PROJECT_ID",
                "key_file": "/path/to/keyfile.json"
            },
            "oracle": {
                "user": "YOUR_USER",
                "private_key": "/path/to/private_key.pem",
                "tenancy": "YOUR_TENANCY",
                "region": "YOUR_REGION"
            },
            "ibm": {
                "api_key": "YOUR_API_KEY"
            }
        }

# Using the CLI

- Basic Monitoring

        python -m orchestrator monitor

- Provider-Specific Monitoring
  
        python -m orchestrator monitor --provider aws

- Real-Time Monitoring

        python -m orchestrator monitor --refresh

- Example Output:

  ## Tabela de Recursos

| **Provider** | **Active Resources** | **CPU %** | **Mem %** | **Disk %** | **Cost (USD)** |
|--------------|----------------------|------------|------------|-------------|-----------------|
| ![AWS](https://)           | 12                   | 20.1       | 35.2       | 60.3        | $250.00         |
| ![Azure](https://)        | 8                    | 25.4       | 40.1       | 50.5        | $180.00         |

---

# Fault Handling

- The system implements retry pattern using the tenacity library:

- Maximum 3 attempts
- Exponential backoff (4-10 seconds)
- Detailed crash logging

# Known Limitations

- Current cost monitoring requires provider-specific implementation
- Some provider-specific operations still need to be implemented
- Feature validation is basic and can be expanded

# Future updates

[  ] - Container and Kubernetes support

[  ] - Integration with external monitoring systems

[  ] - Cross-cloud autoscaling implementation

[  ] - Interactive web dashboard

[  ] - Support more cloud providers


- We value contributions, questions, bugs or suggestions, open an issue in the repository
