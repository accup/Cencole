import argparse

parser = argparse.ArgumentParser(prog='Cencole')
parser.add_argument(
	'base_dir', type=str,
	help='再生したいオーディオファイルが含まれるディレクトリへのパス')
parser.add_argument(
	'-s', '--sample_rate', dest='sample_rate', type=int, default=44100,
	help='サンプリング周波数')
args = parser.parse_args()

# メイン処理開始
import time
import sounddevice as sd
from .sound_selector import SoundSelector
from .text_util import ljust_lclip, rjust, quadrant_three_blocks, IndexFlapper
from . import io_util

try:
	# 端末入力モード初期化
	io_util.init()
	
	# サウンドセレクタの作成
	model = SoundSelector(base_dir=args.base_dir, sample_rate=args.sample_rate)
	
	if model.is_empty():
		print('オーディオファイルが見つかりませんでした。')
		exit(0)
		
	flapper = IndexFlapper(5, 4)
	
	with sd.OutputStream(samplerate=44100, callback=model.callback_output_data):
		while True:
			selected_title = model.selected_title()
			loaded_title = model.loaded_title() if model.is_anything_loaded() else ''
			pause_state = "Play " if model.is_paused() else "Pause"
			print(
				'\r'
				f'\u2195{ljust_lclip(selected_title, 24)}'
				f'|{quadrant_three_blocks(flapper.index())} {ljust_lclip(loaded_title, 24)}'
				f'|Vol.\u2190{rjust(str(model.volume()), 3)}\u2192'
				f'| [\u21b5]Load [ ]{pause_state} [ESC]Quit ',
				end='')
			
			if not io_util.hit_any_key():
				# キー入力以外の処理
				if model.is_anything_loaded() and model.is_loaded_finished():
					# 再生終了時の自動遷移
					model.move_next_title()
					model.load()
				# 毎時更新
				if not model.is_paused():
					flapper.update()
				# 30 FPS
				time.sleep(1 / 30)
				continue
			else:
				# キー入力処理
				k = io_util.key_input()

				if k.up():
					model.move_previous_title()
				elif k.down():
					model.move_next_title()
				elif k.left():
					model.volume(model.volume() - 1)
				elif k.right():
					model.volume(model.volume() + 1)
				elif k.ascii(b' '): # Space
					if model.is_paused():
						model.resume()
					else:
						model.pause()
				elif k.enter():
					model.load()
				elif k.escape():
					# Exit
					break
except Exception as e:
	import sys
	print(e, file=sys.stderr)
finally:
	io_util.restore()
	exit(0)

