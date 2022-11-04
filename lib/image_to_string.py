import os
from PIL import Image
import pyocr

def test():
    #環境変数「PATH」にTesseract-OCRのパスを設定。
    #Windowsの環境変数に設定している場合は不要。
    path='C:\\Program Files\\Tesseract-OCR\\'
    os.environ['PATH'] = os.environ['PATH'] + path

    #pyocrにTesseractを指定する。
    pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    tools = pyocr.get_available_tools()
    tool = tools[0]

    #文字を抽出したい画像のパスを選ぶ
    img = Image.open('Image/test.png')

    #画像の文字を抽出
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    text = tool.image_to_string(img, lang="jpn", builder=builder)

    print(text)