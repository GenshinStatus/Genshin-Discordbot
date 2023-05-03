# 原神のステータスBOT

## 概要

このBOTは原神のビルド画像の生成などを行うことのできるBOTです  
利用方法などは[公式ページ](https://genshindiscordbot.wixsite.com/discord-genshinbot)や`/genbot help`コマンド参考にしてください  
  

## 開発者向け

### 利用しているAPI

[Enka](https://enka.network)という原神のビルドカードなどが作れるサービスの中で提供されているAPIの機能を利用させてもらっています。

### 構成

このBOTではDockerを利用して環境構築しており以下のような構成で実行されています。  
- [Dockerリポジトリ](https://github.com/nikawamikan/Genshin-Discordbot-Docker)
    - データベース (Postgres)
    - [原神ステータスBOTリポジトリ](https://github.com/CinnamonSea2073/Genshin-Discordbot)
        - lib ディレクトリ
            - [アーティファクターリポジトリ](https://github.com/CinnamonSea2073/artifacter)
