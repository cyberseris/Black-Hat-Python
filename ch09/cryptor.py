import base64 
import zlib

from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

def generate():
    #生成金鑰對
    new_key = RSA.generate(2048)
    private_key = new_key.exportKey()   # 私鑰
    public_key = new_key.publickey().exportKey()    # 公鑰

    with open('./rsa_key/key.pri', 'wb') as f:
        f.write(private_key)
    
    with open('./rsa_key/key.pub', 'wb') as f:
        f.write(public_key)

def get_rsa_cipher(keytype):
    # keytype: pub or pri
    with open(f'./rsa_key/key.{keytype}') as f:
        key = f.read()
    rsakey = RSA.importKey(key)
    return PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes()

def encrypt(plaintext):
    # 將明文資料以 bytes 類型傳入並壓縮
    compressed_text = zlib.compress(plaintext)
    # 隨機生成會話密鑰
    session_key = get_random_bytes(16)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    # 使用該密碼對壓縮過的明文加密
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)
    cipher_rsa, _ = get_rsa_cipher('pub')
    # 使用 RSA 公鑰對會鑰密鑰進行加密
    encrypted_session_key = cipher_rsa.encrypt(session_key)
    # 將所有的訊息都打包到一個 payload 中
    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    # 對 payload 進行 base64 編碼
    encrypted = base64.encodebytes(msg_payload)
    return encrypted

def decrypt(encrypted):
    # 將 base64 字符串解碼為 bytes 數據
    encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
    cipher_rsa, keysize_in_bytes = get_rsa_cipher('pri')

    # encrypted_bytes: encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)
    nonce = encrypted_bytes.read(16)
    tag = encrypted_bytes.read(16)
    ciphertext = encrypted_bytes.read()

    # 使用 RSA 私鑰解密會話密鑰
    session_key = cipher_rsa.decrypt(encrypted_session_key)
    # 使用密鑰執行 AES 算法，解碼數據正文
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

    # 解壓為訊息明文
    plaintext = zlib.decompress(decrypted)
    return plaintext

if __name__ == '__main__':
    plaintext = b'hey there you.'
    print(decrypt(encrypt(plaintext)))


'''
OAEP滿足以下兩個目標：

1. 添加隨機性元素，這可用於將確定性加密方案（如傳統 RSA）轉變為概率加密方案。
2. 通過確保無法反轉陷門單向置換f，從而無法恢復明文的任何部分，來防止密文的部分解密（或造成其他信息洩漏）

參考來源
PKCS1_OAEP: https://zh.wikipedia.org/zh-tw/%E6%9C%80%E4%BC%98%E9%9D%9E%E5%AF%B9%E7%A7%B0%E5%8A%A0%E5%AF%86%E5%A1%AB%E5%85%85

'''

'''
1. use a cryptographic authentication tag
2. The tag is generated during encryption and is verified during decryption
3. If the tag doesn't match, it indicates that the data may have been tampered with
'''