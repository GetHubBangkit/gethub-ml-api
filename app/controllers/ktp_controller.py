import json
import re
import cv2
from pytesseract import pytesseract

class KTPInformation:
    def __init__(self):
        self.nik = ""
        self.nama = ""
        self.tempat_lahir = ""
        self.tanggal_lahir = ""
        self.jenis_kelamin = ""
        self.golongan_darah = ""
        self.alamat = ""
        self.rt = ""
        self.rw = ""
        self.kelurahan_atau_desa = ""
        self.kecamatan = ""
        self.agama = ""
        self.status_perkawinan = ""
        self.pekerjaan = ""
        self.kewarganegaraan = ""
        self.berlaku_hingga = "SEUMUR HIDUP"

    def to_dict(self):
        return self.__dict__

class KTPOCR:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.th, self.threshed = cv2.threshold(self.gray, 127, 255, cv2.THRESH_TRUNC)
        self.result = KTPInformation()
        self.master_process()

    def process(self):
        raw_extracted_text = pytesseract.image_to_string(self.threshed, lang="ind")
        return raw_extracted_text

    def word_to_number_converter(self, word):
        word_dict = {
            "L": "1",
            "l": "1",
            "O": "0",
            "o": "0",
            "?": "7",
            "A": "4",
            "Z": "2",
            "z": "2",
            "S": "5",
            "s": "5",
            "b": "6",
            "B": "8",
            "G": "6"
        }
        return "".join(word_dict.get(letter, letter) for letter in word)

    def extract(self, extracted_result):
        for word in extracted_result.split("\n"):
            word = self.pun_rem(word)

            if "NIK" in word:
                self.result.nik = self.word_to_number_converter(word.split(':')[-1].strip())
                continue

            if "Nama" in word:
                result = word.split(':')[-1].strip()
                result = result.replace('Nama ', '')
                result = re.sub(r'\d+', '', result).strip()
                self.result.nama =result
                continue

            if "Lahir" in word:
                word_parts = word.split(':')
                date_match = re.search(r"(\d{2}-\d{2}-\d{4})", word_parts[-1])
                if date_match:
                    self.result.tanggal_lahir = date_match.group(0)
                    self.result.tempat_lahir = word_parts[-1].replace(self.result.tanggal_lahir, '').strip()
                continue

            if "Gol" in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    gender_match = re.search(r"(LAKI-LAKI|LAKI|PEREMPUAN|LELAKI|PEREMPUAN)", word_parts[1])
                    if gender_match:
                        self.result.jenis_kelamin = gender_match.group(0)
                continue

            if "Alamat" in word:
                self.result.alamat = re.sub(r'^\W*\w+\W*', '', word)
                continue

            if "RW" in word:
                word = re.sub(r'^\W*\w+\W*', '', word)
                if " " in word:
                    a = word.split(" ")
                elif "/" in word:
                    a = word.split("/")
                else:
                    a = [word[:3], word[3:]]

                self.result.rt = a[0][-3:]
                self.result.rw = a[1][-3:]
                continue

            if "kel" in word:
                self.result.kecamatan = re.sub(r'^\W*\w+\W*', '', word)
                continue

            if "Agama" in word:
                match = re.search(r"(ISLAM|KRISTEN|KATOLIK|HINDU|BUDDHA|KONG HU CU)", word)
                if match:
                    self.result.agama = match.group(0)
                    break

            if "Status" in word:
                match = re.search(r"(KAWIN|BELUM KAWIN|DUDA CERAI|DUDA MATI|JANDA CERAI|JANDA MATI)", word)
                if match:
                    self.result.status_perkawinan = match.group(0)
                    break

            if "Pekerjaan" in word:
                self.result.pekerjaan = re.sub(r'^\W*\w+\W*', '', word).split(" ")[0]
                continue

            if "Kewarganegaraan" in word:
                match = re.search(r"(WNI|WNA)", word)
                if match:
                    self.result.kewarganegaraan = match.group(0)
                    break

    def pun_rem(self, text):
        punctuations = '''!()[]{}'"\<>?@#$%^&*_~'''
        return ''.join(char for char in text if char not in punctuations)

    def master_process(self):
        raw_text = self.process()
        self.extract(raw_text)

    def to_dict(self):
        return self.result.to_dict()

def scan(image_path):
    ktp_ocr = KTPOCR(image_path)
    return {
        "error_code": 0,
        "result": ktp_ocr.to_dict(),
        "message": "Successfully OCR KTP",
    }
