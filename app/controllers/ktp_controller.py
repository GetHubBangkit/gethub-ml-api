import re
import cv2
from matplotlib import pyplot as plt
from pytesseract import image_to_string

class KTPInformation:
    def __init__(self):
        self.nik = ""
        self.nama = ""
        self.content = ""

    def to_dict(self):
        """Converts object attributes to a dictionary."""
        return self.__dict__

class KTPOCR:
    def __init__(self, image_path, is_image):
        self.image = cv2.imread(image_path)
        self.process(is_image)

    def process(self, is_image):
        """Performs OCR on the preprocessed image."""
        # self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # self.th, self.threshed = cv2.threshold(self.gray, 127, 255, cv2.THRESH_TRUNC)

        if is_image == False:
            self.th, self.threshed = cv2.threshold(self.image, 100, 400, cv2.THRESH_TRUNC)
            imageFinal = self.threshed
        else:
            imageFinal = self.image

        # fig, ax = plt.subplots(figsize=(10, 5))
        # ax.imshow(imageFinal, cmap='gray')
        # ax.set_title('Thresholded Image')
        # ax.axis('off')
        # plt.show()

        self.result = KTPInformation()
        raw_extracted_text = image_to_string(imageFinal)
        # print(raw_extracted_text)
        self.extract(raw_extracted_text)

    def word_to_number_converter(self, word):
        """Converts specific characters in a word to numbers."""
        word_dict = {"L": "1", "O": "0", "?": "7", "A": "4", "Z": "2", "S": "5", "b": "6", "B": "8", "G": "6"}
        return "".join(word_dict.get(letter, letter) for letter in word)

    def extract(self, extracted_result):
        """Extracts information from the OCR result."""
        self.result.content = extracted_result
        next_line = None  # Inisialisasi variabel untuk line berikutnya
        for index, line in enumerate(extracted_result.split("\n")):
            line = self.remove_punctuation(line)

            if "NIK" in line:
                final_nik = self.word_to_number_converter(line.split(':')[-1].strip())
                final_nik = final_nik.replace(" ", "").strip()
                final_nik = final_nik.replace("NIK", "").strip()
                final_nik = final_nik.replace("=", "").strip()
                self.result.nik = final_nik
                # Ambil line berikutnya jika tersedia
                if index + 1 < len(extracted_result.split("\n")):
                    next_line = self.remove_punctuation(extracted_result.split("\n")[index + 1])
                    final_name = re.sub(r'[‘\d]', '', next_line.split(':')[-1].replace('Nama ', '').strip())
                    final_name = final_name.replace("» ", "")
                    final_name = re.sub(r'[^\w\s]', '', final_name)
                    final_name = final_name.replace("Nama", "")
                    final_name = final_name.strip()
                    self.result.nama = final_name

            elif "Nama" in line:
                final_name = re.sub(r'[‘\d]', '', line.split(':')[-1].replace('Nama ', '').strip())
                final_name = final_name.replace("» ", "")
                final_name = re.sub(r'[^\w\s]', '', final_name)
                final_name = final_name.replace("Nama", "")
                final_name = final_name.strip()
                if self.result.nama == "":
                    self.result.nama = final_name

        # Gunakan next_line sesuai kebutuhan
        if next_line:
            print("Data berikutnya setelah NIK:", next_line)

    @staticmethod
    def remove_punctuation(text):
        """Removes punctuation from text."""
        punctuations = '''!()[]{}'"\<>?@#$%^&*_~'''
        return ''.join(char for char in text if char not in punctuations)

    def to_dict(self):
        """Converts the result object to a dictionary."""
        return self.result.to_dict()

def scan(image_path):
    """Scans an Indonesian ID card (KTP) and extracts information."""
    ktp_ocr = KTPOCR(image_path, False)
    if ktp_ocr.to_dict()["nama"] == "":
        ktp_ocr = KTPOCR(image_path, True)

    return {
        "error_code": 0,
        "result": ktp_ocr.to_dict(),
        "message": "Successfully OCR KTP",
    }
