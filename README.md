## 情報
プロジェクト名：mir1-msa1\
概要:独自中間言語であるmir1を独自ISA言語であるmsa1に変換するプロジェクトです\
使用言語:Python 3.12.10

## 使い方・動かし方
mir1で書いた動かしたいプログラムをmir1Code.csvとして保存し、msa1Compiler2.pyと同じフォルダに入れます\
mir1Code.csvとしてアップロードされているファイルはコラッツ予想を実行するmir1コードです\
インプットポート0から初期値をインプットし、アウトプットポート0から途中結果を出力、アウトプットポート1から何ステップ目か出力します\
msa1Compiler2.pyを動かすと、mir1Code.csvを読み取って16進数のmsa1に変換し、program.csvが出力されます\
mir1の書き方はmir1の書き方.pdfを見てください\
出力されたprogram.csvと同じフォルダにROM_writer.pyを入れて、ROM_writer.pyを実行するとromcode.mcfunctionが出力されます

## 注意事項
ROM_writer.pyはChatGPTが書いたコードになります\
msa1Compiler2.pyは水地が書いたコードになります

このプロジェクトのコードにはバグ等が残っている可能性があります\
コードの使用は**自己責任**でお願いします
