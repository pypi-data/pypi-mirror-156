import tkinter as tk
from tkinter import font
from tkinter import messagebox as box


def search_system(title: str = "main", fonts: tuple = ("consolas", 17), size: int = 16):
    class run(object):
        def __init__(self, loadtxt: list, func, boxx: tuple = (100, 100), windowinfo: tuple = (300, 300, False, False)):
            self.window = tk.Tk()
            self.windowinfo = windowinfo
            fontsize = font.Font(size=size)
            self.entryvar = tk.StringVar()
            self.result = tk.Listbox(self.window, selectmode=tk.SINGLE, height=boxx[0], width=boxx[1], font=fontsize)
            self.result.bind("<Double-Button-1>", lambda event: func(event,
                                                                     (self.result.get(self.result.curselection()),
                                                                      self.result.curselection())))
            self.Search = tk.Entry(self.window, font=fonts)
            self.Searchbind()

            self.setwindow()
            self.Search.pack()
            self.result.pack()
            self.load = self.defaultload
            self.reload = loadtxt
            self.data = self.load()

        def get(self):
            return self.result.get(0, tk.END)

        def mainlooper(self):
            self.window.mainloop()
            return self.function_runner

        def function_runner(self, functions: tuple, *parameter):
            if parameter != ():
                if type(functions) is tuple:
                    for function in functions:
                        for args in parameter:
                            if type(args) is tuple:
                                function(*args)
                            else:
                                function(args)
                else:
                    if type(parameter) is tuple:
                        functions(*parameter[0])
                    else:
                        functions(parameter[0])
            else:
                functions()
            return self.mainlooper

        def defaultload(self):
            for i in self.reload:
                self.result.insert(tk.END, i)
            return self.result.get(0, tk.END)

        def Searchbind(self):
            def checked(event):
                self.Search.select_range(0, tk.END)

            def clear(event):
                self.Search.delete(0, tk.END)

            self.Search.bind("<KeyRelease>", self.search)
            self.Search.bind("<Control-a>", checked)
            self.Search.bind("<Control-BackSpace>", clear)

        def setwindow(self):
            self.window.title(title)
            x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
            y = (self.window.winfo_screenheight() // 2) - (800 // 2)
            if type(self.windowinfo[2]) is bool and type(self.windowinfo[3]) is bool:
                self.window.geometry("{}x{}+{}+{}".format(self.windowinfo[0], self.windowinfo[1], x, y))
                self.window.resizable(self.windowinfo[2], self.windowinfo[3])
            else:
                self.window.geometry("{}x{}+{}+{}".format(self.windowinfo[0],
                                                          self.windowinfo[1],
                                                          self.windowinfo[2],
                                                          self.windowinfo[3]))
                self.window.resizable(self.window[4], self.windowinfo[5])

        def search(self, event):
            self.result.delete(0, tk.END)
            if self.Search.get() != "":
                for name in self.data:
                    if self.Search.get() in name:
                        self.result.insert(tk.END, name)
            else:
                self.load()

    return run
