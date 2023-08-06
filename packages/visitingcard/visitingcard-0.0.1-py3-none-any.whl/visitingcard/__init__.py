import cv2
import pytesseract
import re

# pytesseract.pytesseract.tesseract_cmd = 'E:/tes/tesseract.exe'


# Name extraction code (Name must be in left side)
def get_full_name(lst):
    name1 = r"([a-zA-Z'.,-]+( [a-zA-Z'.,-]+)*){8,30}"
    full_name1 = re.search(name1, lst)

    if full_name1 is not None:
        return full_name1.group()


# Email Id extraction code
def get_email(lst):
    mail_pattern = r'\b[A-Za-z0-9. _%+-]+@[A-Za-z0-9. -]+\.[A-Z|a-z ]{2,3}'

    mail = re.search(mail_pattern, lst.replace(" ", "").replace("-", "."))
    if mail is not None:
        return mail.group()


# contact number extraction code
def get_phone_number(lst):
    contact_no4 = r'[0-9.]{13}\b'
    contact_no1 = r'[0-9]{10}\b'
    contact_no3 = r'[0-9.]{12}\b'
    contact_no2 = r'[0-9.]{11}\b'
    Contact_NO1 = re.search(contact_no1,
                            lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                            "").replace(
                                "*", ""))
    if Contact_NO1 is not None:
        print('10')
        return Contact_NO1.group()
    Contact_NO2 = re.search(contact_no2,
                            lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                            "").replace(
                                "*", ""))
    if Contact_NO2 is not None:
        print('11')
        return Contact_NO2.group()
    Contact_NO3 = re.search(contact_no3,
                            lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                            "").replace(
                                "*", ""))
    if Contact_NO3 is not None:
        print('12')
        return Contact_NO3.group()
    Contact_NO4 = re.search(contact_no4,
                            lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                            "").replace(
                                "*", ""))
    if Contact_NO4 is not None:
        print('13')
        return Contact_NO4.group()


# website extraction code
def get_website(lst):
    website_pattern = r'\b(WWW|www)+.[A-Za-z0-9. _%+-]+\.[A-Z|a-z]{2,3}\b'
    web = re.search(website_pattern, lst.replace(" ", ""))
    if web is not None:
        return web.group()


# Accept the file for for data extraction
from kraken import binarization
from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol


def extract(File_path):
    im = Image.open(File_path)
    bw_im = binarization.nlbin(im)
    d = decode(bw_im, symbols=[ZBarSymbol.QRCODE])
    if d:
        for i in d:
            print("QR code Exicuted")
            OCR_Text = i.data.decode('utf-8')

            OCR_Text = OCR_Text.replace(";", " ")
            # print(OCR_Text)
    else:
        path = File_path
        image = cv2.imread(path, 0)
        OCR = pytesseract.image_to_string(image)
        # print(len(OCR))
        # print(OCR)
        OCR_Text = OCR
    Name = ""
    Telephone = ""
    Email = ""
    Website = ""
    result = {}
    # ===========
    Final_text = {"Name": get_full_name(OCR_Text),
                  "Telephone": get_phone_number(OCR_Text),
                  "Email": get_email(OCR_Text),
                  "Website": get_website(OCR_Text)}
    # print(Final_text)
    result["Name"] = Final_text["Name"]
    result["Telephone"] = Final_text["Telephone"]
    result["Email"] = Final_text["Email"]
    result["Website"] = Final_text["Website"]
    print(result)
    return result

# data = extract("kandarpaBaghar.jpg")
# print(data)