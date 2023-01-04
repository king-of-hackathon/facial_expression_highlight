# スーピー（仮）
## 概要
OpenHackU2022ONLINE[^1]での提出作品の改良版です。

[^1]:https://hacku.yahoo.co.jp/2022/

## プレゼンスライド
https://github.com/king-of-hackathon/facial_expression_highlight/blob/main/HACKU2022ONLINE-hackID9.pdf

## デモ
https://user-images.githubusercontent.com/57135683/210380181-70e70256-1f9d-4b40-b3f6-56034fdb6b87.mp4

## インストールと実行
```
$ git clone https://github.com/king-of-hackathon/facial_expression_highlight
$ cd facial_expression_highlight
$ conda create -n highlight-ai python=3.9
$ conda activate highlight-ai
(highlight-ai) $ pip install .
(highlight-ai) $ flask run
* Running on http://127.0.0.1:5000/
```

## 環境の削除
```
$ conda deactivate
$ conda remove -n highlight-ai --all
```

## License

Copyright [RIshimoto] [石元稜]

Apache License Version 2.0（「本ライセンス」）に基づいてライセンスされます。あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。本ライセンスのコピーは下記の場所から入手できます。

http://www.apache.org/licenses/LICENSE-2.0
適用される法律または書面での同意によって命じられない限り、本ライセンスに基づいて頒布されるソフトウェアは、明示黙示を問わず、いかなる保証も条件もなしに「現状のまま」頒布されます。本ライセンスでの権利と制限を規定した文言については、本ライセンスを参照してください。

使用したオープンソースのソースコードは、それぞれのライセンスに従います。
詳細は各ディレクトリ同梱のLICENSEファイルをご確認ください。
