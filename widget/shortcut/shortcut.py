#!python3
import appex, ui, dialogs
import sys, os, re, requests, json
import pickle, time
from threading import Thread, Lock

WIDGET_RECT = (0, 0, 600, 600)

class EnvParam:
	env = None
	lock = None
	file_name = None
	reload_timestamp = 0

	def __init__(self, file_name='env.db'):
		if EnvParam.lock is None:
			EnvParam.lock = Lock()
			EnvParam.lock.acquire()
			EnvParam.file_name = file_name
			f = open(EnvParam.file_name, 'rb')
			try:
				EnvParam.env = pickle.load(f)
			except:
				EnvParam.env = {}
			f.close()
			EnvParam.lock.release()

	def reload(self):
		if time.time() - EnvParam.reload_timestamp > 2:
			EnvParam.reload_timestamp = time.time()
			del EnvParam.lock
			EnvParam.lock = None
			self.__init__()
		return self

	def backup(self):
		for i in range(3):
			f = open(EnvParam.file_name, 'rb')
			try:
				env = pickle.load(f)
				f.close()
			except:
				time.sleep(0.1)
				continue
			if len(env) > 0:
				with open(EnvParam.file_name+'.bk', 'wb') as f:
					pickle.dump(env, f)
					f.close()
				break
		return self

	def save(self):
		assert(self.lock is not None)
		self.lock.acquire()
		f = open(EnvParam.file_name, 'wb')
		pickle.dump(self.env, f)
		f.flush()
		f.close()
		self.lock.release()
		return self

	def get(self, param_name='default', default=None):
		self.lock.acquire()
		res = self.env[param_name] if param_name in self.env else default
		self.lock.release()
		return res

	def put(self, param, param_name='default'):
		self.lock.acquire()
		self.env[param_name] = param
		self.lock.release()
		return self

class DataRt:
	def __init__(self, date, time, code, open, pre_close, new, high, low, volume, amount,
				 b1v, b1n, b2v, b2n, b3v, b3n, b4v, b4n, b5v, b5n,
				 s1v, s1n, s2v, s2n, s3v, s3n, s4v, s4n, s5v, s5n):
			self.date, self.time = int(date), int(time)
			self.open, self.pre_close = float(open), float(pre_close)
			self.high, self.low = float(high), float(low)
			self.code, self.new = int(code), float(new)
			self.volume, self.amount = int(volume), float(amount)
			self.b1n, self.b1v, self.s1n, self.s1v = int(b1n), float(b1v), int(s1n), float(s1v)
			self.b2n, self.b2v, self.s2n, self.s2v = int(b2n), float(b2v), int(s2n), float(s2v)
			self.b3n, self.b3v, self.s3n, self.s3v = int(b3n), float(b3v), int(s3n), float(s3v)
			self.b4n, self.b4v, self.s4n, self.s4v = int(b4n), float(b4v), int(s4n), float(s4v)
			self.b5n, self.b5v, self.s5n, self.s5v = int(b5n), float(b5v), int(s5n), float(s5v)

def get_stock_value(stocks_list):
	res = []
	for i in range(0, len(stocks_list), 256):
		try:
			r = requests.get(
				'http://hq.sinajs.cn/?list={}'.format(','.join(stocks_list[i:min(len(stocks_list), i + 256)])), timeout=5)
			ret = r.content.decode(encoding='gbk')
			for line in ret.strip().split('\n'):
				try:
					context = line.split('"')
					p = context[1].split(',')
					res.append(
						DataRt(
							date=p[30][2:4] + p[30][5:7] + p[30][8:10],
							time=p[31][0:2] + p[31][3:5] + p[31][6:8],
							open=p[1], pre_close=p[2],
							code=context[0][-7:-1], new=p[3], high=p[4], low=p[5], volume=p[8], amount=p[9],
							b1v=p[11], b1n=p[10], b2v=p[13], b2n=p[12], b3v=p[15], b3n=p[14], b4v=p[17], b4n=p[16],
							b5v=p[19], b5n=p[18],
							s1v=p[21], s1n=p[20], s2v=p[23], s2n=p[22], s3v=p[25], s3n=p[24], s4v=p[27], s4n=p[26],
							s5v=p[29], s5n=p[28],
						)
					)
				except IndexError:
					pass
		except:
			pass
	return res

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
		BottonCommon('', 'tel://888888', (BX+110, BY+120, 90, 55), '#ff5a19', 'typb:Telephone', 20),
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
	def edit_location(sender):
		import webbrowser
		webbrowser.open(get_script_path('shortcut.py?action=run&args=edit_weather_location'))
	now = ui.Button(title='', bg_color='#5e96ff', font=('Helvetica Neue', 18), action=edit_location)
	now.tint_color = '#fff'
	now.corner_radius = 10
	ui_view.add_subview(now)
	ui_view.weather['now'] = now

	after = ui.TextView(title='', editable=False, selectable=False, bg_color='#999999', font=('Helvetica Neue', 10))
	after.text_color = '#fff'
	after.alignment = ui.ALIGN_LEFT
	after.corner_radius = 12
	ui_view.add_subview(after)
	ui_view.weather['after'] = after

	def get_weather_now(city):
		try:
			url = 'https://www.tianqiapi.com/api/?version=v6&appid=[appid]&appsecret=[appsecret]&city=%s'
			html = requests.get(url % city, timeout=2).content.decode()
			j = json.loads(html)
			temp = ' {} {}℃ {} {} {}'.format(
				j['wea'], j['tem'], j['humidity'], j['win'] + j['win_speed'], j['air_level']
			)
			temp = temp.replace('晴', '☀️').replace('多云', '🌥').replace('阴', '☁️').replace('小雨', '🌦').\
				replace('中雨', '🌧').replace('大雨', '⛈').replace('雷阵雨', '🌩').replace('雪', '🌨')
			return '{}'.format(temp)
		except:
			return '今天天气好晴朗～处处好风光'

	def get_weather_after(city):
		try:
			url = 'https://www.tianqiapi.com/api/?version=v1&appid=[appid]&appsecret=[appsecret]&city=%s'
			html = requests.get(url % city, timeout=2).content.decode()
			j = json.loads(html)
			res = ''
			for i in range(3):
				c = j['data'][i]
				res += ' {:7s} {:8s} {}'.format(c['day'], '{}~{}'.format(c['tem2'], c['tem1']), c['wea'])
				res += '\n'
			return res
		except:
			return '今天天气好晴朗～处处好风光'

	def layout(ui_view):
		def update_weather_thhread(ui_view, env):
			location = env.get('weather_location', '北京')
			weather_now = location+' '+get_weather_now(location)
			weather_after = get_weather_after(location)
			ui_view.weather['now'].title = weather_now
			ui_view.weather['after'].text = weather_after
			#env.put(weather_now, 'weather_now'). \
			#	put(weather_after, 'weather_after').save()
		env = EnvParam()
		weather_now = None #env.get('weather_now')
		weather_after = None #env.get('weather_after')
		weather_timestamp = env.get('weather_timestamp')
		time_now = time.time()
		ui_view.weather['now'].frame = ui.Rect(10, 10, 380, 40)
		ui_view.weather['after'].frame = ui.Rect(180, 60, 200, 50)
		ui_view.weather['now'].title = weather_now if weather_now is not None else 'Loading'
		ui_view.weather['after'].text = weather_after if weather_after is not None else 'Loading'
		#if weather_timestamp is None or time_now - weather_timestamp > 5:
		#	env.put(time_now, 'weather_timestamp').save()
		#	Thread(target=update_weather_thhread, args=[ui_view, env]).start()
		Thread(target=update_weather_thhread, args=[ui_view, env]).start()
	ui_view.layout_cbs.append(layout)

def create_stock(ui_view):
	stock = ui.TextView(title='', bg_color='#999999', font=('Helvetica Neue', 12))
	stock.text_color = '#fff'
	stock.alignment = ui.ALIGN_LEFT
	stock.corner_radius = 12
	ui_view.add_subview(stock)
	ui_view.stock = stock

	class MyTextViewDelegate (object):
		def textview_should_begin_editing(self, textview):
			import webbrowser
			webbrowser.open(get_script_path('shortcut.py?action=run&args=edit_stock_list'))
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
	stock.delegate = MyTextViewDelegate()

	def get_stock_str(stock_list):
		ret = ''
		try:
			if len(stock_list) == 0: raise
			data = get_stock_value(stock_list)
			if len(data) == 0: raise
			for s in data:
				t = str(s.date * 1000000 + s.time)[-10:-2]
				ret += '  {:06d}  {}  {}\n     {:5.2f}  {:5.2f}  {:5.2f}%\n'.format(
					s.code, '{}-{} {}:{}'.format(t[:2], t[2:4], t[4:6], t[6:8]),
					' 🛩' if s.new - s.pre_close < 0 else ' 🚀',
					s.new, s.new - s.pre_close,
					(s.new - s.pre_close) / s.pre_close * 100)
		except:
			ret = '龙行龘龘\n畸角旮旯'
		finally:
			return ret

	def layout(ui_view):
		def update_stock_thhread(ui_view, env):
			l = env.get('stock_list')
			l = [] if l is None else [x.strip() for x in l.strip().split('\n') if len(x.strip()) > 0]
			stock_str = get_stock_str(l)
			ui_view.stock.text = stock_str
			#env.put(stock_str, 'stock_str').save()
		env = EnvParam()
		stock_str = env.get('stock_str')
		stock_timestamp = env.get('stock_timestamp')
		time_now = time.time()
		ui_view.stock.frame = ui.Rect(10, 60, 160, 210)
		ui_view.stock.text = stock_str if stock_str is not None else 'Loading'
		#if stock_timestamp is None or time_now - stock_timestamp > 5:
		#	env.put(time_now, 'stock_timestamp').save()
		#	Thread(target=update_stock_thhread, args=[ui_view, env]).start()
		Thread(target=update_stock_thhread, args=[ui_view, env]).start()
	ui_view.layout_cbs.append(layout)

def create_remark(ui_view):
	view = ui.TextView(frame=ui.Rect(180, 120, 200, 150), bg_color='#aaaaaa')
	view.font = ('Times New Roman', 16)
	view.alignment = ui.ALIGN_LEFT
	view.scroll_enabled = False
	view.corner_radius = 10
	ui_view.add_subview(view)
	ui_view.remark = view

	class MyTextViewDelegate (object):
		def textview_should_begin_editing(self, textview):
			import webbrowser
			webbrowser.open(get_script_path('shortcut.py?action=run&args=edit_remark'))
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
		text = EnvParam().get('remark')
		ui_view.remark.text = ''.join(text) if text is not None else ''
	ui_view.layout_cbs.append(layout)

class LauncherView_tab1(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, frame=WIDGET_RECT, *args, **kwargs)
		self.bg_color = '#888888'
		self.layout_cbs = []
		self.buttons = []
		self.remark = None
		self.weather = {}
		self.stock = None

		create_buttons(self)
		create_remark(self)
		create_weather(self)
		create_stock(self)

	def layout(self):
		EnvParam().reload()
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

	if True or v is None or v.name != widget_name:
		v = LauncherView_main()
		v.name = widget_name
		appex.set_widget_view(v)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1].strip() == 'edit_remark':
		env = EnvParam().backup()
		text = env.get('remark')
		res = dialogs.text_dialog(text=text if text is not None else '')
		if res is not None:
			env.put(res, 'remark').save()
	elif len(sys.argv) > 1 and sys.argv[1].strip() == 'edit_stock_list':
		env = EnvParam().backup()
		text = env.get('stock_list')
		res = dialogs.text_dialog(text=text if text is not None else '')
		if res is not None:
			env.put(res, 'stock_list').save()
	elif len(sys.argv) > 1 and sys.argv[1].strip() == 'edit_weather_location':
		env = EnvParam().backup()
		text = env.get('weather_location')
		res = dialogs.text_dialog(text=text if text is not None else '')
		if res is not None:
			env.put(res, 'weather_location').save()
	else:
		main()
