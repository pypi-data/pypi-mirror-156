import os
import sys
import codecs
import platform

system = platform.system()
desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
absolute = os.path.abspath(__file__)


class openof:
    def __init__(self, file_path: str, openmoth=codecs.open,mode="+ab", encode="utf-8"):
        self.dict = False
        self.type = None
        if ".json" in file_path:
            self.type = "json"
        elif ".txt" in file_path:
            self.type = "txt"
        self.path = file_path
        self.encode = encode
        self.mode = mode
        self.name = os.path.basename(self.path)
        self.op = openmoth
        self.file = self.op(self.path, self.mode, encoding=self.encode)

    def __enter__(self):
        self.file = self.op(self.path, self.mode, encoding=self.encode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def setting(self, dicts: bool = None,
                types: bool = None,
                path: str = None,
                encode: str = None,
                mode: str = None,
                file: codecs.open or open = None,
                name: str = None,
                op = None
                ) -> None:
        if dicts is None:
            dicts = self.dict
        if types is None:
            types = self.type
        if path is None:
            path = self.path
        if encode is None:
            encode = self.encode
        if mode is None:
            mode = self.mode
        if file is None:
            file = self.file
        if name is None:
            name = self.name
        if op is None:
            op = self.op
        self.dict = dicts
        self.type = types
        self.path = path
        self.encode = encode
        self.mode = mode
        self.file = file
        self.name = name
        self.op = op
        return None

    def write(self, content: str or dict or int, mode: str = "w", cover: bool = True, tobyte: bool = False) -> None:
        if cover:
            self.file.close()
            self.file = self.op(self.path, mode)

        if self.type == "json":
            import json
            if type(content) == dict:
                json.dump(content, self.file, indent=4, sort_keys=True)
            else:
                pass
        elif self.type == "txt":
            if type(content) == dict:
                self.dict = True
            if tobyte:
                self.file.write(content.encode(self.encode))
            else:
                self.file.write(content)
        else:
            if tobyte:
                self.file.write(content.encode(self.encode))
            else:
                self.file.write(content)
        return None

    def writeline(self, content: str or list, mode: str = "a"):
        self.file.writelines(content)

    def read(self, mode: str = "rb", txtmod: str = "r") -> dict or str or int or bool:
        if self.type == "json":
            import json
            self.file.close()
            with self.op(self.path, mode, encoding=self.encode) as f:
                data = json.load(f)
                self.file = self.op(self.path, self.mode)
                return data
        elif self.type == "txt":
            self.file.close()
            with self.op(self.path, mode, encoding=self.encode) as f:
                data = f.read()
                f.close()
                self.file = self.op(self.path, txtmod, encoding=self.encode)
            if self.dict:
                from json import loads as todict
                from demjson import encode
                data = todict(encode(data))
                self.file.close()
                return data
            return data
        else:
            return self.file.read()

    def readline(self, size: int = None):
        return self.file.readline(size)

    def readlines(self, sizeint: int = None):
        return self.file.readlines(sizeint)

    def recontent(self, content: str or tuple or list, overlaycontent: str = "\n", mode1: str = "r", mode2: str = "w", strictly: bool = True):
        self.file.close()
        with self.op(self.path, mode1) as file:
            lines = file.readlines()
        with self.op(self.path, mode2) as file:
            for line in lines:
                contenttype = type(content)
                if contenttype is str:
                    if strictly:
                        if line.strip("\n") != content:
                            file.write(line)
                        else:
                            file.write(overlaycontent)
                    else:
                        if content not in line:
                            file.write(line)
                        else:
                            file.write(overlaycontent)
                elif contenttype is tuple or contenttype is list:
                    if strictly:
                        if line not in content:
                            file.write(line)
                        else:
                            file.write(overlaycontent)
                    else:
                        contentlen = len(content)
                        linebool = False
                        for i in range(contentlen):
                            if content[i] in line:
                                linebool = True
                        if linebool:
                            file.write(overlaycontent)
                        else:
                            file.write(line)
                else:
                    raise ValueError("parameter should be tuple, list or string, instead of {}".format(contenttype))
        self.file = self.op(self.path, self.mode, encoding=self.encode)

    def deleteline(self, del_line: int, overlaycontent: str = "\n", mode1: str = "r", mode2: str = "w"):
        self.file.close()
        with self.op(self.path, mode1) as file:
            filelines = file.readlines()
        with self.op(self.path, mode2) as file:
            count = 0
            for fileline in filelines:
                if del_line != count:
                    file.write(fileline)
                else:
                    file.write(overlaycontent)
                count += 1
        self.file = self.op(self.path, self.mode, encoding=self.encode)

    def close(self) -> None:
        self.file.close()
        return None

    def remove(self) -> int:
        self.file.close()
        if os.path.exists(self.path):
            os.remove(self.path)
            return 1
        return 0

    def reopen(self, mode="a"):
        return self.op(self.path, mode)

    def move(self, other_path: str) -> str or None:
        if os.path.isdir(other_path):
            import shutil
            shutil.move(self.path, other_path)
            if system == "Windows":
                self.path = other_path + "\\" + os.path.basename(self.file.name)
                return self.path
            else:
                self.path = other_path + "/" + os.path.basename(self.file.name)
                return self.path
        return None

    def rename(self, name: str, process: bool = True, mode: str = "x") -> str or None:
        if os.path.exists(os.path.join(os.path.dirname(self.path), name)):
            return None
        self.file.close()
        if system == "Windows":
            sep = "\\"
        else:
            sep = "/"
        if process:
            if "." not in name:
                _, file_suffix = os.path.splitext(self.path)
                name += file_suffix
            os.rename(self.path, os.path.dirname(self.path) + sep + name)
            self.path = os.path.dirname(self.path) + sep + name
            self.name = name
        else:
            os.rename(self.path, name)
            self.path = name
            _, file_suffix = os.path.splitext(name)
            self.name = os.path.dirname(name) + sep + file_suffix
        self.file = codecs.open(self.path, self.mode, encoding=self.encode)
        if system == "Windows":
            self.path = os.path.dirname(self.path) + "\\" + name
        else:
            self.path = os.path.dirname(self.path) + "/" + name
        return self.path

    def zipit(self, zippath: str = os.path.join(os.getcwd(), "newzip.zip"), mode: str = "a"):
        from zipfile import ZipFile
        with ZipFile(zippath, mode) as zip:
            zip.write(self.path, os.path.basename(self.path))
        self.zipath = zippath
        return zippath

    if system == "Windows":
        def createlnk(self,
                      lnk_name: str = None,
                      lnk_path: str = desktop,
                      target: str = None,
                      start: str = None,
                      icon: str = None,
                      style: int = 1,
                      suffix: str = ".lnk"):
            import win32com.client
            if target is None:
                target = self.path
            if lnk_name is None:
                lnk_name = os.path.basename(self.path) + suffix
            path = os.path.join(lnk_path, lnk_name)
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            if start is not None:
                shortcut.Workingdirectory = start
            if icon is not None:
                shortcut.IconLocation = icon
            shortcut.WindowStyle = style  # 7 - Minimized, 3 - Maximized, 1 - Normal
            shortcut.save()

        def unzipit(self, zippath: str = os.getcwd(), mode: str = "r"):
            if "zipath" in dir(self):
                from zipfile import ZipFile
                with ZipFile(self.zipath, mode) as zip:
                    zip.extractall(zippath)
            return None

        def rmzip(self):
            if "zipath" in dir(self):
                os.remove(self.zipath)


def mkdir(path: str = os.getcwd(), name: str = None, handle_path: bool = True) -> str or None:
    if name is None:
        import time
        localtime = time.localtime(time.time())
        name = "{}-{}-{} {}-{}-{}".format(
            localtime.tm_year,
            localtime.tm_mon,
            localtime.tm_mday,
            localtime.tm_hour,
            localtime.tm_min,
            localtime.tm_sec)
    if handle_path:
        if system == "Windows":
            path += "\\" + name
        else:
            path += "//" + name
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        return path
    else:
        return None


def move(path_obj: str, path_target: str):
    import shutil
    shutil.move(path_obj, path_target)


def mkfile(path: str = os.getcwd(), name: str = None, suffix: str = ".txt", mode="a",
           handle_path: bool = True) -> str:
    if name is None and handle_path:
        import time
        localtime = time.localtime(time.time())
        name = "{}-{}-{} {}-{}-{}".format(
            localtime.tm_year,
            localtime.tm_mon,
            localtime.tm_mday,
            localtime.tm_hour,
            localtime.tm_min,
            localtime.tm_sec)
    if handle_path:
        if system == "Windows":
            path += "\\" + name + "." + suffix.strip(".")
        else:
            path += "/" + name + "." + suffix.strip(".")
    if not os.path.exists(path):
        open(path, mode)
    return path


def rmdir(path) -> None:
    import shutil
    shutil.rmtree(path)


def dirname(path: str, times: int) -> str:
    for i in range(times):
        path = os.path.dirname(path)
    return path


def zipfile(*paths: str, zippath: str = os.getcwd() + "newzip.zip", mode: str = "a") -> str:
    from zipfile import ZipFile
    pathlen = len(paths)
    for index in range(pathlen):
        if not os.path.exists(paths[index]):
            raise FileNotFoundError
        with ZipFile(zippath, mode) as zip:
            zip.write(paths[index], os.path.basename(paths[index]))
    return zippath


def unzip(zippath: str, topath: str = os.getcwd(), mode: str = "r"):
    from zipfile import ZipFile
    with ZipFile(zippath, mode) as zip:
        zip.extractall(topath)
