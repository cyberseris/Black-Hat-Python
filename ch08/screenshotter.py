import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot(name='screenshot'):
    # 獲取整個桌面的 handle
    hdesktop = win32gui.GetDesktopWindow()
    # 使用 get_dimensions 函數獲取桌面的寬度、高度、左上角 x 座標和 y 座標。
    width, height, left, top = get_dimensions()
    # 獲取桌面的裝置內容
    desktop_dc = win32gui.GetWindowDC(hdesktop)

    # 最大的差別，img_dc 是與整個桌面相關聯的裝置內容(Device Context, DC)，而 mem_dc 是
    # 為了執行複製而創建的相容 DC
    # 從桌面的裝置內容創建一個裝置內容對象，代表整個桌面的裝置內容。
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    # 從桌面裝置內容創建一個相容的裝置內容對象，為了在 img_dc 其中執行複製操作而創建的相容 DC，
    # 確保了在進行畫面擷取和後續的操作，不會對原始桌面 DC 產生直接影響
    mem_dc = img_dc.CreateCompatibleDC()
    # 創建一個點陣圖對象
    screenshot = win32ui.CreateBitmap()
    # 為點陣圖對象分配相容的點陣圖
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    # 將點陣圖對象選入相容的裝置內容
    mem_dc.SelectObject(screenshot)
    # 將桌面的一部分複製到相容的裝置內容
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    # 將相容的點陣圖保存為 BMP 檔案
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')
    # 釋放相容的裝置內容對象
    mem_dc.DeleteDC()
    # 釋放點陣圖對象
    win32gui.DeleteObject(screenshot.GetHandle())

def run():
    screenshot()
    with open('screenshot.bmp') as f:
        img = f.read()
    return img

if __name__ == '__main__':
    screenshot()

'''
# 為點陣圖對象分配相容的點陣圖
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    # 將點陣圖對象選入相容的裝置內容
    mem_dc.SelectObject(screenshot)

詳細說明：
在 mem_dc 中創建了一個相容位圖，這個位圖的大小與 width 和 height 相同，表示截取桌面的指定區域。這個區域是由 left 和 top 指定的起點，並且寬度和高度分別為 width 和 height。

然後，mem_dc.SelectObject(screenshot) 這一行程式碼是將這個相容位圖選入到 mem_dc 中，這樣任何後續的繪圖操作都會在這個位圖上進行。在這個特定的情境下，mem_dc 的相容位圖就成為了截取桌面區域的畫布，可以在上面進行後續的操作，例如保存成檔案。
'''