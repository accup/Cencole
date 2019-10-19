# Cencole
音楽再生CUIアプリケーション

## 依存関係
- インタプリタ
	- Python 3.6以降
- Pythonライブラリ
	- [sounddevice](https://github.com/spatialaudio/python-sounddevice/)
	- [librosa](https://github.com/librosa/librosa)
- コマンドラインツール（mp3, m4aを再生したい場合）
	- [FFmpeg](http://ffmpeg.org/)

## 使い方
```
python -m Cencole "/path/to/オーディオファイルの入っているフォルダ"
```

- 指定したフォルダから再帰的にオーディオファイルを探します。
- 拡張子が .wav, .mp3, .m4a, .ogg のものをオーディオファイルとして認識します。

## 操作
- <kbd>Up</kbd>, <kbd>Down</kbd>：楽曲選択
- <kbd>Left</kbd>, <kbd>Right</kbd>：音量調整
- <kbd>Enter</kbd>：オーディオファイルの読み込み、そののち再生
- <kbd>Space</kbd>：再生（リジューム）・一時停止（ポーズ）
- <kbd>R</kbd>：全曲リピート・1曲リピート切り替え
- <kbd>Q</kbd>：Cencoleの終了

## Logs

- v1.0.1 (<time datetime="2019-10-19">2019/10/19</time>)
	- 1曲リピート機能を追加
	- 端末サイズに合わせてレイアウトを調整
	- 終了（Quit）キーを<kbd>Esc</kbd>キーから<kbd>Q</kbd>キーに変更
	- デコード失敗時に一言表示するように修正
- v1.0.0 (<time datetime="2019-10-19">2019/10/19</time>)
	- Windowsでそれなりに動くことを確認
	- `librosa.core.load` を使っているが、44100Hzでない音楽ファイルを再生しようとすると、リサンプリングのために時間がかかる。`librosa.core.stream` と逐次的なリサンプリングでアプリケーションの対話性を向上させたい。