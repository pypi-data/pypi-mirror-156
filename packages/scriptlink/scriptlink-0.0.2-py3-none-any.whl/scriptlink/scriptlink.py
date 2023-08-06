#Kill Driver is Control Escape#
#mss requ//ascreentestbugged//trigger hook bug//
import ctypes, ctypes.util
import logging
import threading
import time
import sys
import os
import io
import numpy as np
import cv2
from numpy.lib.stride_tricks import as_strided
from .constants import *
whereislib = ctypes.util.find_library("msvcrt")
ct_clib = ctypes.cdll.LoadLibrary(whereislib)
c_atoi=ct_clib.atoi
'''Classes:
class Fps Ex: fp=Fps();fp.update()
class Sprite:Sprite(filename, x,y,w,h,index,dx,dy,di)
Class Menu:menuinfo={id:["type","display text or image",parentid,status]}
           MenuClass(menuinfo,menucallback,VK["CapsLock"],0,0)'''

#np_load_old = np.loadd
# modify the default parameters of np.load
#np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)


print(os.path.join(os.path.dirname(__file__), 'test.txt'))
HoloGraphicsCallback=None
holoconfig={"running":1,"data":0,"fontnum":99}
cd = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'scriptlink.dll'))
def ClockIt(s=" t"):
    print(s,":",clock()-ClockIt.t)
    ClockIt.t=clock()
ClockIt.t=0
def CLAMP(a,b,c):
    if (a>c):a=c;
    elif (a<b):a=b
    return a;
def signedcmp(a, b):
    return (a >= b) - (a < b)
def prshape(a):
    print(type(a),":",a.shape)
def conv2ds(a, b, s=1):
    Hout = (a.shape[1] - b.shape[0]) // s + 1
    Wout = (a.shape[2] - b.shape[1]) // s + 1
    Stride = (a.strides[0], a.strides[1] * s, a.strides[2] * s, a.strides[1], a.strides[2], a.strides[3])

    a = as_strided(a, (a.shape[0], Hout, Wout, b.shape[0], b.shape[1], a.shape[3]), Stride)

    return np.tensordot(a, b, axes=3)
def getdatetime(time="%m/%d/%y %H:%M:%S"):
    from datetime import datetime
    now = datetime.now()
    dictt={"month":"%m","day":"%d","year":"%y","hour":"%H","minute":"%M","second":"%S","sec":"%S","min":"%M"}
    for i,j in dictt.items():time=time.replace(i,j)
    dt_string = now.strftime(time)
    return dt_string

#cd.holoinit()
#cd.movemouseto.argtypes = c_size_t,c_size_t
#cd.movemouseto.restype = None
#cd.dragmouseto.argtypes = c_size_t,c_size_t,c_size_t,c_size_t,c_size_t
#cd.dragmouseto.restype = None

#######################TransparentGUI##################

#Button(x,y,w,h,name,func)
#resetdraw():
#drawtext(x,y,color,text,num=-1):
#drawbox(x,y,w,h,sz,color,num=-1):
#drawbmp(x,y,color,text,num=-1):

#######################Utility#########################

#SetTrigger(key,func,delay=.500)
#SetToggle(key,func,delay=.500)

WaitAnyInput=cd.waitanyinput #WaitAnyInput() returns key

Sleep=cd.sleep            #Sleep(x)
WaitScreenChange=cd.WaitScreenChange  #WaitScreenChange(percent_change,max_time_towait_ms)
#_render=cd.renderover
holodrawcounter=0
#######################LoadData########################
ChangeCaptureMode=cd.ChangeCaptureMode
GetFontName=cd.getfontname #GetFontName(index)
cd.getfontname.restype = ctypes.c_char_p # override the default return type (int)
GetFontLetters=cd.getfonts #GetFonts(pointer,fontindex)
cd.getfonts.argtypes = ctypes.POINTER(ctypes.POINTER(ctypes.c_int32)),ctypes.c_size_t
###########################Windows Utils#######################################

h_FileExists=cd.FileExistsW
def FileExists(string):
    p = ctypes.create_unicode_buffer(string)
    return h_FileExists(p)
GetActiveWindowNum=cd.GetActiveWindowNum
ResizeWindow=cd.ResizeWindowP#ResizeWindow(windownum,w,h)
MoveWindow=cd.MoveWindowP#MoveWindow(windownum,x,y,w,h)
RGBCOLORS={"red":0xFFFF0000,"green":0xFF00CC00,"blue":0xFF0000FF,"green":0xFF00CC00,"yellow":0xFF00CCCC,"white":0xFFFFFFFF,"black":0xFF010101}
class WrapStruct(ctypes.Structure):
     _fields_ = [ ('x1',ctypes.c_int32),('y1',ctypes.c_int32),('x2',ctypes.c_int32),('y2',ctypes.c_int32),('sz',ctypes.c_int32),('area',ctypes.c_int32),('num',ctypes.c_int32), ('color',ctypes.c_int32), ('magnitude',ctypes.c_int32)]
class LineStruct(ctypes.Structure):
     _fields_ = [ ('x',ctypes.c_int32), ('y',ctypes.c_int32), ('x2',ctypes.c_int32),('y2',ctypes.c_int32),('ming',ctypes.c_int32),('leng',ctypes.c_int32) ]
class FillsStruct(ctypes.Structure):
     _fields_ = [ ('x1',ctypes.c_int32), ('y1',ctypes.c_int32), ('x2',ctypes.c_int32),('y2',ctypes.c_int32),('gd',ctypes.c_int32),('ct',ctypes.c_int32),('chroma',ctypes.c_int32),('color',ctypes.c_int32),('minarea',ctypes.c_int32),('maxarea',ctypes.c_int32),('minsz',ctypes.c_int32),('maxsz',ctypes.c_int32),('frame',ctypes.c_int32),('sort',ctypes.c_int32) ]
def FindFills(x,y,w,h,mingradient=30,frame=1,jump=0,chroma=0,color=121,minarea=0,maxarea=4000000,minsz=0,maxsz=4000000,sort=0):#chroma weights the color portion of the color filter vs the brightness
    if not hasattr(FindFills,"sz"):FindFills.sz=0;
    if (w*h!=FindFills.sz and frame==1):
        FindFills.sz=w*h
        FindFills._data=(ctypes.c_int8 * FindFills.sz*4)()
        print("\r\nnewsz"+str(FindFills.sz)+str(FindFills._data))
        
    finfo=FillsStruct(x,y,x+w,y+h,mingradient,0,chroma,color,minarea,maxarea,minsz,maxsz,frame,sort);
    _findfills=cd.FindFills
    _findfills.restype = ctypes.POINTER(WrapStruct)
    boxes=_findfills(FindFills._data,ctypes.pointer(finfo));
    ct=finfo.ct
    #print("%d %d %d %d %d %d %d %d" %(finfo.x1,finfo.y1,finfo.x2,finfo.y2,finfo.gd,finfo.len,finfo.ct,finfo.chrom))
    if (frame!=False):
        g=bytearray(FindFills._data)
        frame = np.ctypeslib.as_array(g)
        frame=np.reshape(frame,(h,w,4))
        return frame,ct,boxes
    return ct,boxes;
    '''c=finfo.ct
    for i in range(c):
        b=boxes[i]
        print("%d %d %d %d" %(b.color,b.sz,b.x1,b.y1))
    g=bytearray(FindFills._data)
    frame = np.ctypeslib.as_array(g)
    frame=np.reshape(frame,(h,w,4))
    cv2.imshow("new",frame)'''
    #if (c==0):return 0,None
    #return c,boxes;
def FindLineOnScreen(x,y,maxw,maxh,mingradient=30,leng=0,dst=None):
    linfo=LineStruct(x,y,x+maxw,y+maxh,mingradient,leng);
    ret=cd.FindLineOnScreen(ctypes.pointer(linfo));
    linfo.leng=ret
    if (ret==0):return None
    if (dst!=None):
        pointer(dst)[0] = linfo
    return linfo;
#place the point to the left of the target line or region
def FindBoundingBox(x,y,maxw=50,maxh=50,mingradient=30,leng=0,dst=None):
    linfo=LineStruct(x,y,maxw,maxh,mingradient,leng);
    ret=cd.FindBoundingBoxRight(ctypes.pointer(linfo));
    linfo.leng=ret
    if (dst!=None):
        pointer(dst)[0] = linfo
    return linfo;
class WindowsInfo(ctypes.Structure):
     _fields_ = [ ('x',ctypes.c_int32), ('y',ctypes.c_int32), ('w',ctypes.c_int32),('h',ctypes.c_int32),('name', ctypes.c_char * 200),('exename', ctypes.c_char * 200) ]
def GetWindowInfo(windownum):
    winfo=WindowsInfo(0,0,0,0,b'kk')
    cd.GetWindowInfoPy(windownum,ctypes.pointer(winfo));
    return winfo
def GetWindowXY(windownum):
    winfo=WindowsInfo(0,0,0,0,b'kk')
    cd.GetWindowInfoPy(windownum,ctypes.pointer(winfo));
    return winfo.x,winfo.y;
def GetWindowXYWH(windownum):
    winfo=WindowsInfo(0,0,0,0,b'kk')
    cd.GetWindowInfoPy(windownum,ctypes.pointer(winfo));
    return winfo.x,winfo.y,winfo.w,winfo.h;
def GetWindowExeAndTitle(windownum):
    winfo=WindowsInfo(0,0,0,0,b'kk')
    cd.GetWindowInfoPy(windownum,ctypes.pointer(winfo));
    return winfo.exename.decode('utf-8'),winfo.name.decode('utf-8');
GetLocalFolder=os.getcwd()+"\\"
GetMouseX=cd.GetMouseX #GetMouseX()
GetMouseY=cd.GetMouseY #GetMouseY()
def GetMouseXY():return GetMouseX(),GetMouseY();
GetScreenX=cd.GetScreenX #GetScreenX()
GetScreenY=cd.GetScreenY
ScreenX=GetScreenX();ScreenY=GetScreenY();
def GetScreenXY():return GetScreenX(),GetScreenY();
ClockTime=cd.clocktime
def clock():return ClockTime();
GetKeyState=cd.getkeystate #GetKeyState(virtualkey)
GetMouseClick=cd.getmouseclickcoords #GetMouseClick(virtualkey,x1,y1,x2,y2)
#ConsoleGetMouseScroll=cd.ConsoleGetMouseScrollLast
GetLastKey=cd.getlastkey
GetNewLastKey=cd.getnewlastkey
GetKeyClick=cd.getkeyclick
#GetKeyClickMenu=cd.getkeyclickmenu
GetMenuKey=cd.getnewlastkeymenu
def BlockMenuInput(on,time=2000):
    BlockMenuInput=cd.blockinput(on,time)#(0 or 1, all keyboard and left mouse)
def BlockKeyInput(key,on,time=10000):
    cd.blockkeyinput(key,on,time)#specific key block BlockKeyInput(key,0 or 1)
def BlockMouseInput(mousekey,on,time=10000):
    cd.blockmouseinput(mousekey,on,time)#specific mouse block BlockMouseInput(mouseval,0 or 1)
###############################################################Poker#################################
Poker_ev7=cd.poker_ev7
Poker_evomaha=cd.poker_evomaha
Poker_evomahalow=cd.poker_evomahalow
def poker_holdem_equity(h1,h2,boardcards,num_opponents=1,handrange=0):
    cards=[0]*5
    cards[:len(boardcards)] = boardcards
    pct=cd.poker_holdem_equity(h1,h2,len(boardcards),num_opponents,handrange,cards[0],cards[1],cards[2],cards[3],cards[4]);
    return pct/10;
def poker_omaha_equity(h1,h2,h3,h4,boardcards,num_opponents=1,handrange=0):
    cards=[0]*5
    cards[:len(boardcards)] = boardcards
    pct=cd.poker_omaha_equity(h1,h2,h3,h4,len(boardcards),num_opponents,handrange,cards[0],cards[1],cards[2],cards[3],cards[4]);
    return pct/10;
def poker_omahahl_equity(h1,h2,h3,h4,boardcards,num_opponents=1,handrange=0):
    cards=[0]*5
    cards[:len(boardcards)] = boardcards
    pct=cd.poker_omahahl_equity(h1,h2,h3,h4,len(boardcards),num_opponents,handrange,cards[0],cards[1],cards[2],cards[3],cards[4]);
    return pct/10;

############################################################Input Actions##############################

SetMouseMoveLatency=cd.setmousespeed #SetMouseSpeed(0-100)
SetMouseClickLatency=cd.setmousespeed #SetMouseSpeed(0-100)
MouseMovePixel=cd.mousemovepixel #MoveMouse(x,y)
MouseMovePercent=cd.mousemovepercent #MoveMouse(x,y)
MouseMoveRelativePercent=cd.mousemoverelativepercent #MoveMouse(x,y)
MouseDown=cd.mousedown #MouseDown(Mousebutton 1-2)
MouseUp=cd.mouseup #MouseDown(Mousebutton 1-2)
MouseClickPercent=cd.mouseclickpercent #MouseClickPercent(x1,y1,MouseButton 1-2)
MouseDragPercent=cd.mousemovepercent #DragMouse(x1,y1,x2,y2,Mousebutton 1-2)
MouseDragPixel=cd.mousemovepixel #DragMouse(x1,y1,x2,y2,Mousebutton 1-2)
KeyClickScanCode=cd.keyclickdx   #DirectX Scan Code
KeyDownScanCode=cd.keydowndx   #DirectX Scan Code
KeyUpScanCode=cd.keyupdx   #DirectX Scan Code
KeyDown=cd.keydownvk   #VkCode
KeyUp=cd.keyupvk   #VkCode
KeyClick=cd.keyclickvk   #VkCode
PressLetterDown=cd.keydownletter   #VkCode
PressLetterUp=cd.keyupletter   #VkCode
PressLetterDownUp=cd.keyclickletter   #VkCode
def KeyClickLetter(k):        #KeyClick(letter/num) same as PressLetterDownUp
    KeyClickDX(cd.chartokey(ord(k)))
DetectKeyStrokes=cd.DetectKeys
GetMouseRoll=cd.getmouseroll
#508582usyyyyyyooo90899.yo
def TypeString(s,delay=5):
    cd.typestring(s,delay)
def printclock(s=""):
    t=clock()-printclock.ct
    printclock.ct=clock()
    print(str(s)+" clock:"+str(t))
printclock.ct=0
def KillPython():
    cd.BotExit();
    return;
    print(os.getpid())
    PROCESS_TERMINATE = 1
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, os.getpid())
    ctypes.windll.kernel32.TerminateProcess(handle, -1)
    ctypes.windll.kernel32.CloseHandle(handle)
def SlowMoveMouse(relx,rely):
    dy=1*rely/relx
    while (relx>0):
        dy=rely/relx
        MouseMoveRelativePercent(1,int(dy));
        relx-=1
        Sleep(200)
def MouseLeftClick(time):
    MouseDown(1)
    Sleep(time)
    MouseUp(1)
def MouseRightClick(time):
    MouseDown(2)
    Sleep(time)
    MouseUp(2)
#######################################################################Drawing##############################

h_ScreenCaptureToFile=cd.ScreenCapturetoFileW
def ScreenCaptureToFile(string,x=0,y=0,w=-1,h=-1):
    p = ctypes.create_unicode_buffer(string)
    h_ScreenCaptureToFile(p,x,y,w,h)

h_drawstring=cd.DrawStringW
def DrawString(string,x,y,color,fontnum=0):
    p = ctypes.create_unicode_buffer(string)
    h_drawstring(p,x,y,color,fontnum)

h_drawstringbox=cd.DrawStringBoxW
def DrawStringBox(string,x,y,w,h,color,fontnum=0):
    p = ctypes.create_unicode_buffer(string)
    h_drawstringbox(p,x,y,w,h,color,fontnum)

DrawSolidColor=cd.DrawSolidColor#int DrawSolidColor(int x, int y, int w, int h,int color)
DrawLineColor=cd.DrawLineColor#int DrawLineColor(int x, int y, int x2, int y2, int color,int thick)
DrawBox=cd.DrawBox  #int DrawBox(int x, int y, int w, int h, int color,int thick)





############################################################Image/Sprite Utilities##############################

h_GetScreenColor=cd.GetScreenColor
def GetScreenColor(x,y):
    target=h_GetScreenColor(x,y)
    lc=(0x000000FF & target,(0x0000FF00 & target)>>8,(0x00FF0000 & target)>>16,(0xFF000000 & target)>>24)
    return lc
h_FindTextinImageW=cd.FindTextinImageW
def FindTextinImage(name):
    n = ctypes.create_unicode_buffer(name)
    text=ctypes.create_string_buffer(3000)
    r=h_FindTextinImageW(n,text)
    return text

#SaveImage("textimage.bmp",res[0],res[1]+60,800,100);
h_SpliceImageW=cd.SpliceImageW
def SpliceImage(namesmall,namebig,x,y,w,h):
    n = ctypes.create_unicode_buffer(namesmall)
    n2 = ctypes.create_unicode_buffer(namebig)
    x=ctypes.c_int()
    y=ctypes.c_int()
    r=h_SpliceImageW(n,n2,x,y,w,h)

#res=FastFindImage("fastfingersbox.bmp", "screen.bmp") 
h_FastFindImageW=cd.FastFindImageW
def FastFindImage(needle,haystack):
    n = ctypes.create_unicode_buffer(needle)
    h = ctypes.create_unicode_buffer(haystack)
    x=ctypes.c_int()
    y=ctypes.c_int()
    r=h_FastFindImageW(n,h,ctypes.byref(x),ctypes.byref(y))
    if (r==1):
        return x,y
    else: return -1,-1

h_FindImageW=cd.FindImageW
#cd.getfonts.argtypes = ctypes.POINTER(ctypes.POINTER(ctypes.c_int32))
def FindImageonScreen(needle,haystack="screen.bmp"):
    n = ctypes.create_unicode_buffer(needle)
    h = ctypes.create_unicode_buffer(haystack)
    #x=ctypes.c_int()
    #y=ctypes.c_int()
    p=(ctypes.c_int * 100)()
    #p = ctypes.POINTER(ctypes.c_int32)()
    r=h_FindImageW(n,h,ctypes.byref(p))
    if (r==0):return 0,0,0,[]
    #print(r)
    pts=[]
    w=p[0];h=p[1];
    for i in range(1 ,r+1):
        pts.append((p[2*i],p[2*i+1]))
    return w,h,r,pts

h_SlowFindImageW=cd.SlowFindImageW
def SlowFindImage(needle,haystack):
    n = ctypes.create_unicode_buffer(needle)
    h = ctypes.create_unicode_buffer(haystack)
    x=ctypes.c_int()
    y=ctypes.c_int()
    r=h_SlowFindImageW(n,h,ctypes.byref(x),ctypes.byref(y))
    if (r==1):
        return x,y
    else: return -1,-1

h_GetBMPHistW=cd.GetBMPHistW
def GetBMPHist(name):
    n = ctypes.create_unicode_buffer(name)
    p=(ctypes.c_int * (256*3))()
    #self._data=(ctypes.c_int8 * self.sz*4)()
    r=h_GetBMPHistW(n,ctypes.byref(p))
    print(p)
    #for i in range(1 ,r+1):
    #    pts.append((p[2*i],p[2*i+1]))
    return r,p

h_TrimColorImageW=cd.TrimColorImageW
def TrimColorImage(string,Trim=0):
    p = ctypes.create_unicode_buffer(string)
    h_TrimColorImageW(p,Trim)
    
h_MaskColorImageW=cd.MaskColorImageW
def MaskColorImage(string,mask=0):
    p = ctypes.create_unicode_buffer(string)
    h_MaskColorImageW(p,mask)
    
h_ReloadSpriteW=cd.ReloadSpriteW
def ReloadSprite(string):
    p = ctypes.create_unicode_buffer(string)
    h_ReloadSpriteW(p)

h_createfont=cd.HoloCreateFontW
def CreateFont(name,size,number):
    print(name,size,number)
    p = ctypes.create_unicode_buffer(name)
    h_createfont(p,size,number)

#def DrawBox(x,y,w,h,color,thick=1):
    #h_drawbox(x,y,w,h,color,thick)
#def DrawSolidColor(x,y,w,h,color):
    #h_DrawSolidColor(x,y,w,h,color)
  
h_drawspritenaked=cd.DrawSpriteNakedW
def DrawSpriteNaked(string,x,y):
    p = ctypes.create_unicode_buffer(string)
    h_drawspritenaked(p,ctypes.c_float(x),ctypes.c_float(y))
  
h_drawsprite=cd.DrawSpriteWA
def DrawSprite(string,x,y,srcx,srcy,w,h):
    p = ctypes.create_unicode_buffer(string)
    h_drawsprite(p,ctypes.c_float(x),ctypes.c_float(y),srcx,srcy,w,h)

h_drawspritei=cd.DrawSpriteWI
def DrawSpriteIndex(string,x,y,w,h,index):
    p = ctypes.create_unicode_buffer(string)
    h_drawspritei(p,ctypes.c_float(x),ctypes.c_float(y),w,h,index)

h_drawspriteim=cd.DrawSpriteWIMouse
def DrawSpriteIndexMouseOver(string,x,y,w,h,index):
    p = ctypes.create_unicode_buffer(string)
    h_drawspriteim(p,ctypes.c_float(x),ctypes.c_float(y),w,h,index)

h_drawspriteiml=cd.DrawSpriteWIMouseL
def DrawSpriteIndexMouseOverL(string,x,y,w,h,index):
    p = ctypes.create_unicode_buffer(string)
    h_drawspriteiml(p,ctypes.c_float(x),ctypes.c_float(y),w,h,index)
    #h_drawsprite(p,ctypes.c_float(x),ctypes.c_float(y),srcx,srcy,w,h)

# t0 = time.time()
# for i in range(1000000):
    # p = create_string_buffer(b"Hetreeello")
# print (time.time() - t0), "seconds wall time"
# t0 = time.time()
# p = create_string_buffer(b"Hetreeello")
# for i in range(1000000):
    # cd.teststring(p,5,10)
# print (time.time() - t0), "seconds wall time"
# t0 = time.time()
# p = create_string_buffer(b"Hetreeello")
# teststring=cd.teststring
# #cd.teststring.argtypes=POINTER(c_char),c_int32,c_int32
# for i in range(1000000):
    # teststring(p,5,10)
# print (time.time() - t0), "seconds wall time"
#h_DrawString=cd.DrawString#(int x, int y, COLORREF color, char* text)
    

    
# h_DrawString=cd.DrawString#(int x, int y, COLORREF color, char* text)
# cd.DrawString.argtypes = c_int32,c_int32,POINTER(POINTER(c_int32)),c_size_t
# DrawSprite=drawsprite#(char *name, float x, float y, RECT srcRect)
# cd.getfonts.argtypes = POINTER(POINTER(c_int32)),c_size_t
#DrawText=cd.drawtext
#DrawBox=cd.DrawBoxOver
#EraseScreen=cd.erasescreen;
#GetUserRect=cd.getuserrect

GetImageMag=cd.ImageMag #GetFonts(pointer,fontindex)
cd.ImageMag.argtypes = ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32)
def ImageMag(x,y):
    data1 = (ctypes.c_int32 * 5)()
    #p = ctypes.POINTER(ctypes.c_int32)()
    GetImageMag(x,y,ctypes.cast(data1, ctypes.POINTER(ctypes.c_int32)))
    #for i in range(4):
        #print(data1[i])
    #t=np.ctypeslib.as_array(p, shape=(4,))
    return data1
    
def WaitKey(key):
    k=GetKeyState(key)
    while(1):
        k=GetKeyState(key)
        if (k!=0): break
        Sleep(50)
def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

class ImageSorterClass:
    
    def __init__(self,loadname='data.npy',h=28,w=28,sz=4096):
        np_load_old = np.load
        self.loadnew = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)
        self.h=h;self.w=w;self.sz=sz
        self.arraysz=self.sz*self.h*self.w
        self.imgs=np.empty(self.arraysz, dtype=np.uint8)
        self.res=np.arange(0, self.sz, 1, dtype=int)
        self.imgsz=self.w*self.h
        self.img_arrayindex=0;self.imgno=0
        self.wtsname=loadname
        self.img_mainct=0
        if (len(loadname)>0):
            if (os.path.exists(loadname)==0):
                print("failed to load",loadname)
            else:
                print("loaded",loadname)
                self.W=self.loadnew(loadname)
    def printweights(self):
        W = self.W
        print("len:",len(W))
        for a in W:
            print(a.shape)
        for a in W:
            print(a)
            
    def modelpredict(self,X):
        W = self.W#self.model.get_weights()#W = self.W
        #print(X.shape)
        X      = X.reshape(-1)           #Flatten   X      = X.reshape((X.shape[0],-1))
        #print(X.shape,W[0].shape,W[1].shape)
        X      = X @ W[0] + W[1]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[2] + W[3]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[4] + W[5]                      #Dense
        #print(X)
        #X      = np.exp(X)/np.exp(X).sum(1)[...,None] #SoftmaxX      = np.exp(X) / np.sum(np.exp(X));#np.exp(X)/np.exp(X).sum(1)[...,None] #Softmax
        #print(X,np.argmax(X))
        return X
    def singlepredict(self,X):
        W = self.W#self.model.get_weights()#W = self.W
        #print(X.shape)
        X      = X.reshape(-1)           #Flatten   X      = X.reshape((X.shape[0],-1))
        #print(X.shape,W[0].shape,W[1].shape)
        X      = X @ W[0] + W[1]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[2] + W[3]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[4] + W[5]                      #Dense
        #print(X)
        #X      = np.exp(X)/np.exp(X).sum(1)[...,None] #SoftmaxX      = np.exp(X) / np.sum(np.exp(X));#np.exp(X)/np.exp(X).sum(1)[...,None] #Softmax
        #print(X,np.argmax(X))
        return X
    '''def showimage(self,n):
        two_d = np.reshape(self.imgs[n*self.imgsz:n*self.imgsz+self.imgsz], (28, 28))
        plt.imshow(two_d, cmap='gray')
        plt.suptitle('imgno:'+str(n)+str(self.res[n]))
        plt.show()'''
    def findimgfile(self,name):
        tempfile=GetLocalFolder+name
        img = cv2.imread(tempfile,cv2.IMREAD_UNCHANGED)
        return self.find(img)
        '''img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        r=resized.reshape(1,28,28)
        p=self.singlepredict(resized).argmax(0)
        return p;'''
    def findimg(self,img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        r=resized.reshape(1,28,28)
        p=self.singlepredict(resized).argmax(0)
        return p;



class ScreenClass:
    def __init__(self, x=0,y=0,w=0,h=0):
        self._data=None
        self.w=w
        self.h=h
        self.x=x;self.y=y
        self.sz=self.w*self.h
        if (self.sz==0):
            self.w=GetScreenX()
            self.h=GetScreenY()
            self.sz=self.w*self.h
        self._data=(ctypes.c_int8 * self.sz*4)()
    def changemode(self,d3dmode=0,backgroundmode=0):
        self.mode=d3dmode
        self.backgroundmode=backgroundmode
        cd.ChangeCaptureMode(self.mode,self.backgroundmode)
        return self.mode
    def changedims(self,x=0,y=0,w=0,h=0):
        if (x<0):x=0
        if (y<0):y=0
        if (x+w>ScreenX):w=ScreenX-x
        if (y+h>ScreenY):h=ScreenY-y
        self.w=w
        self.h=h
        self.x=x;self.y=y
        if (w*h!=self.sz):
            self.sz=w*h
            self._data=(ctypes.c_int8 * self.sz*4)()
    def savexywh(self,name,x,y,w,h):
        p = ctypes.create_unicode_buffer(name)
        h_ScreenCaptureToFile(p,x,y,w,h)
    def grab(self):
        cd.ScreenCapturetoArray(self._data,self.x,self.y,self.w,self.h)
        return bytearray(self._data)
    def grabxy(self,x,y):
        cd.ScreenCapturetoArray(self._data,x,y,self.w,self.h)
        return bytearray(self._data)
    def grabxywh(self,x,y,w,h):
        self.changedims(x,y,w,h)
        cd.ScreenCapturetoArray(self._data,self.x,self.y,self.w,self.h)
        return bytearray(self._data)
    def framexywh(self,x,y,w,h):
        self.changedims(x,y,w,h)
        cd.ScreenCapturetoArray(self._data,self.x,self.y,self.w,self.h)
        g=bytearray(self._data)
        frame = np.ctypeslib.as_array(g)
        frame=np.reshape(frame,(self.h,self.w,4))
        return frame
    def changecountstart(self):
        cd.ScreenChangeCount(self.x,self.y,self.w,self.h)
    def changecountstop(self):
        ret=cd.ScreenChangeCount(self.x,self.y,self.w,self.h)
        return ret

class ScreenGrabClass():
    
    def __init__(self):
        self.x=-100
        self.y=-1;self.on=0
        self.dx=0;self.ax=0
        self.dy=0;self.ay=0
        self.on=0
    def start(self):
        if (self.on==0):
            self.on=1
            self.x=GetMouseX();
            self.y=GetMouseY()
            self.ax=self.x;self.ay=self.y;
        self.dx=GetMouseX()-self.x
        self.dy=GetMouseY()-self.y
        if (self.dx<0): 
            self.ax=self.x+self.dx;self.dx*=-1
        if (self.dy<0): self.ay=self.y+self.dy;self.dy*=-1;
        
        DrawBox(self.ax,self.ay,self.dx,self.dy,0xFF00CC55,2)  
    def stop(self):
        if (self.on==0): return None
        data=[self.ax+2,self.ay+1,self.dx-2,self.dy-2]
        self.on=0
        return data
    def isrunning(self):
        return (self.on==1)
class ConsoleClass:
    instances = []
    def __init__(self,basew=400,baseh=400,fontsize=10,textcolor=0xFF00FF00,clickthru=1,trans=20,xclosesapp=0,background="console.bmp",title="none"):
        self.basew=basew
        self.baseh=baseh
        self.basex=GetScreenX()-self.basew
        self.basey=140
        #self.box=[self.basex,self.basey,663,663]
        self.basecolor=0x000000
        self.text=[]
        self.textcolors=[]
        self.drawtext=""
        self.intro=-1
        self.fontsize=fontsize
        self.fontnum=holoconfig["fontnum"];
        self.background=background
        holoconfig["fontnum"]-=1;
        ConsoleClass.instances.append(self)
        self.menuon=1
        self.movelocked=0
        self.movex=0
        self.movey=0
        self.mblocked=0;
        self.lastks=0
        self.consoleon=1
        self.drawsprite=None
        self.textsz=0
        self.adlocked=0
        self.clickthru=clickthru
        self.textcolor=textcolor
        self.trans=(int(((100-trans)*255)/100))%256
        self.drawtextsep="+"
        self.xclosesapp=xclosesapp
        self.lastr=0
        self.maxsz=int(self.baseh/(self.fontsize+4))
        self.scrollpos=self.maxsz+1
        self.scrolllock=1
        self.realmaxsz=0;
        self.fontname="Arial"
    def destroy(self):
        BlockMouseInput(1,0);
        ConsoleClass.instances.remove(self)
    def getmouseroll(self):
        r=GetMouseRoll()
        dr=r-self.lastr
        #dr=(dr/abs(dr))
        self.lastr=r
        if (dr!=0):
            dr=CLAMP(dr,-2,2)
            #print("mouseroll:"+str(dr)+":"+str(self.scrollpos))
            self.scrolllock=0
            self.scrollpos-=dr
            self.scrollpos=min(self.textsz+1,self.scrollpos)
            #self.scrollpos=max(self.scrollpos,self.realmaxsz)
        return dr
    '''def calcscroll(self):
        self.maxsz=int(self.baseh/(self.fontsize+4))
        if (self.scrollpos==self.textsz):
            #self.scrollpos=self.textsz-self.maxsz
            self.scrolllock=1
        self.scrollpos=max(self.scrollpos,self.maxsz)
        print(self.scrollpos)'''
    def calctextsize(self):
        sz=0
        self.textsz=0
        self.maxsz=int(self.baseh/(self.fontsize+4))
        i=0
        for sentence in self.text[-1:0:-1]:
            sz+=int(len(sentence)*self.fontsize/self.basew)+1
            self.textsz+=1
            m=int(len(sentence)*self.fontsize/self.basew)
            if ((self.fontsize+4)*i<self.baseh+30):i+=m+1;
            self.realmaxsz=i;
        #print("realmax"+str(self.realmaxsz)+"cur"+str(self.textsz))
    def clear(self):
        self.text=[]
    def printx(self,t,color=None,sep=None):
        #self.scrollpos=max(self.scrollpos,self.realmaxsz)
        
        if (self.scrollpos>=self.textsz):
            self.scrolllock=1
        t=print_to_string(t)
        sz=0
        if (sep!=None):
            s=t.split(sep)
            for a in s:
                self.text.append(a)
                if (color!=None):self.textcolors.append(color);
                else:self.textcolors.append(self.textcolor);
        else :
            self.text.append(t)
            if (color!=None):self.textcolors.append(color);
            else:self.textcolors.append(self.textcolor);
        
        self.calctextsize()
        if (self.scrolllock==1):
            if (self.textsz>=self.scrollpos):self.scrollpos=self.textsz+1;
    def out(self,*args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        self.printx(contents)
    def printf(self,*args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        self.printx(contents)
    def drawx(self,t):
        if (self.consoleon==1 and self.menuon==1):
            self.drawsprite=t
            ReloadSprite(t)
    def settextcolor(self,t):
        self.textcolor=t
    def setxclosesapp(self,t):
        self.xclosesapp=t
    def setclickthru(self,t):
        self.clickthru=t
    def settransparency(self,t):
        self.trans=(int(((100-t)*256)/100))%256
        #print(t)
    def bar(self,t,sep="+"):
        self.drawtext=t
        self.drawtextsep=sep
    def barx(self,t):
        self.drawtext=t
    def barf(self,*args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        self.barx(contents)
    def switchonoff(self,t):
        self.consoleon=t#(self.consoleon+1)%2
    def switchon(self):
        self.consoleon=1#(self.consoleon+1)%2
    def switchoff(self):
        self.consoleon=0#(self.consoleon+1)%2
    def Move(self,dx,dy):
        self.basex+=dx;self.basey+=dy;
        self.basex=max(self.basex,0);self.basey=max(self.basey,0);
    def MoveXY(self,x,y):
        dx=x-self.basex;dy=y-self.basey;
        self.Move(dx,dy)
    def draw(self):
        if (self.consoleon==0): return
        keystate=GetKeyState(1)
        keyclick=0
        keyfinishclick=0
        if (keystate==1 and self.lastks==0):
            keyclick=1
        if (keystate==0 and self.lastks==1):
            keyfinishclick=1
        self.lastks=keystate
        
        w=min(568-120,max(self.basew-90,0))
        DrawSprite("consolemenumin.bmp",self.basex,self.basey-30,0,0,w,30);
        w=min(568,self.basew-30)#max(self.basew-570,0)
        if (self.menuon==0): DrawSprite("consolemenumin.bmp",self.basex+self.basew-90,self.basey-30,600-90,0,90,30);
        else : DrawSprite("consolemenumax.bmp",self.basex+self.basew-90,self.basey-30,600-90,0,90,30);
        x=GetMouseX()
        y=GetMouseY()
        if (self.adlocked==1):
            if (keystate==0):
                self.adlocked=0
                self.basew=max(120,self.basew);self.baseh=max(0,self.baseh)
                self.calctextsize()
            else:
                dx=x-self.movex;dy=y-self.movey;
                self.basew+=dx;self.baseh+=dy;
                self.movex=x;self.movey=y
                self.movex=x
        if (self.movelocked==1):
            if (keystate==0):
                self.movelocked=0
            else:
                dx=x-self.movex;dy=y-self.movey;
                self.Move(dx,dy)
                self.movey=y
                self.movex=x
        if (x<self.basex+self.basew and x>self.basex and y<self.basey+self.baseh and y>self.basey-31):#all window
            dr=self.getmouseroll()
                
            if (self.trans>64 and self.clickthru==0):
                if (self.menuon==1):
                    BlockMouseInput(1,1);
                    self.mblocked=1;
                else :
                    BlockMouseInput(1,0);
                    self.mblocked=0;
            if (x<self.basex+self.basew and y>self.basey+self.baseh-30 and y<self.basey+self.baseh and x>self.basex+self.basew-30):#bottom left drag resize
                BlockMouseInput(1,1);
                self.mblocked=1;
                if (keystate!=0):
                    if (self.adlocked==0 and keyclick==1):
                        self.adlocked=1
                        self.movey=y
                        self.movex=x
            else:
                if (x<self.basex+self.basew and x>self.basex and y<self.basey and y>self.basey-31):#top bar
                    BlockMouseInput(1,1);
                    self.mblocked=1;
                    '''if (x<self.basex+30 or x> self.basex+self.basew-89):                   #middle of top bar is click thru
                        BlockMouseInput(1,1);
                        self.mblocked=1;
                    else :
                        BlockMouseInput(1,0);'''
                    if (x<self.basex+self.basew-29 and x> self.basex+self.basew-59):       #minimize/maximize of top bar
                        if (keyfinishclick==1):
                            if (self.menuon==1):
                                self.minbasex=self.basex;self.minbasey=self.basey;
                                self.MoveXY(GetScreenX()-self.basew-70,GetScreenY()-70)
                            if (self.menuon==0):
                                self.MoveXY(self.minbasex,self.minbasey)
                            self.menuon=(self.menuon+1)%2
                            return
                        #if (keystate!=0 and keyclick==1):
                            #self.menuon=(self.menuon+1)%2
                    if (x<self.basex+self.basew-59 and x> self.basex+self.basew-89):       #transparent of top bar
                        if (keystate!=0 and keyclick==1):
                            #if (keystate==0 and self.clicked==1):
                            self.trans=(self.trans-64)%256
                    if (x>self.basex+self.basew-29):                                        #close(x) of top bar
                        if (keystate!=0 and keyclick==1):
                            self.consoleon=0
                            if (self.xclosesapp==1):
                                print("ending")
                                KillPython()
                            BlockMouseInput(1,0);
                    if (x<self.basex+self.basew-89 and x>self.basex):                                  #move of top bar
                        if (keystate!=0):
                            if (self.movelocked==0 and keyclick==1):
                                self.movelocked=1
                                self.movey=y
                                self.movex=x
                else :
                    if (self.clickthru==1):
                        BlockMouseInput(1,0);
                        self.mblocked=0;
        else :
            if (self.mblocked==1):
                BlockMouseInput(1,0);
                self.mblocked=0;
          
        if (self.intro==-1):
            if (HoloGraphicsCallback==None): return
            CreateFont( self.fontname,self.fontsize,self.fontnum)
            self.intro=0
        if (self.intro==0 and self.menuon==1):
            DrawSolidColor(self.basex,self.basey,self.basew,self.baseh,self.basecolor +self.trans*16777216)
            DrawSprite("consolemenumin.bmp",self.basex+self.basew-30,self.basey+self.baseh-30,0,0,30,30)
            if (self.drawsprite!=None):
                DrawSpriteNaked(self.drawsprite,self.basex+100,self.basey+100)
            i=0;sz=0;ct=0
            end=min(self.textsz+1,self.scrollpos);#min(self.textsz+1,self.maxsz+self.scrollpos)
            for sentence in self.text[end:0:-1]:
                ct+=1
                m=int(len(sentence)*self.fontsize/self.basew)
                i+=m+1
                if ((self.fontsize+4)*i>self.baseh-60):break;
            start=max(end-ct-1,0)
            #print(start,end,self.scrollpos)+-`
            i=0
            #for sentence in self.text[-1-self.textsz-self.scrollpos:end:]:
            #print(start,end)
            b=start
            for sentence in self.text[start:end:]:
                m=int(len(sentence)*self.fontsize/self.basew)
                DrawStringBox(sentence,self.basex,self.basey+(self.fontsize+4)*i,self.basew,100,self.textcolors[b],self.fontnum)
                i+=m+1
                b+=1
                #if ((self.fontsize+4)*i>self.baseh):break;
            sep=self.drawtextsep
            if (sep!=None):
                s=self.drawtext.split(sep)
                i=len(s)
                for a in s:
                    DrawStringBox(a,self.basex+30,self.basey+self.baseh-(self.fontsize+4)*i,self.basew,100,self.textcolor,self.fontnum)
                    i-=1
            else :
                DrawStringBox(self.drawtext,self.basex+30,self.basey+self.baseh-(self.fontsize+4),self.basew,100,self.textcolor,self.fontnum)
class IntroSheet:
    def __init__(self,background="scrollbg.bmp",text="Intro Text separated by +",fontsize=30):
        self.text=text.split('+')
        self.intro=-1
        self.fontsize=fontsize
        self.fontnum=holoconfig["fontnum"];
        self.background=background
        self.fontname="Arial"
        holoconfig["fontnum"]-=1;
        
    def draw(self):
        if (self.intro==-1):
            if (HoloGraphicsCallback==None): return
            
            k=GetKeyState(VK["LeftButton"])
            CreateFont( self.fontname,self.fontsize,self.fontnum)
            self.introsprite=Sprite(self.background,200,200,663,378)
            self.intro=0
        if (self.intro==0):
            self.introsprite.draw()
            i=0
            for sentence in self.text:
                DrawStringBox(sentence,200,200+(self.fontsize+20)*i,700,300,0xFF000000,self.fontnum)
                i+=1
            
            DrawStringBox("[x]",450,500,600,300,0xFF000000,self.fontnum)
            k=GetKeyState(VK["LeftButton"])
            if (k!=0):self.intro=1
class Fps:
    def ms(self):
        return round(time.time() * 1000)
    def __init__(self,ct=0):
        self.ct=0
        self.tm=self.ms()
    def update(self):
        self.ct+=1
    def display(self):
        self.tm2=self.ms()-self.tm
        if (self.tm2>1000):
            self.tm=self.ms()
            fps=(self.ct*1000/(self.tm2))
            print("fps:",fps,":",GetKeyState(1))
            self.ct=0
    def updateanddisplay(self):
        self.update()
        self.display()



   


class Sprite:
    def __init__(self, filename, x,y,w,h,index=0,dx=0,dy=0,di=0):
        self.filename = filename
        self.dx = dx
        self.dy = dy
        self.di = di
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.index=index
    def outdata(self):
        print(self.x,self.y,self.w,self.h,self.index,self.filename);
    def draw(self):
        self.index+=self.di
        DrawSpriteIndex(self.filename,self.x,self.y,self.w,self.h,self.index);
class BounceSprite(Sprite):
    def updateanddraw(self):
        if (self.x>GetScreenX() or self.x<0): self.dx*=-1;
        if (self.y>GetScreenY() or self.y<0): self.dy*=-1;
        self.x+=self.dx
        self.y+=self.dy
        self.index+=self.di
        DrawSpriteIndex(self.filename,self.x,self.y,self.w,self.h,self.index);
    def changespeed(self,dx,dy,di):
        self.dx = dx*signedcmp(self.dx,0)
        self.dy = dy*signedcmp(self.dy,0)
        self.di = di
class TextSprite:
    def __init__(self,text,x,y,c,w=200,h=40,text2="",base="whitebackground.bmp"):
        self.text = text
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.color=c
        self.base=base
        self.text2=text2
    def move(self,dx,dy):
        self.x+=dx
        self.y+=dy
    def updateanddraw(self,status,mtype):
        if (self.text.find(".bmp")==-1):
            DrawSpriteIndexMouseOverL(self.base,self.x,self.y,self.w,self.h,0);
        else:
            DrawSpriteIndexMouseOver(self.text,self.x,self.y,self.w,self.h,0);
        if (mtype==4):
            if (self.text.find(".bmp")==-1):
                DrawString(self.text,self.x,self.y,self.color)
        if (mtype==0):
            DrawString(self.text,self.x,self.y,self.color)
            DrawSpriteIndexMouseOverL("menudropdown.bmp",self.x+180,self.y,20,40,0);
        if (mtype==1):
            DrawString(self.text,self.x+40,self.y+10,self.color)
            if (status==0):
                DrawSpriteIndexMouseOverL("checkboxempty.bmp",self.x,self.y,40,40,0);
            else:
                DrawSpriteIndexMouseOverL("checkboxfull.bmp",self.x,self.y,40,40,0);
        if (mtype==2):
            DrawString(self.text,self.x,self.y,self.color)
            DrawSpriteIndexMouseOverL("sliderback.bmp",self.x+100,self.y+20,100,20,0);
            DrawSpriteIndexMouseOverL("slidergrip.bmp",self.x+status+90,self.y+20,20,20,0);
            DrawString(self.text2,self.x+98,self.y,self.color)
        if (mtype==3):
            DrawString(self.text,self.x,self.y,self.color)
            DrawSpriteIndexMouseOverL("textbox.bmp",self.x+100,self.y+10,100,20,0);
            DrawString(str(status),self.x+100,self.y+10,self.color)
        if (mtype==5):
            if (status!=1):
                DrawSpriteIndexMouseOverL("button2.bmp",self.x+90,self.y,94,30,0);
            else:
                DrawSpriteNaked("button3.bmp",self.x+90,self.y)
            DrawString(self.text,self.x,self.y,self.color)
            DrawString(self.text2,self.x+98,self.y+8,self.color)
           
    def changetext(self,text):
        self.text = text
    def changetext2(self,text2):
        self.text2 = text2
    def changexy(self,text,x,y):
        self.x = x
        self.y = y
        
ClampVal = lambda value, minv, maxv: max(min(value, maxv), minv)
class BoxClass:
    #instances = []
    def __init__(self,x,y,w,h,color,num,label=""):
        self.x=x; self.y=y; self.w=w; self.h=h; self.color=color; self.num=num;self.label=label
        #BoxClass.instances.append(self)
    def draw(self):
        DrawBox(self.x,self.y,self.w,self.h,self.color,self.num)
        if (len(self.label)>0):
            DrawString(self.label,self.x+10,self.y-10,self.color)
class TimerClass:
    instances = []
    def __init__(self,timer,callback):
        self.timer=timer
        self.callback=callback
        self.clock=cd.clocktime()+500
        TimerClass.instances.append(self)
    def dotimer(self):
        if (cd.clocktime()-self.clock>self.timer):
            self.callback()
            self.clock=cd.clocktime()
class MenuClass:
    instances = []
    def __init__(self,timer,callback):
        self.d=dictio
        self.callback=callback
        MenuClass.instances.append(self)
    #Menu Format{id:["type","display text or image",parentid,status]}
    def __init__(self,dictio,callback,menubmp="defaultmenu.bmp",activatebutton=0x0,hardblockinput=0,basex=50,basey=120,width=200,height=40,splitstring="#"):
        self.menubmp=menubmp
        self.d=dictio
        self.callback=callback
        self.sl=[]
        self.rects=[]
        self.oldstatus=[]
        self.chain=[0]*10
        self.active=0
        self.activeparent=0
        self.activatebutton=activatebutton
        #BlockKeyInput(activatebutton,1)
        self.hardblockinput=hardblockinput
        self.h=[0]*100
        #self.h[0]=1
        self.splitstring=splitstring
        self.basex=basex
        self.basey=basey
        self.basew=200
        defaultw=width
        defaulth=height
        self.accepttext=-1
        self.menuon=1
        self.textbox=""
        self.blockinput=0
        self.mouseonmenu=0
        self.hardblockinput=0
        self.movelocked=0
        self.movex=0
        self.movey=0
        self.mblocked=0;
        self.clicked=0
        self.close=0
        self.lastks=0
        self.mouseonmenuck=0
        self.minbasex=10
        self.minbasey=GetScreenY()-100
        
        #x = threading.Thread(target=self.mousethread, args=[self,])
        #x.start()
        #hk=Hotkey()
        #hk.SetClickTrigger(key,self.retfunc,x,y,w,h)
        for key, value in self.d.items():
            if (value[2]==0):
                self.d[key].append(0)
            else:
                try:
                    par=value[2]
                    depth=self.d[par][4]+1
                    self.d[key].append(depth)
                except IndexError:
                    print("Menu Initializer fail, key %d has parent %d which doesnt exist yet" %(key,par))
                    raise
        i=0
        for key, value in self.d.items():
            parent=value[2]
            depth=value[4]
            status=value[3]
            h=self.h[parent]
            mtype=0
            text2=""
            if ("Check" in value[0]):
                mtype=1
            if ("Slider" in value[0]):
                mtype=2
            if ("Text" in value[0]):
                mtype=3
                status=str(value[3])
            if ("Display" in value[0]):
                mtype=4
            if ("Button" in value[0]):
                mtype=5
                text2="clickme"
            controltext=str(value[1]).split(self.splitstring)
            controltext.append(text2)
            #self.sl.append(TextSprite(str(i)+" "+str(depth)+" "+str(parent)+value[1],basex+depth*defaultw,h*defaulth+basey,0xFF000000,defaultw,defaulth))
            self.sl.append(TextSprite(controltext[0],basex+depth*defaultw,h*defaulth+basey,0xFF000000,defaultw,defaulth,controltext[1]))
            #RECTS(0x,1y,2x2,3y2,4parent,5depth,6key,7mtype,8status)
            self.rects.append([basex+depth*defaultw,h*defaulth+basey,basex+defaultw+depth*defaultw,h*defaulth+basey+defaulth,parent,depth,i,mtype,status])
            self.oldstatus.append(status)
            #hk.SetClickTrigger(1,self.retfunc,basex,self.h*defaulth+basey,defaultw,defaulth,{'key':key})
            self.h[parent]+=1
            if (i!=0):
                self.h[i]=h
            i+=1
        MenuClass.instances.append(self)
    def Move(self,dx,dy):
        self.basex+=dx;self.basey+=dy;
        for t in self.sl:
            t.move(dx,dy)
        for t in self.rects:
            t[0]+=dx;t[2]+=dx;
            t[1]+=dy;t[3]+=dy
    def MoveXY(self,x,y):
        dx=x-self.basex;dy=y-self.basey;
        self.Move(dx,dy)
    def draw(self):
        
        keystate=GetKeyState(1)
        keyclick=0;keyfinishclick=0
        if (keystate==1 and self.lastks==0):
            keyclick=1
        if (keystate==0 and self.lastks==1):
            keyfinishclick=1
        self.lastks=keystate
        if (self.menuon==0):
            DrawSpriteNaked("defaultmenumin.bmp",self.basex,self.basey-30);
        else : DrawSpriteIndexMouseOverL("defaultmenumax.bmp",self.basex,self.basey-30,200,30,0);
        x=GetMouseX()
        y=GetMouseY()
        self.mouseonmenu=0
        if (self.movelocked==1):
            if (keystate==0):
                self.movelocked=0
            else:
                dx=x-self.movex;dy=y-self.movey;
                self.movey=y
                self.movex=x
                self.Move(dx,dy)
        if (x<self.basex+self.basew and x>self.basex and y<self.basey and y>self.basey-31):
            BlockMouseInput(1,1);
            self.mblocked=1;
            if (x<self.basex+self.basew-29 and x> self.basex+self.basew-59):
                if (keyfinishclick==1):
                    if (self.menuon==1):
                        self.minbasex=self.basex;self.minbasey=self.basey;
                        self.MoveXY(10,GetScreenY()-70)
                    if (self.menuon==0):
                        self.MoveXY(self.minbasex,self.minbasey)
                    self.menuon=(self.menuon+1)%2
                    return
                    #self.movelocked=1
            if (x>self.basex+self.basew-29):
                if (keyfinishclick==1):
                    self.close=1
                    KillPython()
                    #cd.BotExit()
                    #sys.exit();
            if (x<self.basex+self.basew-59):
                if (keystate!=0):
                    if (self.movelocked==0 and keyclick==1):
                        self.movelocked=1
                        self.movey=y
                        self.movex=x
        else :
            if (self.mblocked==1):
                BlockMouseInput(1,0);
                self.mblocked=0;            
        '''if (x<self.basex+200 and x>self.basex and y<self.basey and y>self.basey-31):
            BlockMouseInput(1,1);
            self.mblocked=1;
            if (x<self.basex+171 and x> self.basex+141):
                if (keystate!=0 and keyclick==1):
                    #if (keystate==0 and self.clicked==1):
                    self.menuon=(self.menuon+1)%2
            if (x<self.basex+141):
                if (keystate!=0):
                    if (self.movelocked==0 and keyclick==1):
                        self.movelocked=1
                        self.movey=y
                        self.movex=x
            if (x>self.basex+171):
                if (keystate!=0):
                    sys.exit();
        else :
            if (self.mblocked==1):
                BlockMouseInput(1,0);
                self.mblocked=0;'''
        while(1):
            k=GetMenuKey()
            
            if (k==0): break
            if (k==self.activatebutton):   #Ctrl Shift scancode
                self.menuon=(self.menuon+1)%2
                Sleep(20)
                if (self.hardblockinput==1):
                    BlockMenuInput(self.menuon)
                self.accepttext=-1
            if (self.accepttext!=-1 and self.menuon==1):
                tx=self.rects[self.accepttext][8]
                if (k==VK["Back"]):
                    tx=tx[:-1]
                elif (k==VK["Delete"]):
                    tx=""
                else:
                    if (k==187):tx+='=';
                    if (k==189):tx+='-';
                    if (k==190):tx+='.';
                    if (k==188):tx+=",";
                    if (k==0x2E):tx="";
                    if (k==0x09):tx+="   ";
                    if (k==0x2E):tx="";
                    if (k==0x2E):tx="";
                    if (k>=0x30 and k<=0x5A):
                        shiftstate=GetKeyState(16)#Shift
                        if (shiftstate==0):
                            tx=tx+chr(k).lower()
                        else:tx=tx+chr(k)
                #print(self.textbox)
                self.rects[self.accepttext][8]=tx
                if (self.callback!=0):
                    self.callback(self.rects[self.accepttext][6],tx)
        if (self.menuon==0):
            BlockMenuInput(0)
            self.blockinput=0
            return
       
       
        self.mouseonmenu=0
        
        if (keyclick!=0 and self.accepttext!=-1):self.accepttext=-1            
        for index in range(len(self.rects)):
            g=self.rects[index]
            par=g[4]
            depth=g[5]
            key=g[6]
            mtype=g[7]
            status=g[8]
            #g=self.rects[i]
            
            if (x<g[2] and x>g[0] and y<g[3] and y>g[1] and (g[4] in self.chain)):
                #if (mtype==5 and keystate==0 and status==1):status=2
                if (keystate!=0):
                    if (mtype==5):
                        status=1
                        g[8]=status
                        self.rects[index]=g
                        self.oldstatus[index]=1
                    if (mtype==2):
                        status=x-(g[0]+100)
                        status=ClampVal(status,0,100)
                        if (g[8]!=status):
                            g[8]=status
                            self.rects[index]=g
                            ar={"args":status}
                            self.callback(key,status)
                if (keyfinishclick!=0):
                    self.accepttext=-1
                    if (mtype==5):
                        status=2
                        if (g[8]!=status):
                            g[8]=status
                            self.rects[index]=g
                        self.callback(key,status)
                        
                    if (mtype==1):
                        status=(status+1)%2
                        if (g[8]!=status):
                            g[8]=status
                            self.rects[index]=g
                            ar={"args":status}
                            self.callback(key,status)
                    if (mtype==3):
                        self.accepttext=index
                        
                    #margs={'index':self.active}
                    #x = threading.Thread(target=f.func, kwargs=margs)
                    #x.start()
                self.mouseonmenuck=clock()
                self.mouseonmenu=1
                self.active=index
                self.chain[depth]=index
                self.chain[depth+1:]=[0]*(len(self.chain)-(depth+1))
                #self.chain[depth+2]=0
                #self.chain[(g[5])
            if (par in self.chain):
                self.sl[index].updateanddraw(status,mtype)
        if (clock()-self.mouseonmenuck>2000):
            self.active=0
            self.chain[depth]=0
            self.chain[1:]=[0]*(len(self.chain)-(1))
        if (self.hardblockinput==0):
            if (self.mouseonmenu==1 and self.menuon==1):
                BlockMenuInput(1)
                self.blockinput=1
            else:
                if (self.blockinput==1):
                    BlockMenuInput(0)
                    self.blockinput=0
    def destroy(self):
        BlockMenuInput(0)
        MenuClass.instances.remove(self)
    def changestatus(self,key,status):
        #key=key-1
        c=self.rects[key]
        c[8]=status
        self.rects[key]=c
        return status
    def changetext(self,id,text):
        self.sl[id].changetext(text)
    def changetext2(self,id,text2):
        self.sl[id].changetext2(text2)
    def getstatus(self,key):
        #key=key-1
        return self.rects[key][8]
    def isstatuschanged(self,key):
        #key=key-1
        res=0
        if (self.rects[key][8]!=self.oldstatus[key]):
            res=1
        self.oldstatus[key]=self.rects[key][8]
        return res
    def retfunc(self,key):
        x=GetMouseX()
        y=GetMouseY()
        print("key",key,x,y)
        self.callback(key)
        return



def SetKillKey(a,b):
    cd.SetKillKey(a,b)
def DoThread(name,args=None):
    x = threading.Thread(target=name, args=[])
    x.daemon = True
    x.start()     
def HoloGraphicsCallbackThread():
    try:
        while(1):
           
            ret=cd.initoverlay()
            if (ret==1):
                #if (HoloConsoleFunc is not None): return;
                #r=HoloGraphicsCallback()
                for a in TimerClass.instances:
                    a.dotimer()
                for a in ConsoleClass.instances:
                    a.draw()
                for a in MenuClass.instances:
                    a.draw()
                r=HoloGraphicsCallback()
                #if (r==0): break
                cd.presentoverlay()
                cd.sleep(1);
            #Sleep(20)
    except:
        print("exception graphics thread")
        for a in ConsoleClass.instances:
            a.destroy()
        for a in MenuClass.instances:
            a.destroy()
        raise
        
def ScriptLinkLoopFunc():
    if (GetKeyState(VK["Escape"])!=0):
        KillPython()
        pass
def SLMainLoop(func=ScriptLinkLoopFunc):
    while(1):
        func()
        Sleep(10)
        cv2.waitKey(1);
        #if cv2.waitKey(1) & 0xFF == chr(27):break;
def StartGraphics(func,name="overlay"):
    global HoloGraphicsCallback
    
    if (HoloGraphicsCallback is not None): return;
    HoloGraphicsCallback=func
    p = ctypes.create_unicode_buffer(name)
    cd.SpawnWindowW(p)
    x = threading.Thread(target=HoloGraphicsCallbackThread, args=[])
    x.daemon = True
    x.start()
















