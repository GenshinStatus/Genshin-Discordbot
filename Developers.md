# Developing GenshinStatusBot

このドキュメントは、このプロジェクトの開発者向けガイドラインです。

* [Development Setup](#setup)
* [Coding Rules](#rules)
* [Commit Message Guidelines](#commits)

## <a name="setup"> Development Setup
1. [Dockerリポジトリ](https://github.com/nikawamikan/Genshin-Discordbot-Docker)をcloneしてください。
```bash
$ git clone https://github.com/nikawamikan/Genshin-Discordbot-Docker.git
```
2. docker-composeと同じ階層に.envファイルを作成し、botのトークンを貼り付けます。
botのトークンは[ここ](https://discord.com/developers/applications)から取得できます。
```env
TOKEN = ''

# database
POSTGRES_USER = ''
POSTGRES_PASSWORD = ''
HOST = ''
PORT = ''
POSTGRES_DB = ''

# google calender
CALENDAR_ID = ''
CALENDAR_JSON_PATH = ''
DATA_PATH = ''
```

3. docker-composeを利用し、コンテナを立ち上げます。

```bash
$ docker-compose up
```
4. 起動が確認できれば完了です。

## <a name="rules"> Coding Rules
### 原則
原則、コーディング規則については、Pythonのコーディング規則である[pep8](https://pep8-ja.readthedocs.io/ja/latest/)を参考にすること。

### 個別規約
* 命名は英単語を基本する。スペルに自信が無い場合は確認するべきである。
* 変数名は全て小文字とする。複数単語からなる場合はアンダーバー(_)を使用する。
* 定数名は全て大文字とする。複数単語からなる場合はアンダーバー(_)を使用する。
* メソッド名は全て小文字とする。複数単語からなる場合はアンダーバー(_)を使用する。
* クラス名は単語の先頭のみ大文字とし、ほかは小文字とする。複数単語からなる場合はそれぞれ単語の先頭を大文字とする。
* 組み込み関数や組み込み変数などと同名にし、オーバーライドしてはならない。
* 100行を超えるような長いメソッドは作らない。もしそのような場合に遭遇した場合、いくつかのメソッドに分ける。
* マジックナンバーは使用しない。代わりに、定数を使用する。ただし、画像処理において座標を指定する場合はその限りではない。
* 各メソッドにはコメントを入れ、説明すること。

## <a name="commits"> Git Commit Guidelines

コミットメッセージは、
* ヘッダー
* ボディ
* フッター

の三つで構成される。
ヘッダーにおいては、
```
<type>: <subject>
```
とする。

### type
| タイプ | 説明 |
| ---- | ---- |
| feat | 新機能の追加 |
| fix | バグの修正 |
| docs | ドキュメントの変更 |
| style | 空白やセミコロンなど、コードの挙動に影響を及ぼさない変更 |
| refactor | コードの動作に影響がないコードの変更 |
| perf | パフォーマンスの改善 |
| test | テストの追加や変更 |
| chore | ビルドプロセスやライブラリ、環境の変更 |

### subject
変更を簡易的に説明する。
以下の法則に従う。
* 現在形/命令形を使用する
* 頭文字を大文字にしない
* 句点を付けない

なお、この項目は**日本語でもよいもの**とします。

### body
コミット変更の同期及び変更前後の動作について説明する。
subjectと同様、現在形/命令形を使用する。

### footer
破壊的変更がある場合はフッターに含める。
`BREAKING CHANGE:` を先頭に始める。