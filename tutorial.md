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

2. `.env` を開き、ご自身のプロジェクト ID やストレージバケット名などを入力します。

3. Python 仮想環境を作成して依存パッケージをインストールします。

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. 開発用サーバーを起動します。

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
python deployment/deploy.py --list
```

不要になったエージェントを削除する場合は `--delete` オプションとリソース ID を指定します。

```bash
python deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## UI Testing

ブラウザ上で動作を確認したい場合は、Streamlit を使った簡易 UI も用意しています。

```bash
streamlit run ui.py --server.enableCORS=false
```
