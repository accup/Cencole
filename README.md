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



## Logs

- v1.0.0
	- Windowsでそれなりに動くことを確認
	- `librosa.core.load` を使っているが、44100Hzでない音楽ファイルを再生しようとすると、リサンプリングのために時間がかかる。`librosa.core.stream` と逐次的なリサンプリングでアプリケーションの対話性を向上させたい。