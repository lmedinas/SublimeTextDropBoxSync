import sublime
import sublime_plugin

import webbrowser
import time
import os
import sys

try:
	from dropbox import client, rest, session
except Exception, e:
	raise e

APP_KEY = "l08b15ayq6f160z"
APP_SECRET = "hdaspw56j9itp9l"
ACCESS_TYPE = "app_folder"
TOKEN_FILE = sublime.packages_path() + "/DropBoxSync" + "/token.txt"

class DropboxInit:
	def __init__(self, app_key, app_secret, access_type):
		self.sess = session.DropboxSession(app_key, app_secret, access_type)
		self.current_path = ''
		#when is this necessary
		#sess.unlink()

	def auth(self):
		#verify if the token alredy exists
		if (os.path.exists(TOKEN_FILE)):
			#open file with token and set it
			tokenopen = open(TOKEN_FILE, "r")
			token_key,token_secret = tokenopen.read().split(' ')
			self.sess.set_token(token_key,token_secret)
			tokenopen.close()
		#try to request token
		else:
			try:
				print ("ter")
				self.request_token = self.sess.obtain_request_token()
			except:
				self.request_token = None
				sublime.error_message("Error connecting to DropBox. Try again.")
				return False

			authdialog = sublime.ok_cancel_dialog("""Sublime Text 2 will open a window in your Web Browser to login and authorize with your DropBox Account.""", "OK")
			if (authdialog):
				#get token from browser
				url = self.sess.build_authorize_url(self.request_token)

				if (webbrowser.open_new(url)):
					time.sleep(10)
					#access token
					access_token = self.sess.obtain_access_token(self.request_token)
					#store token
					storetoken = open(TOKEN_FILE, "w")
					#print("tuple %s and %s " % (access_token.key,access_token.secret))
					storetoken.write("%s %s" % (access_token.key,access_token.secret))
					storetoken.close()
				else:
					sublime.error_message("Browser not available.")
			else:
				sublime.status_message("Need autherization to proceed.")
				return
		#app client
		self.client = client.DropboxClient(self.sess)
		#print ("linked account: %s" % self.client.account_info())
		return True

	def mkdir(self, path):
		self.client.file_create_folder(path)

	def ls(self, path=None):
		if path is None:
			resp = self.client.metadata(self.current_path)
		else:
			resp = self.client.metadata(path)
		contents = []
		if 'contents' in resp:
			for f in resp['contents']:
				name = os.path.basename(f['path'])
				contents.append(name)
			return contents

	def uploadfile(self, file):
		fopen = open(file)
		self.current_path = file
		#check settings
		settings = sublime.load_settings("DropBoxSync.sublime-settings")
		if (settings.get("include_dir")):
			directory = os.path.split(os.path.dirname(self.current_path))[1]
			if (os.path.isdir(directory)):
				self.mkdir(directory)
			self.current_path =  directory + "/" + os.path.basename(self.current_path)
			response = self.client.put_file(self.current_path, fopen)
		else:
			self.current_path = os.path.basename(self.current_path)
			response = self.client.put_file(self.current_path, fopen)
		fopen.close()
		print ("uploaded: %s" % response)

class SavedropboxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		db = DropboxInit(APP_KEY,APP_SECRET, ACCESS_TYPE)
		auth = db.auth()
		if (auth == True):
			db.uploadfile(self.view.file_name())

class OpendropboxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#print ("open window %s" % self.window.active_view().file_name())
		db = DropboxInit(APP_KEY,APP_SECRET, ACCESS_TYPE)
		auth = db.auth()
		if (auth == True):
			self.cont = []
			for i in db.ls():
				self.cont.append(i)

			window = self.view.window()
			window.show_quick_panel(self.cont, self.on_done, sublime.MONOSPACE_FONT)

	def on_done(self, idx):
		if idx < 0:
			return
		print "numer %d ",idx


