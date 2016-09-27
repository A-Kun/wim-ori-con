#!/usr/bin/env python3

__author__ = "Andrew Wang"

import os
import shutil
import struct
import imghdr
import base64
import pexpect
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

GREEN = "#C8E6C9"
YELLOW = "#FFF9C4"
RED = "#FFCDD2"

def load_main_config():
    result = []
    for i in range(8):
        result.append(False)
    try:
        file = open("data/main.config")
        count = 0
        for e in file:
            for ee in e:
                if ee == "1":
                    result[count] = True
                count += 1
        file.close()
        return result
    except FileNotFoundError:
        return result


def save_main_config(var):
    if not os.path.exists("data"):
        os.makedirs("data")
    file = open("data/main.config", "w")
    for e in var:
        file.write(str(IntVar.get(e)))
    file.close()
    messagebox.showinfo("", "主设置已保存。")


def initialize():
    if messagebox.askyesno("", "你确定要初始化数据吗？这将清除所有已输入的数据。"):
        if os.path.exists("data"):
            try:
                shutil.rmtree("data")
                messagebox.showinfo("", "数据初始化成功！")
            except:
                messagebox.showerror("", "数据初始化失败。")
        else:
            messagebox.showinfo("", "数据初始化成功！")


def submit(button):
    button["text"] = "提交中..."
    if messagebox.askyesno("", "你确定要将数据上传至服务器吗？"):
        try:
            var_password = base64.b64decode(b"V0lNV0lNMTIzNDU2").decode("ascii")
            var_command = base64.b64decode(b"c2NwIC1yIGRhdGEgd29ybGRpc21vZUBmaXNzdXJlLnV0c2MudXRvcm9udG8uY2E6fg==").decode("ascii")
            # make sure in the above command that username and hostname are according to your server
            var_child = pexpect.spawn(var_command)
            i = var_child.expect(["password:", "yes/no", pexpect.EOF])

            if i==0: # send password
                var_child.sendline(var_password)
                var_child.expect(pexpect.EOF)
            elif i==1:
                var_child.sendline("yes")
                j = var_child.expect(["password:", pexpect.EOF])
                if j==0:
                    var_child.sendline(var_password)
                    var_child.expect(pexpect.EOF)
            else:
                messagebox.showerror("", "提交失败。")
            messagebox.showinfo("", "提交成功！")
        except Exception as e:
            messagebox.showerror("", "提交失败。")
    button["text"] = "提交"


def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height


def check_dir_existance(question_type):
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/" + question_type):
        os.makedirs("data/" + question_type)


def select_file():
    root.update()
    filename = filedialog.askopenfilename(filetypes=[("JPG Files", "*.jpg")])
    return filename


def check_bg_image_size(filename):
    size = get_image_size(filename)
    return size == (1280, 800)


def select_bg():
    filename = select_file()
    if filename:
        if check_bg_image_size(filename):
            if not os.path.exists("data"):
                os.makedirs("data")
            shutil.copy(filename, "data/bg.jpg")
            messagebox.showinfo("", "设定成功！")
        else:
            messagebox.showerror("", "图片分辨率必须为1280 x 800.")
        check_bg_set()


def check_bg_set():
    if os.path.exists("data/bg.jpg"):
        BGL.config(text="已设定")
        BGL.config(fg="#4CAF50")
    else:
        BGL.config(text="未设定")
        BGL.config(fg="red")


def show_question_list_window(question_type):
    if question_type == "mc":
        no_questions = 40
        title = "选择题"
    elif question_type == "sq":
        no_questions = 20
        title = "简答题"
    elif question_type == "music":
        no_questions = 30
        title = "音乐题"
    mc = Tk()
    mc.title(title)
    ls = Listbox(mc, height=no_questions + 1)
    ls.insert(0, "规则文本")
    for i in range(1, no_questions + 1):
        ls.insert(i, str(i))

    check_question_completion(question_type, ls)

    ls.pack()

    btn = Button(mc, text="Edit", command=lambda: edit_question(question_type, ls))
    btn.pack()

    ls.mainloop()


def edit_question(question_type, ls):
    if not ls.curselection():
        return
    index = ls.curselection()[0]
    if index == 0:
        content = ""
        if os.path.exists("data/" + question_type + "/" + str(index) + ".config"):
            file = open("data/" + question_type + "/" + str(index) + ".config", encoding="utf8")
            content = file.read()
            file.close()

        rule_edit = Tk()
        rule_edit.title("编辑[规则文本]")

        box = Text(rule_edit)
        box.pack()
        box.insert(INSERT, content)

        save_btn = Button(rule_edit, text="Save", command=lambda: save_rule(question_type, box.get("1.0", END), rule_edit, ls))
        save_btn.pack()

        rule_edit.mainloop()
    else:
        content = None
        if os.path.exists("data/" + question_type + "/" + str(index) + ".config"):
            file = open("data/" + question_type + "/" + str(index) + ".config", encoding="utf8")
            content = file.readlines()
            file.close()

        question_edit = Tk()
        question_edit.title("编辑[第" + str(index) + "题]")

        SV = []
        IV = IntVar(question_edit)
        for i in range(7):
            if i < 6:
                SV.append(StringVar(question_edit))
            try:
                if content:
                    if i == 6:
                        IV.set(int(content[i].strip()))
                    else:
                        SV[i].set(content[i].strip())
            except IndexError:
                pass

        if question_type in {"mc", "sq"}:
            L0 = Label(question_edit, text="问题第1行")
            L0.grid(row=0, column=0)
            E0 = Entry(question_edit, textvariable=SV[0])
            E0.grid(row=0, column=1)

            L1 = Label(question_edit, text="问题第2行")
            L1.grid(row=1, column=0)
            E1 = Entry(question_edit, textvariable=SV[1])
            E1.grid(row=1, column=1)
        elif question_type == "music":
            L0 = Label(question_edit, text="番名")
            L0.grid(row=0, column=0)
            E0 = Entry(question_edit, textvariable=SV[0])
            E0.grid(row=0, column=1)

            L1 = Label(question_edit, text="歌名")
            L1.grid(row=1, column=0)
            E1 = Entry(question_edit, textvariable=SV[1])
            E1.grid(row=1, column=1)

        if question_type == "sq":
            L2 = Label(question_edit, text="答案")
            L2.grid(row=2, column=0)
            E2 = Entry(question_edit, textvariable=SV[2])
            E2.grid(row=2, column=1)

        if question_type == "mc":
            L2 = Label(question_edit, text="A选项")
            L2.grid(row=2, column=0)
            E2 = Entry(question_edit, textvariable=SV[2])
            E2.grid(row=2, column=1)

            L3 = Label(question_edit, text="B选项")
            L3.grid(row=3, column=0)
            E3 = Entry(question_edit, textvariable=SV[3])
            E3.grid(row=3, column=1)

            L4 = Label(question_edit, text="C选项")
            L4.grid(row=4, column=0)
            E4 = Entry(question_edit, textvariable=SV[4])
            E4.grid(row=4, column=1)

            L5 = Label(question_edit, text="D选项")
            L5.grid(row=5, column=0)
            E5 = Entry(question_edit, textvariable=SV[5])
            E5.grid(row=5, column=1)

            L5 = Label(question_edit, text="答案")
            L5.grid(row=6, column=0)
            R1 = Radiobutton(question_edit, text="A", variable=IV, value=1)
            R2 = Radiobutton(question_edit, text="B", variable=IV, value=2)
            R3 = Radiobutton(question_edit, text="C", variable=IV, value=3)
            R4 = Radiobutton(question_edit, text="D", variable=IV, value=4)
            R1.grid(row=6, column=1)
            R2.grid(row=7, column=1)
            R3.grid(row=8, column=1)
            R4.grid(row=9, column=1)
        elif question_type == "music":
            L5 = Label(question_edit, text="出现位置")
            L5.grid(row=6, column=0)
            R1 = Radiobutton(question_edit, text="N/A", variable=IV, value=1)
            R2 = Radiobutton(question_edit, text="OP", variable=IV, value=2)
            R3 = Radiobutton(question_edit, text="ED", variable=IV, value=3)
            R4 = Radiobutton(question_edit, text="挿入歌", variable=IV, value=4)
            R1.grid(row=6, column=1)
            R2.grid(row=7, column=1)
            R3.grid(row=8, column=1)
            R4.grid(row=9, column=1)

        save_btn = Button(question_edit, text="保存", command=lambda: save_question(question_type, index, SV, IV, question_edit, ls))
        save_btn.grid(row=10, columnspan=2)

        question_edit.mainloop()


def save_question(question_type, index, SV, IV, window, ls):
    check_dir_existance(question_type)
    file = open("data/" + question_type + "/" + str(index) + ".config","w" , encoding="utf8")
    if question_type == "mc":
        for e in SV:
            file.write(e.get() + "\n")
    elif question_type == "sq":
        for i in range(len(SV)):
            if i > 2:
                file.write("N/A\n")
            else:
                file.write(SV[i].get() + "\n")
    elif question_type == "music":
        for i in range(len(SV)):
            if i > 1:
                file.write("N/A\n")
            else:
                file.write(SV[i].get() + "\n")
    if question_type in {"mc", "music"}:
        file.write(str(IV.get()) + "\n")
    elif question_type == "sq":
        file.write("-1\n")
    file.close()
    window.destroy()
    check_question_completion(question_type, ls)


def save_rule(question_type, content, window, ls):
    check_dir_existance(question_type)
    file = open("data/" + question_type + "/0.config", "w", encoding="utf8")
    file.write(content);
    file.close()
    window.destroy()
    check_question_completion(question_type, ls)


def check_question_completion(question_type, ls):
    if question_type == "mc":
        no_questions = 40
    elif question_type == "sq":
        no_questions = 20
    elif question_type == "music":
        no_questions = 30
    greenlist = []
    for i in range(0, no_questions + 1):
        if i == 0:
            try:
                file = open("data/" + question_type + "/0.config", encoding="utf8")
                if file.read().strip():
                    ls.itemconfig(i, bg=GREEN)
                else:
                    ls.itemconfig(i, bg=RED)
                file.close()
            except:
                ls.itemconfig(i, bg=RED)
        else:
            if os.path.exists("data/" + question_type + "/" + str(i) + ".config"):
                ls.itemconfig(i, bg=GREEN)
                greenlist.append(i)
            else:
                ls.itemconfig(i, bg=RED)
    for e in greenlist:
        file = open("data/" + question_type + "/" + str(e) + ".config", encoding="utf8")
        empty = True
        count = 0
        for l in file:
            if not l.strip():
                if question_type == "music":
                    ls.itemconfig(e, bg=YELLOW)
                else:
                    if count != 1: # 问题第二行可以为空
                        ls.itemconfig(e, bg=YELLOW)
            elif count == 6 and l.strip() == "0":
                ls.itemconfig(e, bg=YELLOW)
            else:
                empty = False
            count += 1
        if empty:
            ls.itemconfig(e, bg=RED)
        file.close()

if (__name__ == "__main__"):
    root = Tk()
    root.title("")

    B = []
    C = []
    var = []
    for i in range(8):
        B.append(None)
        C.append(None)
        var.append(IntVar())

    BGB = Button(root, text="背景图片", command=select_bg)
    BGB.grid(row=0, column=0)
    BGL = Label(root)
    BGL.grid(row=0, column=1)

    check_bg_set()

    B[0] = Button(root, text="选择题", command=lambda: show_question_list_window("mc"))
    B[0].grid(row=1, column=0)
    C[0] = Checkbutton(root, text="启用", variable=var[0])
    C[0].grid(row=1, column=1)

    B[1] = Button(root, text="简答题", command=lambda: show_question_list_window("sq"))
    B[1].grid(row=2, column=0)
    C[1] = Checkbutton(root, text="启用", variable=var[1])
    C[1].grid(row=2, column=1)

    B[2] = Button(root, text="条件题", state=DISABLED)
    B[2].grid(row=3, column=0)
    C[2] = Checkbutton(root, text="启用", variable=var[2])
    C[2].grid(row=3, column=1)

    B[3] = Button(root, text="图片题", state=DISABLED)
    B[3].grid(row=4, column=0)
    C[3] = Checkbutton(root, text="启用", variable=var[3])
    C[3].grid(row=4, column=1)

    B[4] = Button(root, text="其他题", state=DISABLED)
    B[4].grid(row=5, column=0)
    C[4] = Checkbutton(root, text="启用", variable=var[4])
    C[4].grid(row=5, column=1)

    B[5] = Button(root, text="音乐题", command=lambda: show_question_list_window("music"))
    B[5].grid(row=6, column=0)
    C[5] = Checkbutton(root, text="启用", variable=var[5])
    C[5].grid(row=6, column=1)

    B[6] = Button(root, text="冲刺题A", state=DISABLED)
    B[6].grid(row=7, column=0)
    C[6] = Checkbutton(root, text="启用", variable=var[6])
    C[6].grid(row=7, column=1)

    B[7] = Button(root, text="冲刺题B", state=DISABLED)
    B[7].grid(row=8, column=0)
    C[7] = Checkbutton(root, text="启用", variable=var[7])
    C[7].grid(row=8, column=1)

    BSubmit = Button(root, text="提交", command=lambda: submit(BSubmit))
    BSubmit.grid(row=9, column=0)
    BSave = Button(root, text="保存", command=lambda: save_main_config(var))
    BSave.grid(row=9, column=1)

    BRun = Button(root, text="测试运行(Mac only)", command=lambda: os.system("open -a Flash\ Player orient16demo.swf"))
    BRun.grid(row=10, columnspan=2)

    BInit = Button(root, text="数据初始化", command=initialize)
    BInit.grid(row=11, columnspan=2)

    enable = load_main_config()
    for i in range(len(enable)):
        if enable[i]:
            C[i].select()

    root.mainloop()
