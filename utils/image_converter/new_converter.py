import textwrap

from PIL import Image, ImageDraw, ImageFont


class TimetableIMG:
    """Class for creating a schedule image from text"""
    final_img_width, final_img_height = (2600, 2700)
    font_h1 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=100)
    font_h2 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=70)
    font_h3 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=50)
    font_reqular = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Regular.ttf", size=40)
    font_bold = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Bold.ttf", size=45)
    font_italic = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Italic.ttf", size=40)

    def __init__(self, path_final_img: str):
        self.path_final_img = path_final_img
        self.current_image = self._create_foundation()
        self.x = 40
        self.y = 30

    @staticmethod
    def _create_foundation() -> Image:
        image = Image.new(mode="RGB",
                          size=(TimetableIMG.final_img_width, TimetableIMG.final_img_height),
                          color="white")
        with Image.open('data/converter/pictures_for_use/spbu.png') as image_spbu:
            image.paste(im=image_spbu, box=(image.width - image_spbu.width - 20, 0), mask=image_spbu)
        with Image.open('data/converter/pictures_for_use/spbu_logo.png') as image_spbu_logo:
            image.paste(im=image_spbu_logo, box=(-100, 200), mask=image_spbu_logo)
        return image

    def image_title(self, title: str, date: str):
        x, y = self.x - 15, self.y - 15
        image = self.current_image
        draw = ImageDraw.Draw(image)
        draw.text(xy=(x, y), text=title, font=TimetableIMG.font_h1, fill="black")
        y += TimetableIMG.font_h1.size + 30
        draw.text(xy=(x, y), text=date, font=TimetableIMG.font_h2, fill="black")
        y += TimetableIMG.font_h2.size + 40
        draw.line(xy=[(x, y), (image.width-x, y)], fill="black", width=5)
        y += 20
        self.x, self.y = x, y
        image.save(self.path_final_img)

    def _draw_text(self, xy: tuple, text: str, font: ImageFont, offset_x: int) -> tuple:
        image = self.current_image
        draw = ImageDraw.Draw(image)
        x, y = xy
        lines = textwrap.wrap(text, width=50)
        for line in lines:
            width, height = font.getsize(line)
            draw.text((x, y), f"  {line}", font=font, fill="black")
            y += height
        x += offset_x
        return x, y

    def insert_timetable(self, date: str, events: list):
        image = self.current_image
        draw = ImageDraw.Draw(image)
        skip, indent = 10, 80
        x, y = self._draw_text(xy=(self.x, self.y), text=date, font=TimetableIMG.font_h3, offset_x=indent)
        self.y += TimetableIMG.font_h3.size + skip
        for event in events:
            if y > self.final_img_height:
                break
            x, y = self._draw_text(xy=(x, y), text=event.subject_name, font=TimetableIMG.font_bold, offset_x=0)
            x, y = self._draw_text(xy=(x, y), text=event.educator, font=TimetableIMG.font_italic, offset_x=0)
            x, y = self._draw_text(xy=(x, y), text=event.locations, font=TimetableIMG.font_reqular, offset_x=0)
            x, y = self._draw_text(xy=(x, y), text=event.subject_format, font=TimetableIMG.font_italic, offset_x=0)
            draw.line(xy=[(x + 4, self.y + skip), (x + 4, y - skip // 2)], fill="red", width=5)
            draw.text(xy=(5, self.y + skip),
                      text="{}\n{}".format(event.start_time.strftime("%H:%M"), event.end_time.strftime("%H:%M")),
                      font=TimetableIMG.font_reqular, fill="black")
            self.x, self.y = x, y + skip
        self.y += TimetableIMG.font_reqular.size + skip
        self.x -= indent
        image.save(self.path_final_img)

    def crop_image(self):
        image = self.current_image
        image.crop(box=(0, 0, self.final_img_width, self.y)).save(self.path_final_img)
