# -*- coding: utf-8 -*-
#    MTUOC-Translator-lite
#    Copyright (C) 2020  Antoni Oliver
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

import argparse
import codecs
import sys
import time


#IMPORTS FOR MTUOC CLIENT
from websocket import create_connection
import socket

#IMPORTS FOR MOSES CLIENT
import xmlrpc.client

#IMPORTS FOR OPENNMT / MODERNMT CLIENT
import requests

def print_info(message1,message2=""):
    print(message1,message2)


def connect():
    server_type=args.type
    if server_type=="MTUOC":
        try:
            service="ws://"+args.ip+":"+str(args.port)+"/translate"
            global ws
            ws = create_connection(service)
        except:
            errormessage="Error connecting to MTUOC: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)
            
    elif server_type=="MTUOC2":
        try:
            global urlMTUOC2
            urlMTUOC2 = "http://"+args.ip+":"+str(args.port)+"/translate"
        except:
            errormessage="Error connecting to MTUOC2: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage) 
            
    elif server_type=="Moses":
        try:
            global proxyMoses
            proxyMoses = xmlrpc.client.ServerProxy("http://"+args.ip+":"+str(args.port)+"/RPC2")
        except:
            errormessage="Error connecting to Moses: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)      
            
    elif server_type=="OpenNMT":
        try:
            global urlOpenNMT
            urlOpenNMT = "http://"+args.ip+":"+str(args.port)+"/translator/translate"
        except:
            errormessage="Error connecting to OpenNMT: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)   
    elif server_type=="NMTWizard":
        try:
            global urlNMTWizard
            urlNMTWizard = "http://"+args.ip+":"+str(args.port)+"/translate"
        except:
            errormessage="Error connecting to NMTWizard: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)           
    elif server_type=="ModernMT":
        try:
            global urlModernMT
            urlModernMT = "http://"+args.ip+":"+str(args.port)+"/translate"
        except:
            errormessage="Error connecting to ModernMT: \n"+ str(sys.exc_info()[1])
            print_info("Error", errormessage)
    
def translate_segment_MTUOC(segment):
    translation=""
    try:
        ws.send(segment)
        translation = ws.recv()
    except:
        errormessage="Error retrieving translation from MTUOC: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
    return(translation)

    
def translate_segment_MTUOC2(segment,id=101,srcLang="en-US",tgtLang="es-ES",):
    import random
    global urlMTUOC2
    translation=""
    try:
        headers = {'content-type': 'application/json'}
        #params = [{ "id" : id},{ "src" : segment},{ "srcLang" : srcLang},{"tgtLang" : tgtLang}]
        params={}
        params["id"]=random.randint(0, 10000)
        params["src"]=segment
        params["srcLang"]=srcLang
        params["tgtLang"]=tgtLang
        response = requests.post(urlMTUOC2, json=params, headers=headers)
        target = response.json()
        translation=target[0][0]["tgt"]
    except:
        errormessage="Error retrieving translation from MTUOC2: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
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
        target = response.json()
        translation=target["tgt"][0][0]["text"]
    except:
        print(sys.exc_info())
        errormessage="Error retrieving translation from NMTWizard: \n"+ str(sys.exc_info()[1])
        print_info("Error", errormessage)
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
        print_info("Error", errormessage)
    return(translation)
    
def translate_segment(segment):
    MTEngine=args.type
    if MTEngine=="MTUOC":
        translation=translate_segment_MTUOC(segment)
    elif MTEngine=="MTUOC2":
        translation=translate_segment_MTUOC2(segment)
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



parser = argparse.ArgumentParser(description='MTUOC-Translator-lite: command line MTUOC translator. Translates segmented text files (one segment per line).')
parser.add_argument('--ip', dest='ip', help='The ip of the server or localhost', action='store',required=True)
parser.add_argument('--port', dest='port', help='The port used by the server', action='store',required=True)
parser.add_argument('--type', dest='type', help='The type of server. One of: MTUOC, Moses, OpenNMT, NMTWizard, ModernMT', action='store',required=True)
parser.add_argument('-i','--input', dest='input', help='The input file', action='store',required=True)
parser.add_argument('-o','--output', dest='output', help='The output file', action='store',required=True)
parser.add_argument('-e','--encoding', dest='encoding', help='The character encoding for input and output', action='store',default="utf-8")
args = parser.parse_args()

connect()

entrada=codecs.open(args.input,"r",encoding=args.encoding)
sortida=codecs.open(args.output,"w",encoding=args.encoding)
resultat=[]
cont=0
start_time = time.time()
chars=0
for linia in entrada:
    linia=linia.rstrip()
    cont+=1
    chars+=len(linia)
    print(cont)
    print(linia)
    traduccio=translate_segment(linia)
    print(traduccio)
    print("------------------------------------------")
    sortida.write(traduccio+"\n")
    resultat.append((linia,traduccio))
end_time = time.time()
total_time=end_time-start_time
          
print("TOTAL TIME:", round(total_time,2))
print("TOTAL SEGMENTS:", cont)
print("TOTAL CHARS:", chars)
ss=cont/total_time
print("SEGMENTS/SECONDS:",round(ss,2))
cs=chars/total_time
print("CHARS/SECONDS:",round(cs,2))
