# ADK blog writer agent team
Google ADKを使ったブログ生成エージェントのサンプル

## チュートリアル
```bash
$ git clone https://github.com/danishi/adk-blog-writer-agent.git
$ cd adk-blog-writer-agent
$ teachme tutorial.md
```

## Getting Started

```bash
$ gcloud auth application-default login
```

Create your .env file with the following content:

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ adk web
```

## Deployment

```bash
$ python deploy.py --create
```

```bash
$ python deployment/deploy.py --list
```

```bash
$ python deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## UI Testing

```bash
$ streamlit run ui.py
```
