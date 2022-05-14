import textwrap
from typing import List

from PIL import Image, ImageDraw, ImageFont

from utils.db_api.db_timetable import StudyEvent
from utils.timetable.helpers import is_basic_events_info_identical


class TimetableIMG:
    """Class for creating a schedule image from text"""
    _final_img_width, _final_img_height = 3800, 4300
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

    def create_image_title(self, title: str, date: str) -> None:
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

    def _draw_text(self, xy: tuple, text: str, font: ImageFont, event_cancelled: bool = False) -> int:
        image = self._current_image
        draw = ImageDraw.Draw(image)
        x, y = xy
        lines = textwrap.wrap(text, width=int(self._final_img_width * 0.9 // font.size))
        for line in lines:
            width, height = font.getsize(line)
            draw.text((x, y), f"  {line}", font=font, fill="grey" if event_cancelled else "black")
            y += height
        return y

    def _insert_events(self, draw: ImageDraw, skip: int, indent: int, x: int, y: int, events: List[StudyEvent]) -> None:
        for i, event in enumerate(events):
            if i == 0 or is_basic_events_info_identical(events[i-1], events[i]):
                if i == 0 or events[i-1].start_time != event.start_time or events[i-1].end_time != event.end_time:
                    event_time = f"{event.start_time.strftime('%H:%M')}\n{event.end_time.strftime('%H:%M')}"
                    draw.text(xy=(x - indent, y), text=event_time,
                              font=TimetableIMG._font_reqular, fill="grey" if event.is_canceled else "black")
                y = self._draw_text(xy=(x, y), text=event.subject_name,
                                    font=TimetableIMG._font_bold, event_cancelled=event.is_canceled)
                y = self._draw_text(xy=(x, y), text=event.subject_format,
                                    font=TimetableIMG._font_italic, event_cancelled=event.is_canceled)
            y_for_subject_line = y
            y = self._draw_text(xy=(x + 25, y), text=event.contingent,
                                font=TimetableIMG._font_italic, event_cancelled=event.is_canceled)
            y = self._draw_text(xy=(x + 25, y), text=event.locations,
                                font=TimetableIMG._font_reqular, event_cancelled=event.is_canceled)
            draw.line(xy=[(x + 25, y_for_subject_line + skip // 2), (x + 25, y - skip // 2)],
                      fill="grey" if event.is_canceled else "#0088cc", width=3)

            if y > self._y_max:
                self._y_max = y
            if y > self._final_img_height - 300:
                if x >= self._final_img_width // 2:
                    self._x, self._y = x, y
                    break
                x, y = self._final_img_width // 2 + indent, self._y_foundation
            self._x, self._y = x, y + skip

    def insert_timetable(self, date: str, events: List[StudyEvent]) -> None:
        image = self._current_image
        draw = ImageDraw.Draw(image)
        skip, indent = 15, 90
        if self._y > self._final_img_height - 500 and self._x >= self._final_img_width // 2:
            return
        y = self._draw_text(xy=(self._x, self._y), text=date, font=TimetableIMG._font_h3)
        x = self._x + indent
        self._y += TimetableIMG._font_h3.size + skip

        self._insert_events(draw, skip, indent, x, y, events)
        self._y += TimetableIMG._font_reqular.size
        self._x -= indent

    def crop_image(self) -> None:
        image = self._current_image
        image = image.crop(box=(0, 0, self._final_img_width, min(self._y_max + 15, self._final_img_height)))
        image.save(self._path_final_img, 'jpeg')
