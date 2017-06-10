#!/usr/bin/env pythonw

import wx
import subprocess
import shlex
import webbrowser
import re

ICON_PATH = 'resources/tray_icon/tray_icon.iconset/icon_512x512.png'


class JupyterNotebook:
    def __init__(self):
        self.pid = None
        self.is_running = False

        self.jupyter_command = "jupyter-notebook"
        self.jupyter_url = "http://localhost:8888"

    def start(self):
        self.proc = subprocess.Popen(shlex.split(self.jupyter_command),
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.pid = self.proc.pid
        self.is_running = True

    def stop(self):
        self.proc.terminate()

        self.pid = None
        self.is_running = False

    def restart(self):
        self.stop()
        self.start()

    def open(self):
        webbrowser.open(self.jupyter_url)


class JupyterNotebookLauncher(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        if not hasattr(self, "status_item"):
            self.status_item = None

        self.init_icon()
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_tasktray_activate)

        self.jupyter_notebook_init()

    def CreatePopupMenu(self):
        menu = wx.Menu()

        self.add_status_item(menu)
        self.jupyter_notebook_change_statusline()
        menu.AppendSeparator()

        self.add_menu_item(menu, "Open in browser", self.jupyter_notebook_open)
        menu.AppendSeparator()

        self.add_menu_item(menu, "Start", self.jupyter_notebook_start)
        self.add_menu_item(menu, "Stop", self.jupyter_notebook_stop)
        self.add_menu_item(menu, "Restart", self.jupyter_notebook_restart)
        menu.AppendSeparator()

        self.add_menu_item(menu, "Quit", self.on_tasktray_close)

        return menu

    def init_icon(self):
        img = wx.Image(ICON_PATH, wx.BITMAP_TYPE_PNG)
        icon = wx.IconFromBitmap(img.ConvertToBitmap())
        self.SetIcon(icon, "Jupyter Notebook Launcher")

    def on_tasktray_activate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def on_tasktray_close(self, evt):
        self.jupyter_notebook.stop()
        wx.CallAfter(self.frame.Close)

    def add_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)

        return item

    def add_status_item(self, menu):
        item = self.add_menu_item(menu, "", None)
        item.Enable(False)

        self.status_item = item

    def change_status_item(self, text):
        if self.status_item:
            self.status_item.SetItemLabel(text)

    def jupyter_notebook_init(self):
        self.jupyter_notebook = JupyterNotebook()
        self.jupyter_notebook.start()
        self.jupyter_notebook_change_statusline()

    def jupyter_notebook_change_statusline(self):
        if self.jupyter_notebook.is_running:
            self.change_status_item(
                "Running (PID: {})".format(self.jupyter_notebook.pid))
        else:
            self.change_status_item("Not running")

    def jupyter_notebook_open(self, evt):
        self.jupyter_notebook.open()

    def jupyter_notebook_start(self, evt):
        self.jupyter_notebook.start()
        self.jupyter_notebook_change_statusline()

    def jupyter_notebook_stop(self, evt):
        self.jupyter_notebook.stop()
        self.jupyter_notebook_change_statusline()

    def jupyter_notebook_restart(self, evt):
        self.jupyter_notebook.restart()
        self.jupyter_notebook_change_statusline()


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(1, 1))
        self.trayicon = JupyterNotebookLauncher(self)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

    def on_close_window(self, evt):
        self.trayicon.Destroy()
        evt.Skip()


if __name__ == "__main__":
    app = wx.App(redirect=False)
    frame = MainFrame(None)
    frame.Show(True)
    app.MainLoop()
