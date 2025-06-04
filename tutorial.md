# ADK blog writer agent team
これは、Google ADK を使ったブログ生成エージェントのサンプルです。

このチュートリアルは **Google Cloud Shell** 上での利用を想定しています。
Cloud Shell では `teachme` コマンドを使うことで、以下の手順を順に実行できます。
まずはリポジトリを取得してチュートリアルを開きましょう。

```bash
git clone https://github.com/danishi/adk-blog-writer-agent.git
cd adk-blog-writer-agent
teachme tutorial.md
```

## Getting Started

1. 設定ファイルのひな形をコピーします。

   ```bash
   cp .env.example .env
   ```

2. `.env` を開き、ご自身のプロジェクト ID やGCSバケット名などを入力します。

   ```env
   # Environment
   ENV=local # StremalitのUIを使う場合に設定、ローカルのADKを呼び出すかリモートのAgent Engineを呼び出すか（local以外に設定）
   
   # ADK
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=<your_project_id>
   GOOGLE_CLOUD_LOCATION=<your_project_location>
   GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>
   IMAGE_FILE_NAME=image.png
   
   # Streamlit
   REMOTE_AGENT_ENGINE_ID=9999999999999999999 # Agent Engineデプロイ後に差し替える
   ```

4. Python 仮想環境を作成して依存パッケージをインストールします。

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. 開発用サーバーを起動します。

   ```bash
   adk web
   ```

## Deployment

ローカルで動作確認ができたら、エージェントをクラウドにデプロイすることもできます。

```bash
python deploy.py --create
```

作成済みのエージェントを確認する場合は次のコマンドを実行します。

```bash
python deploy.py --list
```

不要になったエージェントを削除する場合は `--delete` オプションとリソース ID を指定します。

```bash
python deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## UI Testing

ブラウザ上で動作を確認したい場合は、Streamlit を使った簡易 UI も用意しています。

```bash
streamlit run ui.py --server.enableCORS=false
```
