# ADK blog writer agent team
これは、Google ADKを使ったブログ生成エージェントのサンプルです。

## Getting Started
```
cp .env.example .env
```

Create your .env file with the following content:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
adk web
```

## Deployment

```bash
python deploy.py --create
```

```bash
python deployment/deploy.py --list
```

```bash
python deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## UI Testing

```bash
streamlit run ui.py --server.enableCORS=false
```
