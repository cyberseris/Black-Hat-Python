import smtplib
import time
import win32com.client

# 指定 smtp 伺服器地址、連接的 port、用戶和密碼

smtp_server = "smtp.example.com"
smtp_port = 587
smtp_acct = "seris@test.com"
smtp_password = "seKret"
tgt_accts = ["seris@test2.com"]

def plain_email(subject, contents):
    # 生成一條訊息
    message = f"Subject: {subject}\nFrom: {smtp_acct}\n"
    message += f"To: {tgt_accts}\n\n{contents.decode()}"
    server =smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    # 連接伺服器，登錄郵箱
    server.login(smtp_acct, smtp_password)

    # 傳入帳號、收件地址和郵件訊息    
    server.sendmail(smtp_acct, tgt_accts, message)
    time.sleep(1)
    server.quit()

def outlook(subject, contents):
    # 創建一個 Outlook 應用實例
    outlook = win32com.client.Dispatch("Outlook.Application")
    message = outlook.CreateItem(0)

    # 發送郵件後立即刪除
    message.DeleteAfterSubmit = True
    message.Subject = subject
    message.Body = contents.decode()
    message.To = tgt_accts[0]
    # 發送郵件
    message.Send()

if __name__ == '__main__':
    plain_email('Attention', b'wake up')
    # outlook('Attention', 'wake up')