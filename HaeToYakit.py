import yaml
import json
import argparse
from io import TextIOWrapper
import os

from tkinter import ttk
from tkinter import Menu
from tkinter import filedialog
from tkinter import Text
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk

print(f"""
作者:柚木梨酱
介绍:一个能够将hae插件规则转换为yakit规则配置的脚本
github:https://github.com/youmulijiang
知识大陆:地图大师的挖洞军火库
""")

parse = argparse.ArgumentParser()
parse.add_argument("-f","--file",metavar="hae_rules.yaml",help="指定hae的配置文件",type=argparse.FileType(encoding="utf-8"))
parse.add_argument("-o","--output",metavar="savePath",help="保存指定目录",type=str,default=None)
parse.add_argument("--gui",help="开启gui界面",default=None,action="store_true")
args = parse.parse_args();

def yamltojson(fileio:TextIOWrapper,savePath:str): 
    # 该函数通过解析yaml格式的数据,返回json结果
    allDictList = []
    result = yaml.load(fileio.read(),Loader=yaml.FullLoader)
    index:int = 0
    groupList:list = result['rules']
    for i in groupList:
        ruleDict:dict = i 
        ruleList:dict = ruleDict.get('rule')
        ruleGroup:str = ruleDict.get('group')
        for rule in ruleList:
            rule:dict = rule
            index += 1
            name = rule['name']
        
            if "f_regex" in rule and rule["f_regex"] != "":
                regex = rule['f_regex']
            elif "s_regex" in rule and rule["s_regex"] != "":
                regex = rule['s_regex']
            elif "regex" in rule and rule["regex"] != "":
                regex = rule['regex']
            else:
                regex = ""

            # print(f"{name}的规则是{regex}")
            
            loaded = rule['loaded']
            scope = rule['scope']
            color = rule['color']
            yakitDict = bpRuleToYakitRule(ruleGroup,name,regex,loaded,scope,color,index)
            # print(yakitDict)
            if yakitDict != {}:
                allDictList.append(yakitDict)
    yakitJson = json.dumps(allDictList,indent=5,sort_keys=True)

    if(savePath != None):
        with open(savePath,"w+") as saveFile:
            saveFile.write(yakitJson)
    
    return yakitJson
        

def bpRuleToYakitRule(ruleGroup:str,name:str,rule:str,loaded:bool,scope:str,color:str,index:int) -> dict:
    """
    对hae的配置文件进行解析,转换为yakit的规则
    {
        "Rule": "(?i)((access|admin|api|debug|auth|authorization|gpg|ops|ray|deploy|s3|certificate|aws|app|application|docker|es|elastic|elasticsearch|secret)[-_]{0,5}(key|token|secret|secretkey|pass|password|sid|debug))|(secret|password)([\"']?\\s*:\\s*|\\s*=\\s*)",
        "NoReplace": true,
        "Color": "red",
        "EnableForRequest": true,
        "EnableForResponse": true,
        "EnableForHeader": true,
        "EnableForBody": true,
        "Index": 3,
        "ExtraTag": [
            "敏感信息"
        ]
    }
    """
    yakitDict = {}
    if loaded == False:
        return yakitDict
    yakitDict['ExtraTag'] = [ruleGroup+"/"+name]
    yakitDict['VerboseName'] = name
    yakitDict['Rule'] = rule
    yakitDict['NoReplace'] = True
    yakitDict['Color'] = color
    yakitDict['Index'] = index
    if(scope.endswith("body")):
        yakitDict["EnableForBody"] = True

    elif(scope.endswith("header")):
        yakitDict['EnableForHeader'] = True
    else:
        yakitDict["EnableForBody"] = True
        yakitDict['EnableForHeader'] = True

    if(scope.startswith("request")):
        yakitDict['EnableForRequest'] = True
    elif(scope.startswith("response")):
        yakitDict['EnableForResponse'] = True
    else:
        yakitDict['EnableForResponse'] = True
        yakitDict['EnableForRequest'] = True
    
    return yakitDict

class Root(ttk.Frame):
    #添加gui操作
    def __init__(self,master=None):
        super().__init__()
        # 创建í一个 ttk 样式的实例
        style = ttk.Style()

        # 使用样式配置主题
        style.theme_use("xpnative")
        self.createMenu()
        self.master.title("HaeToYakit")
        # self.haeYamlFileName = None
        self.createYamlTextArea().grid(row=0,column=1,padx=15,pady=15)
        self.createFuncArea().grid(row=0,column=2,padx=15,pady=15)
        self.createJsonTextArea().grid(row=0,column=3,padx=15,pady=15)

    def createMenu(self):
        topMenu = Menu(self.master)
        fileMenu = Menu(topMenu)
        topMenu.add_cascade(label="菜单",menu=fileMenu)
        self.master.config(menu=topMenu)
        fileMenu.add_command(label="作者",command=lambda:self._getAuthor())
        fileMenu.add_command(label="介绍",command=lambda:self._getIntroduce())

    def createYamlTextArea(self):
        self.yamlTextArea = Text(width=30,height=40)
        return self.yamlTextArea
    
    def createJsonTextArea(self):
        self.jsonTextArea = Text(width=30,height=40)
        return self.jsonTextArea
    
    def createFuncArea(self):
        funcAreaFrame = ttk.Frame(self.master)
        self.addHaeRuleButton = ttk.Button(master=funcAreaFrame,text="打开hae规则文件",command=lambda:self._getHaeRuleFile())
        self.parseHaeRuleToYakitButton = ttk.Button(master=funcAreaFrame,text="转换为yakit配置格式",command=lambda:self._parseYamlToJson())
        self.saveYakitJsonButton = ttk.Button(master=funcAreaFrame,text="保存配置文件",command=lambda:self._saveYakitJson())

        self.addHaeRuleButton.grid(row=0,column=0)
        self.parseHaeRuleToYakitButton.grid(row=1,column=0)
        self.saveYakitJsonButton.grid(row=2,column=0)
        return funcAreaFrame
        

    
    def _getHaeRuleFile(self):
        try:
            self.yamlTextArea.delete("1.0",tk.END)
            self.haeYamlFileName = filedialog.askopenfilename(filetypes=[("hae规则文件",".yml"),("hae规则文件",".yaml")],title="请选择hae配置文件")
            with open(self.haeYamlFileName,encoding="utf-8") as yamlFile:
                for i in yamlFile:
                    self.yamlTextArea.insert("insert",i)
        except:
            pass

    def _parseYamlToJson(self):
        self.jsonTextArea.delete("1.0",tk.END)
        yakitJson = yamltojson(open(self.haeYamlFileName,encoding="utf-8"),None)
        for i in yakitJson:
            self.jsonTextArea.insert("insert",i)

    def _getAuthor(self):
        text = """ 
        作者:柚木梨酱
        github:https://github.com/youmulijiang
        知识大陆:地图大师的挖洞军火库
         """
        messagebox.showinfo(title="作者",message=text)

    def _getIntroduce(self):
        text = "一个能够将hae插件规则转换为yakit规则配置的脚本"
        messagebox.showinfo(title="介绍",message=text)

    def _saveYakitJson(self):
        try:
            yamlFileName = filedialog.askopenfilename(title="选择保存的文件")
            ok = messagebox.askyesnocancel(message=f"是否保存到{yamlFileName}")
            if(ok):
                with open(yamlFileName,mode="w+",encoding="utf-8") as yamlFile:
                    yamlFile.write(self.yamlTextArea.get("1.0","end-1c"))
        except:
            pass

        
if __name__ == "__main__":
    try:
        if(args.file == None and args.output == None and args.gui == None):
            root = Root()
            root.mainloop()
        if(args.gui):
            root = Root()
            root.mainloop()
        if (args.file != None or args.output != None):
            print(yamltojson(args.file,args.output))
    except:
        pass
    