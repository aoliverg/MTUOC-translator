#    MTUOC-Translator
#    Copyright (C) 2022  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#GENERIC IMPORTS
import sys
import re
import codecs
import os

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom

#IMPORTS FOR GRAPHICAL INTERFACE
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext


import srx_segmenter


#IMPORTS FOR YAML
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
#IMPORTS FOR MTUOC CLIENT
from websocket import create_connection
import socket

#IMPORTS FOR MOSES CLIENT
import xmlrpc.client

#IMPORTS FOR OPENNMT / MODERNMT CLIENT
import requests

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def connect():
    server_type=connecto_ListBox_TypeList.get(ACTIVE)
    '''OLD MTUOC PROTOCOL
    if server_type=="MTUOC":
        try:
            service="ws://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/translate"
            global ws
            ws = create_connection(service)
        except:
            errormessage="Error connecting to MTUOC: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage)
    '''        
    if server_type=="MTUOC":
        try:
            global urlMTUOC
            urlMTUOC = "http://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/translate"
        except:
            errormessage="Error connecting to MTUOC: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage) 
            
            
    elif server_type=="Moses":
        try:
            global proxyMoses
            proxyMoses = xmlrpc.client.ServerProxy("http://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/RPC2")
        except:
            errormessage="Error connecting to Moses: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage)      
            
    elif server_type=="OpenNMT":
        try:
            global urlOpenNMT
            urlOpenNMT = "http://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/translator/translate"
        except:
            errormessage="Error connecting to OpenNMT: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage)   
    elif server_type=="NMTWizard":
        try:
            global urlNMTWizard
            urlNMTWizard = "http://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/translate"
        except:
            errormessage="Error connecting to NMTWizard: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage)           
    elif server_type=="ModernMT":
        try:
            global urlModernMT
            urlModernMT = "http://"+connecto_E_Server.get().strip()+":"+str(connecto_E_Port.get())+"/translate"
        except:
            errormessage="Error connecting to ModernMT: \n"+ str(sys.exc_info()[1])
            messagebox.showinfo("Error", errormessage)
            
    connecto_B_Connect.configure(state=DISABLED)
    connecto_B_Disconnect.configure(state=NORMAL)
    
def disconnect():
    server_type=connecto_ListBox_TypeList.get(ACTIVE)
    '''
    if server_type=="MTUOC":
        try:
            ws.close()
        except:
            pass
    '''
    connecto_B_Connect.configure(state=NORMAL)
    connecto_B_Disconnect.configure(state=DISABLED)
    
   
def clear_test():
    test_text_source.delete(1.0,END)
    test_text_target.delete(1.0,END)
    
'''OLD PROTOCOL MTUOC
def translate_segment_MTUOC(segment):
    translation=""
    try:
        ws.send(segment)
        translation = ws.recv()
    except:
        errormessage="Error retrieving translation from MTUOC: \n"+ str(sys.exc_info()[1])
        messagebox.showinfo("Error", errormessage)
    return(translation)
'''

def translate_segment_MTUOC(segment,id=101,srcLang="en-US",tgtLang="es-ES",):
    import random
    global urlMTUOC
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        #params = [{ "id" : id},{ "src" : segment},{ "srcLang" : srcLang},{"tgtLang" : tgtLang}]
        params={}
        params["id"]=random.randint(0, 10000)
        params["src"]=segment
        params["srcLang"]=srcLang
        params["tgtLang"]=tgtLang
        response = requests.post(urlMTUOC, json=params, headers=headers)
        
        target = response.json()
        translation=target["tgt"]
    except:
        errormessage="Error retrieving translation from MTUOC: \n"+ str(sys.exc_info()[1])
        messagebox.showinfo("Error", errormessage)
    return(translation)
    
def translate_segment_OpenNMT(segment):
    global urlOpenNMT
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        params = [{ "src" : segment}]
        response = requests.post(urlOpenNMT, json=params, headers=headers)
        target = response.json()
        translation=target[0][0]["tgt"]
    except:
        errormessage="Error retrieving translation from OpenNMT: \n"+ str(sys.exc_info()[1])
        messagebox.showinfo("Error", errormessage)
    return(translation)

    
def translate_segment_NMTWizard(segment):
    global urlNMTWizard
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        params={ "src": [  {"text": segment}]}
        response = requests.post(urlNMTWizard, json=params, headers=headers)
        print("RESPONSE",response)
        target = response.json()
        print("TARGET",target)
        translation=target["tgt"][0][0]["text"]
    except:
        print(sys.exc_info())
        errormessage="Error retrieving translation from NMTWizard: \n"+ str(sys.exc_info()[1])
        messagebox.showinfo("Error", errormessage)
    return(translation)
    
def translate_segment_ModernMT(segment):
    global urlModernMT
    params={}
    params['q']=segment
    response = requests.get(urlModernMT,params=params)
    target = response.json()
    translation=target['data']["translation"]
    return(translation)
        
def translate_segment_Moses(segment):

    translation=""
    try:
        param = {"text": segment}
        result = proxyMoses.translate(param)
        translation=result['text']
    except:
        errormessage="Error retrieving translation from Moses: \n"+ str(sys.exc_info()[1])
        messagebox.showinfo("Error", errormessage)
    return(translation)
    
def translate_segment(segment):
    MTEngine=connecto_ListBox_TypeList.get(ACTIVE)
    #if MTEngine=="MTUOC":
    #    translation=translate_segment_MTUOC(segment)
    if MTEngine=="MTUOC":
        translation=translate_segment_MTUOC(segment)
    elif MTEngine=="OpenNMT":
        translation=translate_segment_OpenNMT(segment)
    elif MTEngine=="NMTWizard":
        translation=translate_segment_NMTWizard(segment)
    elif MTEngine=="ModernMT":
        translation=translate_segment_ModernMT(segment)
    elif MTEngine=="Moses":
        translation=translate_segment_Moses(segment)
    translation=translation.replace("\n"," ")
    return(translation)
def translate_para(para):
    print("PARA",para)
    sws=connecto_T_AsktoSegment.state()
    if len(sws)>0 and sws[0]=="selected":
        sws=True
    else:
        sws=False
    if sws:
        translationpara=[]
        srx_rules = srx_segmenter.parse(connecto_E_Segmentation.get())
        tree = ET.parse(connecto_E_Segmentation.get())

        root = tree.getroot()
        
        for lm in root.iter('{http://www.lisa.org/srx20}languagemap'):
            regexp=lm.attrib['languagepattern']
            languagerulename=lm.attrib['languagerulename']
            regexpcomp=re.compile(regexp)
            trobat=re.match(regexpcomp,connecto_E_SL.get())
            if trobat:
                break
        try:
            segmenter = srx_segmenter.SrxSegmenter(srx_rules[languagerulename],para)
        except:
            segmenter = srx_segmenter.SrxSegmenter(srx_rules["Default"],para)
        segments=segmenter.extract()
        for s in segments[0]:
            ts=translate_segment(s)
            translationpara.append(ts)
        translationfinal=[]
        for i in range(0,len(translationpara)):
            translationfinal.append(segments[1][i])
            translationfinal.append(translationpara[i])
            
        return("".join(translationfinal))
    else:
        translation=translate_segment(para)
        return(translation)

def translate_test():
    sourcetext=test_text_source.get("1.0",END)
    traduccio=translate_para(sourcetext)
    test_text_target.delete(1.0,END)
    test_text_target.insert(1.0,traduccio)
    
def open_source_text_file():
    filename_in_txt = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*"),("text files", "*.txt")))
    text_frame_E_source.delete(0,END)
    text_frame_E_source.insert(0,filename_in_txt)
    if os.path.isfile(text_frame_E_TMX.get()):
        filename_tmx=filename_in_txt.replace(".txt","")+"-"+connecto_E_SL.get()+"-"+connecto_E_TL.get()+".tmx"
        text_frame_E_TMX.delete(0,END)
        text_frame_E_TMX.insert(0,filename_tmx)
    
    return

def open_target_text_file():
    filename_out_txt = asksaveasfilename(initialdir = filepathin, filetypes = (("All files", "*"),("text files", "*.txt")))
    text_frame_E_target.delete(0,END)
    text_frame_E_target.insert(0,filename_out_txt)
    if not os.path.isfile(filename_out_txt):
        a=open(filename_out_txt, 'w')
        a.close()
    return
    
def open_TMX_file():
    filename_tmx = asksaveasfilename(initialdir = filepathin, filetypes = (("All files", "*"),("TMX files", "*.tmx")))
    text_frame_E_TMX .delete(0,END)
    text_frame_E_TMX.insert(0,filename_tmx)
    return
    
def translate_text_file():
    
    process=True
    if not os.path.isfile(text_frame_E_source.get()):
        errormessage="A source file should be given!"
        messagebox.showinfo("Error", errormessage)
        process=False
        return
    if not os.path.isfile(text_frame_E_target.get()):
        errormessage="A target file should be given!"
        messagebox.showinfo("Error", errormessage)
        process=False
        return
    if process:
        entrada=codecs.open(text_frame_E_source.get(),"r",encoding=textfile_encoding)
        sortida=codecs.open(text_frame_E_target.get(),"w",encoding=textfile_encoding)
        resultat=[]
        for linia in entrada:
            linia=linia.rstrip()
            traduccio=translate_para(linia)
            sortida.write(traduccio+"\n")
            resultat.append((linia,traduccio))
            
    exporttmx=text_frame_Check_TMX.state()
    if "selected" in exporttmx:
        export_tmx(resultat,text_frame_E_TMX.get())
        
def export_tmx(resultat,tmxfile):
    sortidatmx=codecs.open(tmxfile,"w",encoding="utf-8")
    root = Element('tmx')
    root.set('version', '1.4')
    header = SubElement(root, 'header')
    body = SubElement(root, 'body')
    for transunit in resultat:
        segment1=transunit[0]
        segment2=transunit[1]
        tu=SubElement(body, 'tu')
        
        tuv = SubElement(tu,'tuv')
        tuv.set('xml:lang',connecto_E_SL.get())
        seg= SubElement(tuv,'seg')
        seg.text=segment1
        
        tuv = SubElement(tu,'tuv')
        tuv.set('xml:lang',connecto_E_TL.get())
        seg= SubElement(tuv,'seg')
        seg.text=segment2
    sortidatmx.write((prettify(root)))


def open_source_xliff_file():
    filename_in_xliff=""
    filename_in_xliff = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*.*"),("XLIFF files", "*.xlf"),("SDLXLIFF files", "*.sdlxliff"),("MXLIFF files","*.mxliff")))
    xliff_frame_E_source.delete(0,END)
    xliff_frame_E_source.insert(0,filename_in_xliff)
    
    if xliff_frame_E_TMX.get()=="":
        filename_tmx=filename_in_xliff.replace(".txt","")+"-"+connecto_E_SL.get()+"-"+connecto_E_TL.get()+".tmx"
        xliff_frame_E_TMX.delete(0,END)
        xliff_frame_E_TMX.insert(0,filename_tmx)

    return
    
def open_target_xliff_file():
    filename_out_xliff = ""
    filename_out_xliff = asksaveasfilename(initialdir = filepathout, filetypes = (("All files", "*.*"),("XLIFF files", "*.xlf"),("SDLXLIFF files", "*.sdlxliff"),("MXLIFF files","*.mxliff")))
    xliff_frame_E_target.delete(0,END)
    xliff_frame_E_target.insert(0,filename_out_xliff)
    
    if not os.path.isfile(filename_out_xliff):
        a=open(filename_out_xliff, 'w')
        a.close()
    return
    
    
def translate_xliff_file():
    process=True
    if not os.path.isfile(xliff_frame_E_source.get()):
        errormessage="A source XLIFF file should be given!"
        messagebox.showinfo("Error", errormessage)
        process=False
        return
    if not os.path.isfile(xliff_frame_E_target.get()):
        errormessage="A target XLIFF file should be given!"
        messagebox.showinfo("Error", errormessage)
        process=False
        return
    if process:
        xliff_file=xliff_frame_E_source.get()
        xliff_file_out=xliff_frame_E_target.get()
        tree = ET.parse(xliff_file)
        #NAMESPACES FOR XLIFF
        ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
        ET.register_namespace('sdl', "http://sdl.com/FileTypes/SdlXliff/1.0")
        ET.register_namespace('m', "http://www.memsource.com/mxlf/2.0")
        root = tree.getroot()
        resultat=[]
        for tu in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
            translation={}
            childtags=[]
            for child in tu:
                childtags.append(child.tag)
            #segmented
            if "{urn:oasis:names:tc:xliff:document:1.2}seg-source" in childtags:
                #source
                for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}seg-source'):
                    for child in para.iter():
                        if child.tag=="{urn:oasis:names:tc:xliff:document:1.2}mrk":
                            ident=child.attrib['mid']
                            translation[ident]=translate_segment(child.text)
                            resultat.append((child.text,translation[ident]))
                            
                #target
                for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
                    for child in para.iter():
                        if child.tag=="{urn:oasis:names:tc:xliff:document:1.2}mrk":
                            ident=child.attrib['mid']
                            child.text=translation[ident]
                            
            #not segmented
            else:
                for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}source'):
                    translation=translate_para(para.text)
                for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
                    para.text=translation
                    
        tree.write(xliff_file_out,encoding="utf-8",xml_declaration=True)
        exporttmx=xliff_frame_Check_TMX.state()
        if "selected" in exporttmx:
            export_tmx(resultat,xliff_frame_E_TMX.get())    
    

#YAML 

stream = open('config_translator.yaml', 'r',encoding="utf-8")
config=yaml.load(stream,Loader=Loader)
server_Port=config['Server']['port']
server_IP=config['Server']['ip']
server_type=config['Server']['type']
filepathin=config['Filepath']['path_in']
filepathout=config['Filepath']['path_out']
Segmentation_segment=config['Segmentation']['segment']
Segmentation_SRX=config['Segmentation']['SRX_file']


SLcode=config['LanguageCodes']['source']
TLcode=config['LanguageCodes']['target']

textfile_encoding=config['Textfile']['encoding']

maprules={}
maprules["en"]="English"
maprules["eng"]="English"
maprules["es"]="Spanish"
maprules["esp"]="Spanish"
maprules["spa"]="Spanish"



###GRAPHICAL INTERFACE
main_window = Tk()
main_window.title("MTUOC Translator v.1.2")


notebook = ttk.Notebook(main_window)

connecto_frame = Frame(notebook)
connecto_L_Server = Label(connecto_frame,text="Server IP:").grid(sticky="W",row=0,column=0)
connecto_E_Server = Entry(connecto_frame, textvariable=server_IP, width=20,)
connecto_E_Server.grid(sticky="W",row=0,column=1)
connecto_E_Server.insert(0,server_IP)
connecto_L_Port = Label(connecto_frame,text="Server port:").grid(sticky="W",row=1,column=0)
connecto_E_Port = Entry(connecto_frame, textvariable=server_Port, width=20,)
connecto_E_Port.grid(sticky="W",row=1,column=1)
connecto_E_Port.insert(0,server_Port)

connecto_L_List = Label(connecto_frame,text="Server type:").grid(sticky="W",row=2,column=0)

connecto_ListBox_TypeList = Listbox(connecto_frame,selectmode=SINGLE)
connecto_ListBox_TypeList.grid(sticky="W",row=2,column=1)
listTypes=["MTUOC","Moses", "OpenNMT", "NMTWizard", "ModernMT"]
for item in listTypes:
    connecto_ListBox_TypeList.insert(END, item)
connecto_ListBox_TypeList.config(width=0,height=0)

try:
    connecto_ListBox_TypeList.select_set(listTypes.index(server_type))
    connecto_ListBox_TypeList.activate(listTypes.index(server_type))
except:
    pass

connecto_L_SL = Label(connecto_frame,text="Source Language:").grid(sticky="W",row=3,column=0)
connecto_E_SL = Entry(connecto_frame, textvariable=SLcode, width=10,)
connecto_E_SL.grid(sticky="W",row=3,column=1)
connecto_E_SL.insert(0,SLcode)

connecto_T_SL = Label(connecto_frame,text="Target Language:").grid(sticky="W",row=4,column=0)
connecto_E_TL = Entry(connecto_frame, textvariable=TLcode, width=10,)
connecto_E_TL.grid(sticky="W",row=4,column=1)
connecto_E_TL.insert(0,TLcode)


connecto_T_AsktoSegment=ttk.Checkbutton(connecto_frame, text="Segmentation")
connecto_T_AsktoSegment.grid(sticky="W",row=5,column=0)
if Segmentation_segment:
    connecto_T_AsktoSegment.state(["selected"])
else:
    connecto_T_AsktoSegment.state(["!selected"])
connecto_E_Segmentation = Entry(connecto_frame, textvariable=Segmentation_SRX, width=20,)
connecto_E_Segmentation.grid(sticky="W",row=5,column=1)
connecto_E_Segmentation.insert(0,Segmentation_SRX)

connecto_B_Connect=Button(connecto_frame, text = str("Connect"), command=connect,width=10)
connecto_B_Connect.grid(row=6,column=0)
connecto_B_Disconnect=Button(connecto_frame, text = str("Disconnect"), command=disconnect,width=10, state=DISABLED)
connecto_B_Disconnect.grid(row=6,column=1)




#TEST
test_frame = Frame(notebook)
test_text_source=scrolledtext.ScrolledText(test_frame,height=5)
test_text_target=scrolledtext.ScrolledText(test_frame,height=5)
test_text_source.grid(row=0,column=0)
test_text_target.grid(row=1,column=0)
test_B_Clear=Button(test_frame, text = str("Clear"), command=clear_test,width=10)
test_B_Clear.grid(row=2,column=0)
test_B_translate=Button(test_frame, text = str("Translate"), command=translate_test,width=10)
test_B_translate.grid(row=3,column=0)



#TEXT
text_frame = Frame(notebook)
text_frame_B_source=Button(text_frame, text = str("Select source file"), command=open_source_text_file,width=15)
text_frame_B_source.grid(row=0,column=0)
text_frame_E_source = Entry(text_frame,  width=50)
text_frame_E_source.grid(row=0,column=1)
text_frame_B_target=Button(text_frame, text = str("Select target file"), command=open_target_text_file,width=15)
text_frame_B_target.grid(row=1,column=0)
text_frame_E_target = Entry(text_frame,  width=50)
text_frame_E_target.grid(row=1,column=1)
text_frame_Check_TMX = ttk.Checkbutton(text_frame, text="Export TMX")
text_frame_Check_TMX.grid(row=2,column=0)
text_frame_B_TMX=Button(text_frame, text = str("Select TMX file"), command=open_TMX_file,width=15)
text_frame_B_TMX.grid(row=3,column=0)
text_frame_E_TMX = Entry(text_frame,  width=50)
text_frame_E_TMX.grid(row=3,column=1)
text_frame_B_translate=Button(text_frame, text = str("Translate"), command=translate_text_file,width=15)
text_frame_B_translate.grid(row=4,column=0)


#XLIFF
xliff_frame = Frame(notebook)
xliff_frame_B_source=Button(xliff_frame, text = str("Select source file"), command=open_source_xliff_file,width=15)
xliff_frame_B_source.grid(row=0,column=0)
xliff_frame_E_source = Entry(xliff_frame,  width=50)
xliff_frame_E_source.grid(row=0,column=1)
xliff_frame_B_target=Button(xliff_frame, text = str("Select target file"), command=open_target_xliff_file,width=15)
xliff_frame_B_target.grid(row=1,column=0)
xliff_frame_E_target = Entry(xliff_frame,  width=50)
xliff_frame_E_target.grid(row=1,column=1)
xliff_frame_Check_TMX = ttk.Checkbutton(xliff_frame, text="Export TMX")
xliff_frame_Check_TMX.grid(row=2,column=0)
xliff_frame_B_TMX=Button(xliff_frame, text = str("Select TMX file"), command=open_TMX_file,width=15)
xliff_frame_B_TMX.grid(row=3,column=0)
xliff_frame_E_TMX = Entry(xliff_frame,  width=50)
xliff_frame_E_TMX.grid(row=3,column=1)
xliff_frame_B_translate=Button(xliff_frame, text = str("Translate"), command=translate_xliff_file,width=15)
xliff_frame_B_translate.grid(row=4,column=0)

notebook.add(connecto_frame, text="Connect to", padding=30)
notebook.add(test_frame, text="TEST", padding=30)
notebook.add(text_frame, text="TEXT FILE", padding=30)
notebook.add(xliff_frame, text="XLIFF",padding=30)


notebook.pack()
notebook.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
notebook.pack(fill=BOTH, expand=1)
main_window.mainloop()
