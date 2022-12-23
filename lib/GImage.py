from PIL import Image, ImageFont, ImageDraw
from typing import TypeVar, Union


class Colors:
    RED = (0xff, 0x00, 0x00, 0xff)
    GREEN = (0x00, 0xff, 0x00, 0xff)
    BLUE = (0x00, 0x00, 0xff, 0x7f)
    YELLOW = (0xff, 0xff, 0x00, 0xff)
    CYAN = (0xff, 0x00, 0xff, 0xff)
    MAGENTA = (0x00, 0xff, 0xff, 0xff)
    WHITE = (0xff, 0xff, 0xff, 0xff)
    CLEAR = (0xff, 0xff, 0xff, 0x00)
    CLEAR_RED = (0xff, 0x00, 0x00, 0x7f)


print(0x7f, 127)


class Anchors:
    RIGHT_ASCENDER = "ra"
    RIGHT_TOP = "rt"
    RIGHT_MIDDLE = "rm"
    RIGHT_BASELINE = "rs"
    RIGHT_BOTTOM = "rm"
    RIGHT_DESCENDER = "rd"
    LEFT_ASCENDER = "la"
    LEFT_TOP = "lt"
    LEFT_MIDDLE = "lm"
    LEFT_BASELINE = "ls"
    LEFT_BOTTOM = "lm"
    LEFT_DESCENDER = "ld"
    MIDDLE_ASCENDER = "ma"
    MIDDLE_TOP = "mt"
    MIDDLE_MIDDLE = "mm"
    MIDDLE_BASELINE = "ms"
    MIDDLE_BOTTOM = "mm"
    MIDDLE_DESCENDER = "md"


class ImageAnchors:
    RIGHT_TOP = (1, 0)
    RIGHT_MIDDLE = (1, 0.5)
    RIGHT_BOTTOM = (1, 1)
    LEFT_TOP = (0, 0)
    LEFT_MIDDLE = (0, 0.5)
    LEFT_BOTTOM = (0, 1)
    MIDDLE_TOP = (0.5, 0)
    MIDDLE_MIDDLE = (0.5, 0.5)
    MIDDLE_BOTTOM = (1, 0.5)


class Algin:
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


TypeGImage = TypeVar("TypeGImage", bound="GImage",)


class GImage:
    def __init__(
        self,
        image_path: str = None,
        box_size: tuple[int, int] = None,
        default_font_path: str = "uzura.ttf",
        default_font_size: int = 30,
        default_font_color: Colors = Colors.WHITE,
    ):
        if image_path is not None:
            self.__image = Image.open(image_path).convert('RGBA').copy()
        elif len(box_size) == 2:
            self.__image = Image.new(
                mode="RGBA", size=box_size, color=Colors.CLEAR)
        else:
            raise ValueError(
                "Either image path or box size, one value must be valid")
        self.set_default_font_color(default_font_color)
        self.set_default_font_size(default_font_size)
        self.set_font_path(default_font_path)

    def set_default_font_size(self, font_size):
        """デフォルトのフォントサイズを設定するためのメソッドです。"""
        self.default_font_size = font_size

    def set_default_font_color(self, font_color):
        """デフォルトのフォントカラーを設定するためのメソッドです。"""
        self.default_font_color = font_color

    def set_font_path(self, font_path):
        """デフォルトのフォントのパスを設定するためのメソッドです。"""
        self.font_path = font_path

    def get_font(self, font_path=None, font_size=None):
        """指定されたフォントのパスとサイズを使って、ImageFont.truetype関数を呼び出し、フォントオブジェクトを作成して返します。
        もし、フォントのパスが指定されていない場合は、デフォルトのフォントのパスが使われます。"""
        if font_size is None:
            font_size = self.default_font_size
        if font_path is None:
            font_path = self.font_path
        return ImageFont.truetype(font=font_path, size=font_size)

    def get_image(self):
        return self.__image

    def draw_text(
        self,
        text: str,
        position: tuple[int, int],
        anchor: str = None,
        align: str = None,
        font_size: int = None,
        font_color: Colors = None,
        font_path: str = None,
    ):
        """画像に文字列を描画するためのメソッドです。
        このメソッドは、文字列（text）、文字列を描画する座標（position）、文字列を描画する際のアンカー（anchor）、
        文字列を描画する際のテキストのアライン（align）、文字列を描画する際のフォントのパス（font_path）、
        文字列を描画する際のフォントサイズ（font_size）、文字列を描画する際のフォントカラー（font_color）
        の7つのパラメータを受け取ります。"""
        draw = ImageDraw.Draw(im=self.__image)
        draw.text(
            xy=position,
            text=text,
            fill=font_color,
            font=self.get_font(font_path=font_path, font_size=font_size),
            anchor=anchor,
            align=align,
        )

    def paste(self, im: Union[Image.Image, TypeGImage], box: tuple[int, int] = (0, 0)) -> None:
        if self == im:
            raise ValueError(
                "Because the same object is specified, PASTE cannot be performed.")
        if not isinstance(im, Image.Image):
            im = im.get_image()
        self.__image.paste(im=im, box=box, mask=im)

    def add_image(self, image_path, box: tuple[int, int] = (0, 0), size: tuple[int, int] = None, image_anchor: tuple[int, int] = ImageAnchors.LEFT_TOP):
        """画像を別の画像に貼り付けるためのメソッドです。
        貼り付ける画像（image）、貼り付ける位置（xy）、貼り付ける画像をリサイズするかどうか（resize）を受け取ります。
        貼り付ける位置は、アンカーと同様に、左上、左中央、左下、右上、右中央、右下、中央上、中央中央、中央下の9種類があります。"""
        im = Image.open(image_path).convert('RGBA').copy()
        if size is not None:
            im.thumbnail(size=size)

        box = (
            box[0] - int(im.size[0]*image_anchor[0]),
            box[1] - int(im.size[1]*image_anchor[1])
        )
        print(box)
        self.__image.paste(im=im, box=box, mask=im)

    def add_image_object(self, im: Image.Image, box: tuple[int, int] = (0, 0), size: tuple[int, int] = None, image_anchor: tuple[int, int] = ImageAnchors.LEFT_TOP):
        """画像を別の画像に貼り付けるためのメソッドです。
        貼り付ける画像（image）、貼り付ける位置（xy）、貼り付ける画像をリサイズするかどうか（resize）を受け取ります。
        貼り付ける位置は、アンカーと同様に、左上、左中央、左下、右上、右中央、右下、中央上、中央中央、中央下の9種類があります。"""
        if size is not None:
            im.thumbnail(size=size)

        box = (
            box[0] - int(im.size[0]*image_anchor[0]),
            box[1] - int(im.size[1]*image_anchor[1])
        )
        print(box)
        self.__image.paste(im=im, box=box, mask=im)

    def save(self, fp: str):
        self.__image.save(fp)

    def show(self):
        self.__image.show()
