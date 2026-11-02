# Shop floor assistant

## Overview:

### MES-agent

Analyze MES data.

Two kinds of tools now (mes_agent/analytics/tool_core.py):
 routing: From historical MES-data help to route new products based on the part family
 most common: Find what faults have occurred the most, which workstation has caused the most downtime etc.


### Document agent

Can retrieve and answer to users questions related to machines
and troubleshoot issues with the machines

---

## Technologies

Langgraph, Ollama (qwen2.5:14b-instruct)

---

## Data

Document agents data is real Siemens manuals and troubleshooting guides
MES data is synthetic made for this project.


---

## Usage
Note MES-api has not been uploaded yet, so document agent works only.

### Prerequisites
 - Install requirements
 pip install -r requirements.txt (NOTE not added)

 - Build the documents
python pipelines/build_vector_index.py

### Frontend

npm run dev

### Backend

uvicorn api.app:main 

