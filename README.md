# ADK Blog Writer Agent

このリポジトリは Google ADK を利用してブログ記事の作成を支援するエージェントのサンプルです。リサーチャー、ブログ編集者、画像生成ツールを組み合わせ、ブログの企画から記事執筆、アイキャッチ画像の生成までを行います。

## 主な機能

- **Researcher Agent**: キーワードに基づくブログ記事のアイデアを提案します。
- **Blog Editor Agent**: 選択したテーマからプロフェッショナルな記事を生成します。
- **Image Generator Tool**: ブログ用のアイキャッチ画像を作成します。
- **Streamlit UI**: チャット形式でエージェントとやり取りできる簡易 UI を提供します。

## 環境構築

1. リポジトリをクローンします。
   ```bash
   git clone https://github.com/danishi/adk-blog-writer-agent.git
   cd adk-blog-writer-agent
   ```
2. Python 仮想環境を作成し依存ライブラリをインストールします。
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. `.env.example` をコピーして `.env` を作成し、Google Cloud のプロジェクトやリージョンなどを設定します。
   ```bash
   cp .env.example .env
   # 必要に応じて値を編集してください
   ```
4. Google Cloud CLI で認証を行います。
   ```bash
   gcloud auth application-default login
   ```

## ローカルでの実行

開発中は ADK をローカルモードで起動できます。
```bash
adk web
```
または、Streamlit UI を利用する場合は以下を実行してください。
```bash
streamlit run ui.py --server.enableCORS=false
```

## デプロイ

Vertex AI Agent Engines へデプロイするには次のスクリプトを使用します。
```bash
python deploy.py --create        # 新規作成
python deploy.py --list          # 一覧表示
python deploy.py --delete --resource_id=<ENGINE_ID>  # 削除
```
環境変数でプロジェクト ID やロケーション、バケット名を指定する必要があります。

## チュートリアル

手順を追って学習したい場合は `tutorial.md` を `teachme` コマンドで表示できます。
```bash
teachme tutorial.md
```

