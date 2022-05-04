import textwrap
from PIL import Image, ImageDraw, ImageFont

class TimetableIMG:
    """Class for creating a schedule image from text"""
    _final_img_width, _final_img_height = 3800, 5500
    _font_h1 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=100)
    _font_h2 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=70)
    _font_h3 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=50)
    _font_reqular = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Regular.ttf", size=40)
    _font_bold = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Bold.ttf", size=45)
    _font_italic = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Italic.ttf", size=40)

    def __init__(self, path_final_img: str):
        self._path_final_img: str = path_final_img
        self._current_image: Image = self._create_foundation()
        self._x: int = 40
        self._y: int = 30
        self._y_foundation: int = 0
        self._y_max: int = 0

    @staticmethod
    def _create_foundation() -> Image:
        image = Image.new(mode="RGB",
                          size=(TimetableIMG._final_img_width, TimetableIMG._final_img_height),
                          color="white")
        with Image.open('data/converter/pictures_for_use/spbu.png') as image_spbu:
            image.paste(im=image_spbu, box=(image.width - image_spbu.width - 30, 0), mask=image_spbu)
        with Image.open('data/converter/pictures_for_use/spbu_logo.png') as image_spbu_logo:
            image.paste(im=image_spbu_logo, box=(200, 300), mask=image_spbu_logo)
        return image

    def create_image_title(self, title: str, date: str):
        x, y = self._x - 15, self._y - 15
        image = self._current_image
        draw = ImageDraw.Draw(image)
        draw.text(xy=(x, y), text=title, font=TimetableIMG._font_h1, fill="black")
        y += TimetableIMG._font_h1.size + 30
        draw.text(xy=(x, y), text=date, font=TimetableIMG._font_h2, fill="black")
        y += TimetableIMG._font_h2.size + 40
        draw.line(xy=[(x, y), (image.width-x, y)], fill="black", width=5)
        y += 20
        self._x = x
        self._y = self._y_foundation = self._y_max = y

    def _draw_text(self, xy: tuple, text: str, font: ImageFont, event_cancelled: bool = False) -> tuple:
        image = self._current_image
        draw = ImageDraw.Draw(image)
        x, y = xy
        lines = textwrap.wrap(text, width=self._final_img_width * 0.9 // font.size)
        for line in lines:
            width, height = font.getsize(line)
            draw.text((x, y), f"  {line}", font=font, fill="grey" if event_cancelled else "black")
            y += height
        return x, y

    def insert_timetable(self, date: str, events: list):
        image = self._current_image
        draw = ImageDraw.Draw(image)
        skip, indent = 10, 90
        x, y = self._draw_text(xy=(self._x, self._y), text=date, font=TimetableIMG._font_h3)
        x += indent
        self._y += TimetableIMG._font_h3.size + skip
        for event in events:
            x, y = self._draw_text(xy=(x, y), text=event.subject_name,
                                   font=TimetableIMG._font_bold, event_cancelled=event.is_canceled)
            x, y = self._draw_text(xy=(x, y), text=event.educator if hasattr(event, "educator") else event.groups,
                                   font=TimetableIMG._font_italic, event_cancelled=event.is_canceled)
            x, y = self._draw_text(xy=(x, y), text=event.locations,
                                   font=TimetableIMG._font_reqular, event_cancelled=event.is_canceled)
            x, y = self._draw_text(xy=(x, y), text=event.subject_format,
                                   font=TimetableIMG._font_italic, event_cancelled=event.is_canceled)
            draw.line(xy=[(x + 10, self._y + skip), (x + 10, y - skip // 2)], fill="red", width=5)
            draw.text(xy=(x - indent, self._y + skip),
                      text="{}\n{}".format(event.start_time.strftime("%H:%M"), event.end_time.strftime("%H:%M")),
                      font=TimetableIMG._font_reqular, fill="black")
            if y > self._y_max:
                self._y_max = y
            if y > self._final_img_width - 300 and x >= self._final_img_width // 2:
                break
            if y > self._final_img_width - 300:
                x, y = self._final_img_width // 2, self._y_foundation
            self._x, self._y = x, y + skip
        self._y += TimetableIMG._font_reqular.size + skip
        self._x -= indent

    def crop_image(self):
        image = self._current_image
        image.crop(box=(0, 0, self._final_img_width, self._y_max + 15)).save(self._path_final_img)
