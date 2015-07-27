#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# By R.Suzi
# $Id: widgets.py,v 4.0 2001/11/04 12:43:09 rnd Exp $

from Tkinter import *
from ttk import *
from decoder import *
import os

class Application(Tk):
    def __init__(self, master=None):                    
        Tk.__init__(self, master)                    
        self.createWidgets()
        self.decoder = Decoder(os.path.dirname(os.path.abspath(__file__))+"/")
        self.params = []
                                                         
    def createWidgets(self):
        self.title("генератор API")
        colWidth = 60

        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="Generate", menu=file_menu)
        file_menu.add_command(label="all parameters", command=self.onGenerate)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.destroy)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste", state=DISABLED)

        frame = Frame(self)
        frame.grid()

        subFrame = Frame(frame)
        subFrame.grid(row=0,column=1)
        btn = Button(subFrame, text="Сгенерировать",command= self.onGenerateService)
        btn.grid(row=0, column=1)

        lbl = Label(subFrame, text="Параметры процедуры").grid(row =0, column =0)

        subFrameFunc = Frame(frame)
        subFrameFunc.grid(row=2,column=1)

        lbl = Label(subFrameFunc, text="название процедуры").grid(row =0, column =0)
        lbl = Label(subFrameFunc, text="параметры процедуры").grid(row =0, column =1)
        
        self.inputFuncName = Text(subFrameFunc, width=colWidth/2, height=2)
        self.inputFuncName.grid(row=1, column=0)
        self.inputFuncName.insert(AtInsert(), "")

        self.inputFuncParam = Text(subFrameFunc, width=colWidth/2, height=2)
        self.inputFuncParam.grid(row=1, column=1)
        self.inputFuncParam.insert(AtInsert(), "")

        subFrame = Frame(frame)
        subFrame.grid(row=0,column=0)
        btn = Button(subFrame, text="Сгенерировать",command= self.onGenerate)
        btn.grid(row=0, column=1)

        inputParamLabel = Label(subFrame, text="входящие параметры")
        inputParamLabel.grid(row =0, column =0)
        #========= ListBox ===========
	
        lb = Listbox(frame,height=18,width=colWidth,selectmode=EXTENDED)
        lb.grid(row = 4, column = 2)
        #========= text area =========
        self.inputTxt = Text(frame, width=colWidth, height=10)
        self.inputTxt.grid(row=2, column=0)
        self.inputTxt.insert(AtInsert(), "")

        outConstLabel = Label(frame, text="сгенерированные константы")
        outConstLabel.grid(row =3, column =0)

        outModelLabel = Label(frame, text="сгенерированные поля модели")
        outModelLabel.grid(row =3, column =1)
        # вывод для параметров
        self.outConstTxt = Text(frame, width=colWidth, height=18)
        self.outConstTxt.grid(row=4, column=0)
        self.outConstTxt.insert(AtInsert(), "")

        self.outModelTxt = Text(frame, width=colWidth, height=18)
        self.outModelTxt.grid(row=5, column=0)
        self.outModelTxt.insert(AtInsert(), "")

        #вывод для функции
        self.outInterfaceTxt = Text(frame, width=colWidth, height=18)
        self.outInterfaceTxt.grid(row=4, column=1)
        self.outInterfaceTxt.insert(AtInsert(), "")

        self.outServiceTxt = Text(frame, width=colWidth, height=18)
        self.outServiceTxt.grid(row=5, column=1)
        self.outServiceTxt.insert(AtInsert(), "")


    def onGenerate(self):
        self.outConstTxt.delete('1.0',END)
        params = self.inputTxt.get("1.0",END).replace('"','')
        out = self.decoder.generateConst(params)
        self.outConstTxt.insert(AtInsert(), out)

        self.outModelTxt.delete('1.0',END)
        out = self.decoder.generateModel(params)
        self.outModelTxt.insert(AtInsert(), out)

    def onGenerateService(self):
        self.outInterfaceTxt.delete('1.0',END)
        self.outServiceTxt.delete('1.0',END)
        funcName = self.inputFuncName.get("1.0",END).replace('"','').strip()
        outParams = self.inputTxt.get("1.0",END).replace('"','')
        inParams = self.inputFuncParam.get("1.0",END).replace('"','').strip()
        out = self.decoder.generateConstFunc(funcName)
        self.outInterfaceTxt.insert(AtInsert(), out)
        self.outInterfaceTxt.insert(AtInsert(), "\n\n")

        out = self.decoder.generateConst(inParams)
        self.outInterfaceTxt.insert(AtInsert(), out)

        self.outInterfaceTxt.insert(AtInsert(), "\n\n")

        out = self.decoder.generateInterface(funcName, inParams)
        self.outInterfaceTxt.insert(AtInsert(), out)

        out = self.decoder.generateService(funcName, inParams)
        self.outServiceTxt.insert(AtInsert(), out)
        self.params = self.decoder.getFlatParams(inParams)
        self.params += self.decoder.getFlatParams(outParams)
        lst = []
        for i in self.params:
            lst.append(i[0])
        self.cb = Combobox(frame,values = lst, width=colWidth, height=3, style='Kim.TButton', foreground='#FF0000',state='readonly')
        self.cb.grid(row = 2, column = 2)
        self.cb.bind('<<ComboboxSelected>>', self.getSelected)        

    def getSelected(self):
        sel = self.cb.get()
        print sel
                                                        
app = Application()                                 
app.mainloop()   

