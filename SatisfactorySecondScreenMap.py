import win32process
import win32con
import win32api
import ctypes
import win32gui

import os
import sys

from selenium import webdriver
import time

def get_module_base_address(pid, module_name):
    from ctypes import windll, byref, Structure, c_ulonglong, c_uint, c_void_p, c_size_t
    from ctypes.wintypes import DWORD, HMODULE, MAX_PATH
    
    class MODULEENTRY32(Structure):
        _fields_ = [('dwSize', DWORD),
                    ('th32ModuleID', DWORD),
                    ('th32ProcessID', DWORD),
                    ('GlblcntUsage', DWORD),
                    ('ProccntUsage', DWORD),
                    ('modBaseAddr', c_void_p),
                    ('modBaseSize', DWORD),
                    ('hModule', HMODULE),
                    ('szModule', ctypes.c_char * (MAX_PATH + 1)),
                    ('szExePath', ctypes.c_char * (MAX_PATH + 1))]
    
    hSnapshot = windll.kernel32.CreateToolhelp32Snapshot(0x00000008, pid)  # TH32CS_SNAPMODULE
    if hSnapshot == -1:
        return 0
    
    me32 = MODULEENTRY32()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32)
    
    if windll.kernel32.Module32First(hSnapshot, byref(me32)):
        while True:
            if module_name.lower() in me32.szModule.decode('utf-8').lower():
                windll.kernel32.CloseHandle(hSnapshot)
                return me32.modBaseAddr
            
            if not windll.kernel32.Module32Next(hSnapshot, byref(me32)):
                break
    
    windll.kernel32.CloseHandle(hSnapshot)
    return 0

PROCESS_ALL_ACCESS=(0x000F0000|0x00100000|0xFFF)
window=win32gui.FindWindow(None,"Satisfactory  ")
if window==0:
    print("游戏没有运行，先打开游戏载入存档")
else:
    hid,pid=win32process.GetWindowThreadProcessId(window)
    phand=win32api.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
    mydll = ctypes.windll.LoadLibrary("C:\\Windows\\System32\\kernel32.dll")
    #module_handles = win32process.EnumProcessModules(phand)
    #module_handle = module_handles[0]
    x_base_address = get_module_base_address(pid, "FactoryGameSteam-SignificanceManager-Win64-Shipping.dll")
    r_base_address = get_module_base_address(pid, "FactoryGameSteam-Engine-Win64-Shipping.dll")
    x_addr=x_base_address+0x000181C0
    r_addr=r_base_address+0x01F0A400
    data = ctypes.c_longlong(0)
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(x_addr),ctypes.byref(data),8,None)
    x_addr=data.value+0x8
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(x_addr),ctypes.byref(data),8,None)
    x_addr=data.value+0x170
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(x_addr),ctypes.byref(data),8,None)
    x_addr=data.value
    y_addr=x_addr+4
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(r_addr),ctypes.byref(data),8,None)
    r_addr=data.value+0x30
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(r_addr),ctypes.byref(data),8,None)
    r_addr=data.value+0xAE0
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(r_addr),ctypes.byref(data),8,None)
    r_addr=data.value+0x280
    data = ctypes.c_float(0)
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(x_addr),ctypes.byref(data),4,None)
    x=data.value
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(y_addr),ctypes.byref(data),4,None)
    y=data.value
    mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(r_addr),ctypes.byref(data),8,None)
    r=data.value
    options = webdriver.EdgeOptions();
    options.add_argument("--disable-web-security");
    driver = webdriver.Edge(options)
    driver.get("file:///"+os.path.dirname(sys.argv[0])+"/map.html")
    while(driver.current_url.find('#') <= 0):
        time.sleep(1)
    driver.execute_script("initPlayerMarker()")
    last_r = 0
    push_r = 0
    last_push_r = 0
    while(True):
        time.sleep(0.2)
        data = ctypes.c_float(0)
        mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(x_addr),ctypes.byref(data),4,None)
        x=data.value
        mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(y_addr),ctypes.byref(data),4,None)
        y=data.value
        mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(r_addr),ctypes.byref(data),4,None)
        r=int(data.value)
        dr=r-last_r
        if(dr<=-180):
            dr=dr+360
        if(dr>=180):
            dr=dr-360
        last_r=r
        push_r=r+450
        if(dr>0 ):
            while(push_r < last_push_r):
                push_r=push_r+360
        elif(dr<0):
            while(push_r > last_push_r):
                push_r=push_r-360
        last_push_r=push_r
        old_url=driver.current_url
        newurl = old_url[0:old_url.find(';')+1] + str(int(x))+';' + str(int(y)) + old_url[old_url.find('|'):]
        driver.get(newurl)
        driver.execute_script("window.updatePlayerDirection("+str(push_r)+")")