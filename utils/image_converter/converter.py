from PIL import Image, ImageDraw, ImageFont
import re


class TimetableIMG:
    """Class for creating a schedule image from text"""
    final_img_width, final_img_height = (2500, 2900)
    font_h1 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=100)
    font_h2 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=70)
    font_h3 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=50)
    font_reqular = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Regular.ttf", size=45)
    font_bold = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Bold.ttf", size=45)
    font_italic = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Italic.ttf", size=45)

    def __init__(self, path_final_img: str):
        self.path_final_img = path_final_img
        self.current_image = self.create_foundation()
        self.x = 50
        self.y = 30
        self.days_count = 0
        self.title_y = 0

    @staticmethod
    def create_foundation() -> Image:
        image_spbu = Image.open('data/converter/pictures_for_use/spbu.png')
        image_spbu_logo = Image.open('data/converter/pictures_for_use/spbu_logo.png')
        image = Image.new(mode="RGB",
                          size=(TimetableIMG.final_img_width, TimetableIMG.final_img_height),
                          color="white")
        image.paste(im=image_spbu, box=(image.width - image_spbu.width - 20, 10), mask=image_spbu)
        image_spbu.close()
        image.paste(im=image_spbu_logo, box=(-100, 200), mask=image_spbu_logo)
        image_spbu_logo.close()
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
        self.x, self.y, self.title_y = x, y, y
        image.save(self.path_final_img)

    def draw_text(self, xy: tuple, text: str, font: ImageFont, offset_x: int, offset_y: int) -> tuple:
        image = self.current_image
        draw = ImageDraw.Draw(image)
        x, y = xy
        if text.find('\n') == -1:
            draw.text(xy=xy, text=text, font=font, fill="black")
            y += font.size + offset_y
        else:
            draw.multiline_text(xy=xy, align="left", text=text, font=font, fill="black")
            y += (font.size + offset_y) * (len([i for i in text if i == '\n']) + 1)
        x += offset_x
        return x, y

    def insert_timetable(self, timetable: str):
        text = re.findall(r">([^<]+)</", timetable)
        image = self.current_image
        draw = ImageDraw.Draw(image)
        skip = 10
        indent = 120
        if self.days_count == 3:
            self.x, self.y = self.final_img_width//2 - 40, self.title_y
        x, y = self.draw_text(xy=(self.x, self.y), text=text[0], font=TimetableIMG.font_h2,
                              offset_x=indent, offset_y=skip)
        self.y += TimetableIMG.font_h2.size + skip
        for i in range(1, len(text), 5):
            x, y = self.draw_text(xy=(x, y), text=f"  {text[i]}", font=TimetableIMG.font_bold,
                                  offset_x=0, offset_y=skip)
            x, y = self.draw_text(xy=(x, y), text=f"  {text[i + 2]}", font=TimetableIMG.font_italic,
                                  offset_x=0, offset_y=skip)
            x, y = self.draw_text(xy=(x, y), text=f"  {text[i + 4]}", font=TimetableIMG.font_reqular,
                                  offset_x=0, offset_y=skip)
            x, y = self.draw_text(xy=(x, y), text=f"  {text[i + 3]}", font=TimetableIMG.font_italic,
                                  offset_x=0, offset_y=skip)
            draw.line(xy=[(x + 4, self.y + skip), (x + 4, y - skip//2)], fill="red", width=5)
            self.draw_text(xy=((self.days_count >= 3) * (self.final_img_width//2 - 80) + 30,
                               self.y + skip),
                           text="{}\n{}".format(text[i+1].split('–')[0], text[i+1].split('–')[1]),
                           font=TimetableIMG.font_h3, offset_x=0, offset_y=0)
            self.x, self.y = x, y + skip
        self.y += TimetableIMG.font_reqular.size + skip
        self.x -= indent
        self.days_count += 1
        image.save(self.path_final_img)

    def crop_image(self):
        if self.days_count < 3:
            image = self.current_image
            image.crop(box=(0, 0, self.final_img_width, self.y)).save(self.path_final_img)
