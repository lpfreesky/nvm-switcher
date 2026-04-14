__version__ = "1.0.0"

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import re
import os
import shutil
import threading


class NvmSwitcherApp:
    VERSION = "1.0.0"
    def __init__(self, root):
        self.root = root
        self.root.title(f"NVM Node.js 版本切换器  v{NvmSwitcherApp.VERSION}")
        self.root.geometry("520x450")
        self.root.resizable(False, False)
        self._center_window()

        self.current_version = tk.StringVar(value="检测中...")
        self.installed_versions = []
        self.nvm_path = self.find_nvm()
        self._busy = False

        self._set_icon()
        self._build_ui()

        if not self.nvm_path:
            self.status_var.set("未找到 nvm")
            self.root.after(200, self._show_nvm_not_found)
        else:
            self.refresh_versions()

    def find_nvm(self):
        """按优先级查找 nvm.exe"""
        # 1. PATH
        nvm_cmd = shutil.which("nvm")
        if nvm_cmd:
            return nvm_cmd

        # 2. 环境变量
        for env_var in ("NVM_HOME", "NVM_DIR"):
            val = os.environ.get(env_var)
            if val:
                exe = os.path.join(val, "nvm.exe")
                if os.path.exists(exe):
                    return exe

        # 3. 常见目录扫描
        common_paths = [
            os.path.expanduser(r"~\AppData\Roaming\nvm"),
            os.path.expanduser(r"~\nvm"),
            r"C:\nvm",
            r"D:\nvm",
            r"C:\ProgramData\nvm",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "nvm"),
        ]
        for p in common_paths:
            if p and os.path.exists(os.path.join(p, "nvm.exe")):
                return os.path.join(p, "nvm.exe")
        return None

    def _center_window(self):
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.update_idletasks()
            ww = self.root.winfo_width()
            wh = self.root.winfo_height()
            self.root.geometry(f"+{(sw - ww)//2}+{(sh - wh)//2}")
        except Exception:
            pass

    def _set_icon(self):
        try:
            # exe 打包后 __file__ 会指向临时目录，icon.ico 随包一起
            if getattr(sys, '_MEIPASS', None):
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def _show_nvm_not_found(self):
        messagebox.showwarning(
            "未找到 NVM",
            "未检测到 nvm-windows。\n\n"
            "本工具只支持 nvm-windows：\n"
            "https://github.com/coreybutler/nvm-windows\n\n"
            "如果已安装但不在常见位置，请点击菜单【帮助 -> 手动选择 nvm.exe】指定路径。"
        )

    def _select_nvm_manually(self):
        path = filedialog.askopenfilename(
            title="选择 nvm.exe",
            filetypes=[("nvm executable", "nvm.exe"), ("所有文件", "*.*")]
        )
        if path:
            self.nvm_path = path
            self.refresh_versions()

    def _build_ui(self):
        # 菜单栏
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="手动选择 nvm.exe", command=self._select_nvm_manually)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menubar)

        # 标题
        ttk.Label(self.root, text="NVM Node.js 版本切换器", font=("Microsoft YaHei", 16, "bold")).pack(pady=15)

        # 当前版本
        frame_current = ttk.Frame(self.root)
        frame_current.pack(pady=5)
        ttk.Label(frame_current, text="当前版本:", font=("Microsoft YaHei", 11)).pack(side=tk.LEFT)
        ttk.Label(frame_current, textvariable=self.current_version, font=("Microsoft YaHei", 11, "bold"), foreground="#0078D7").pack(side=tk.LEFT, padx=5)

        # 版本列表
        ttk.Label(self.root, text="已安装版本:", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=30, pady=(15, 0))

        list_frame = ttk.Frame(self.root)
        list_frame.pack(pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.version_listbox = tk.Listbox(
            list_frame,
            height=7,
            width=42,
            font=("Consolas", 11),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle="none"
        )
        self.version_listbox.pack(side=tk.LEFT)
        scrollbar.config(command=self.version_listbox.yview)

        self.version_listbox.bind("<Double-Button-1>", lambda e: self.switch_version())

        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)

        btn_refresh = ttk.Button(btn_frame, text="刷新列表", width=12, command=self.refresh_versions)
        btn_switch = ttk.Button(btn_frame, text="切换版本", width=12, command=self.switch_version)
        btn_install = ttk.Button(btn_frame, text="安装 LTS", width=12, command=self.install_lts)
        btn_refresh.pack(side=tk.LEFT, padx=5)
        btn_switch.pack(side=tk.LEFT, padx=5)
        btn_install.pack(side=tk.LEFT, padx=5)
        self._action_buttons = [btn_refresh, btn_switch, btn_install]

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="gray")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def _run_nvm(self, args):
        """运行 nvm 命令并返回 (success, stdout, stderr)"""
        if not self.nvm_path:
            return False, "", "未找到 nvm，请先安装或手动指定路径。"
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", f'& "{self.nvm_path}" {" ".join(args)}'],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120
            )
            return True, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def _set_buttons(self, enabled):
        """启用/禁用操作按钮，防止加载中重复点击"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self._action_buttons:
            btn.config(state=state)

    def refresh_versions(self):
        if not self.nvm_path:
            self.status_var.set("未找到 nvm")
            return
        if self._busy:
            return
        self._busy = True
        self.status_var.set("正在刷新...")
        self.version_listbox.delete(0, tk.END)
        self._set_buttons(False)

        def do():
            ok, out, err = self._run_nvm(["list"])
            self.root.after(0, self._on_refresh_done, ok, out, err)

        threading.Thread(target=do, daemon=True).start()

    def _on_refresh_done(self, ok, out, err):
        self.installed_versions = []
        self.version_listbox.delete(0, tk.END)

        if not ok:
            self.status_var.set("运行 nvm 失败")
            self._busy = False
            self._set_buttons(True)
            messagebox.showerror("错误", f"无法运行 nvm 命令:\n{err}")
            return

        current_ver = None
        for line in out.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if current_ver is None and ("*" in line_stripped or ">" in line_stripped):
                raw = re.sub(r"^\s*[*>]\s*", "", line_stripped)
                raw = re.sub(r"\s*\(.*", "", raw).strip()
                if re.match(r"^v?\d+", raw):
                    current_ver = raw
            ver = re.sub(r"^\s*[*>]\s*", "", line_stripped)
            ver = re.sub(r"\s*\(.*", "", ver).strip()
            if re.match(r"^v?\d+", ver):
                self.installed_versions.append(ver)
                display = ver
                if ver == current_ver or ("v" + str(current_ver) == ver) or (str(current_ver) == "v" + ver):
                    display = f">> {ver}  (当前)"
                self.version_listbox.insert(tk.END, display)
                if "(当前)" in display:
                    self.version_listbox.selection_set(tk.END)
                    self.version_listbox.see(tk.END)

        if current_ver:
            self.current_version.set(current_ver)

        self.status_var.set(f"共 {len(self.installed_versions)} 个已安装版本")
        self._busy = False
        self._set_buttons(True)

    def switch_version(self):
        selection = self.version_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个版本")
            return

        display_text = self.version_listbox.get(selection[0])
        ver = re.sub(r"^>>\s*", "", display_text)
        ver = ver.replace("  (当前)", "").strip()

        if ver == self.current_version.get() or ("v" + self.current_version.get() == ver) or (self.current_version.get() == "v" + ver):
            messagebox.showinfo("提示", f"当前已经是 {ver}")
            return

        if self._busy:
            return
        self._busy = True
        self.status_var.set(f"正在切换到 {ver} ...")
        self._set_buttons(False)

        def do():
            ok, out, err = self._run_nvm(["use", ver])
            self.root.after(0, self._on_switch_done, ok, out, err, ver)

        threading.Thread(target=do, daemon=True).start()

    def _on_switch_done(self, ok, out, err, ver):
        combined = (out + "\n" + err).lower()
        if ok and ("success" in combined or "now using" in combined or "现在使用" in combined or "is now" in combined):
            messagebox.showinfo("成功", f"已切换到 Node.js {ver}")
            self._busy = False
            self.refresh_versions()
        else:
            msg = out.strip() if out.strip() else err.strip()
            messagebox.showerror("失败", f"切换失败:\n{msg}")
            self.status_var.set("切换失败")
            self._busy = False
            self._set_buttons(True)

    def install_lts(self):
        if not self.nvm_path:
            messagebox.showwarning("提示", "未找到 nvm，请先安装或手动指定路径。")
            return
        if not messagebox.askyesno("确认", "确定要安装最新的 LTS 版本吗？"):
            return
        if self._busy:
            return
        self._busy = True
        self.status_var.set("正在安装 LTS 版本，请稍候...")
        self._set_buttons(False)

        def do():
            ok, out, err = self._run_nvm(["install", "lts"])
            self.root.after(0, self._on_install_done, ok, out, err)

        threading.Thread(target=do, daemon=True).start()

    def _on_install_done(self, ok, out, err):
        messagebox.showinfo("安装结果", out.strip() if out.strip() else err.strip())
        self._busy = False
        self.refresh_versions()


def main():
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = NvmSwitcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
