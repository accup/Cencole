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
from shutil import get_terminal_size
from .sound_selector import SoundSelector
from .text_util import lclip, ljust_lclip, rjust, quadrant_three_blocks, IndexFlapper
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
	single_repeat = False
	old_terminal_width = 0
	
	with sd.OutputStream(samplerate=44100, callback=model.callback_output_data):
		while True:
			terminal_width, _ = get_terminal_size()
			if terminal_width != old_terminal_width:
				print('\r' + (' ' * (terminal_width - 1)), end='')
			old_terminal_width = terminal_width
			title_width = (terminal_width - 62) // 2
			selected_title = model.selected_title()
			selected_ext = model.selected_extension()
			if model.is_anything_loaded():
				loaded_title = model.loaded_title()
				loaded_ext = model.loaded_extension()
			else:
				loaded_title = ''
				loaded_ext = ''
			pause_state = "Play " if model.is_paused() else "Pause"
			repeat_state = "1" if single_repeat else "A"
			if 20 <= title_width:
				clipped_selected_title = lclip(selected_title, title_width) + selected_ext
				clipped_loaded_title = lclip(loaded_title, title_width) + loaded_ext
				print(
					f'\r\u2195{ljust_lclip(clipped_selected_title, title_width + 4)}'
					f'|{repeat_state}{quadrant_three_blocks(flapper.index())}'
					f'{ljust_lclip(clipped_loaded_title, title_width + 4)}'
					f'|Vol\u2190{rjust(str(model.volume()), 3)}\u2192'
					f'|[\u21b5]Load [ ]{pause_state} [R]Rep [Q]Quit ',
					end='')
			else:
				title_width = (terminal_width - 29) // 2
				clipped_selected_title = lclip(selected_title, title_width) + selected_ext
				clipped_loaded_title = lclip(loaded_title, title_width) + loaded_ext
				print(
					f'\r\u2195{ljust_lclip(clipped_selected_title, title_width + 4)}'
					f'|{repeat_state}{quadrant_three_blocks(flapper.index())}'
					f'{ljust_lclip(clipped_loaded_title, title_width + 4)}'
					f'|Vol\u2190{rjust(str(model.volume()), 3)}\u2192 ',
					end='')				
			
			if not io_util.hit_any_key():
				# キー入力以外の処理
				if model.is_anything_loaded() and model.is_loaded_finished():
					# 再生終了時の自動遷移
					if single_repeat:
						model.restart()
					else:
						model.load_next()
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
				elif k.ascii(b'r'):
					single_repeat = not single_repeat
				elif k.ascii(b'q'):
					# Exit
					break
except Exception as e:
	import sys
	print()
	print(e, file=sys.stderr)
finally:
	io_util.restore()

