#!python3
import appex, ui
import os, re, requests, json
import pickle

WIDGET_RECT = (0, 0, 600, 600)
REMARK_NAME = 'remark.txt'

class EnvParam:
	def __init__(self, file_name='env.db'):
		self.env = {}
		self.file_name = file_name
		self.load()

	def load(self):
		try:
			with open(self.file_name, 'rb') as f:
				self.env = pickle.load(f)
		except:
			self.env = {}
		return self

	def save(self):
		with open(self.file_name, 'wb') as f:
			pickle.dump(self.env, f)
		return self

	def get(self, param_name='default'):
		return self.env[param_name] if param_name in self.env else None

	def put(self, param, param_name='default'):
		self.env[param_name] = param
		return self

	def delete(self, param_name='default'):
		if param_name in self.env:
			del (self.env[param_name])
		return self

	def clear(self):
		self.env = {}
		return self

def get_script_path(filename):
	return 'pythonista://'+os.getcwd().split('Documents/')[-1]+'/'+filename

def get_local_ip():
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
		s.close()
	except:
		ip = 'N/A'
	return ip

class BottonCommon:
	def __init__(self, title, url, rect, color=None, icon='iow:chevron_right_24', corner=0, font=None):
		self.title = title
		self.url = url
		self.rect = rect
		self.color = color
		self.icon = icon
		self.corner = corner
		self.font = font

def create_buttons(ui_view):
	def button_action(sender):
		import webbrowser
		webbrowser.open(sender.name)
	BX, BY = (180, 285)
	shortcus = [
		BottonCommon('车', 'yitongxing://', (BX+110, BY+60, 90, 55), '#5e96ff', 'iob:ios7_bolt_32', 20),
		BottonCommon('', 'tel://10010', (BX+110, BY+120, 90, 55), '#ff5a19', 'typb:Telephone', 20),
		BottonCommon('', 'fmip1://', (BX+110, BY+180, 90, 54), '#1e4c38', 'typb:Relocate', 20),
		BottonCommon('扫', 'weixin://scanqrcode', (BX, BY+60, 90, 55), '#0fe24b', 'iow:chatbubbles_32', 20),
		BottonCommon('扫', 'alipayqr://platformapi/startapp?saId=10000007', (BX, BY+120, 90, 55), '#42aeff', 'iob:social_bitcoin_32', 20),
		BottonCommon('码', 'alipay://platformapi/startapp?appId=20000056', (BX, BY+180, 90, 55), '#42aeff', 'iow:social_bitcoin_32', 20),
		BottonCommon('', get_script_path('../ftp_server/run.py?action=run'), (BX, BY+240, 200, 55), '#d6861c', 'iow:folder_32', 20,),
		BottonCommon('录', 'recorder://record', (BX+110, BY, 90, 55), '#ff7842', 'iob:disc_32', 20),
		BottonCommon('BT', 'lightblue://', (BX, BY, 90, 55), '#5e96ff', 'iob:bluetooth_32', 20),
	]

	for s in shortcus:
		btn = ui.Button(title=' ' + s.title, frame=ui.Rect(*s.rect),
		name=s.url, action=button_action, bg_color=s.color, tint_color='#fff', corner_radius=s.corner)
		if s.icon is not None:
			btn.image = ui.Image(s.icon)
		if s.font is not None:
			btn.font = s.font
		ui_view.add_subview(btn)
		ui_view.buttons.append((btn, s.rect))

	def layout(ui_view):
		for b in ui_view.buttons:
			b[0].frame = ui.Rect(*b[1])
		ui_view.buttons[6][0].title = get_local_ip()
	ui_view.layout_cbs.append(layout)

def create_weather(ui_view):
	now = ui.Button(title='', bg_color='#5e96ff', font=('Helvetica Neue', 18))
	now.tint_color = '#fff'
	now.corner_radius = 10
	# now.font =
	ui_view.add_subview(now)
	ui_view.weather['now'] = now

	after = ui.TextView(title='', editable=False, selectable=False, bg_color='#686868', font=('Helvetica Neue', 10))
	after.text_color = '#fff'
	after.alignment = ui.ALIGN_CENTER
	after.corner_radius = 12
	ui_view.add_subview(after)
	ui_view.weather['after'] = after

	def get_weather_now(city):
		try:
			url = 'https://www.tianqiapi.com/api/?version=v6&city=%s'
			html = requests.get(url % city, timeout=2).content.decode()
			j = json.loads(html)
			temp = ' {} {}℃ {} {}'.format(
				j['wea'], j['tem'], j['win'] + j['win_speed'], j['air_level']
			)
			return '{}'.format(temp)
		except:
			return '今天天气好晴朗～处处好风光'

	def get_weather_after(city):
		try:
			url = 'https://www.tianqiapi.com/api/?version=v1&city=%s'
			html = requests.get(url % city, timeout=2).content.decode()
			j = json.loads(html)
			res = ''
			for i in range(3):
				c = j['data'][i]
				res += '{:7s} {:8s} {}'.format(c['day'], '{}~{}'.format(c['tem2'], c['tem1']), c['wea'])
				res += '\n'
			return res
		except:
			return '今天天气好晴朗～处处好风光'

	def layout(ui_view):
		ui_view.weather['now'].frame = ui.Rect(10, 10, 380, 40)
		ui_view.weather['now'].title = get_weather_now('北京')
		ui_view.weather['after'].frame = ui.Rect(180, 60, 200, 50)
		ui_view.weather['after'].text = get_weather_after('北京')
	ui_view.layout_cbs.append(layout)

def create_remark(ui_view):
	view = ui.TextView(frame=ui.Rect(180, 120, 200, 150), bg_color='#cccccc')
	view.font = ('Times New Roman', 16)
	view.alignment = ui.ALIGN_LEFT
	view.scroll_enabled = False
	view.corner_radius = 10
	ui_view.add_subview(view)
	ui_view.remark = view

	class MyTextViewDelegate (object):
		def textview_should_begin_editing(self, textview):
			import webbrowser
			webbrowser.open(get_script_path(REMARK_NAME))
			return False
		def textview_did_begin_editing(self, textview):
			pass
		def textview_did_end_editing(self, textview):
			pass
		def textview_should_change(self, textview, range, replacement):
			return False
		def textview_did_change(self, textview):
			pass
		def textview_did_change_selection(self, textview):
			pass
	view.delegate = MyTextViewDelegate()

	def layout(ui_view):
		if not os.path.exists('remark.txt'):
			open(REMARK_NAME, 'w').close()
		ui_view.remark.text = ''.join(open(REMARK_NAME, 'r', encoding='utf-8').readlines())
	ui_view.layout_cbs.append(layout)

class LauncherView_tab1(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, frame=WIDGET_RECT, *args, **kwargs)
		self.bg_color = '#888888'
		self.layout_cbs = []
		self.buttons = []
		self.remark = None
		self.weather = {}

		create_buttons(self)
		create_remark(self)
		create_weather(self)

	def layout(self):
		for cb in self.layout_cbs:
			cb(self)

class LauncherView_tab2(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, frame=WIDGET_RECT, *args, **kwargs)

class LauncherView_main(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, frame=WIDGET_RECT, *args, **kwargs)
		self.tabs = []

		self.tabs.append(LauncherView_tab1())
		# self.tabs.append(LauncherView_tab2())
		for tab in self.tabs:
			self.add_subview(tab)

		seg = ui.SegmentedControl(frame=ui.Rect(220, 140, 135, 35), bg_color='#eff8ff')
		seg.segments = ['T1', 'T2', 'T3']
		def cb(ui):
			idx = ui.selected_index
			if 0 <= idx < len(ui.superview.tabs):
				for i in range(len(ui.superview.tabs)):
					ui.superview.tabs[i].hidden = False if i == idx else True
		seg.action = cb
		self.add_subview(seg)
		self.seg = seg

	def layout(self):
		# self.seg.bring_to_front()
		self.seg.hidden = True
		self.tabs[0].bring_to_front()

def main():
	widget_name = __file__ + str(os.stat(__file__).st_mtime)
	v = appex.get_widget_view()

	if v is None or v.name != widget_name:
		v = LauncherView_main()
		v.name = widget_name
		appex.set_widget_view(v)

if __name__ == '__main__':
	main()
