from PIL import Image, ImageDraw, ImageFont
import re


class TimetableIMG:
    """Class for creating a schedule image from text"""
    final_img_width, final_img_height = (2200, 2700)
    font_h1 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=100)
    font_h2 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=80)
    font_h3 = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Medium.ttf", size=50)
    font_reqular = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Regular.ttf", size=45)
    font_bold = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Bold.ttf", size=45)
    font_italic = ImageFont.truetype(font="data/converter/FiraSansFonts/FiraSans-Italic.ttf", size=45)

    def __init__(self, path_final_img):
        self.path_final_img = path_final_img
        self.current_image = self.create_foundation()
        self.x = 30
        self.y = 30

    @staticmethod
    def create_foundation() -> Image:
        image_spbu = Image.open('data/converter/pictures_for_use/spbu.png')
        image_spbu_logo = Image.open('data/converter/pictures_for_use/spbu_logo.png')
        image = Image.new(mode="RGB",
                          size=(TimetableIMG.final_img_width, TimetableIMG.final_img_height),
                          color="white")
        image.paste(im=image_spbu, box=(image.width - image_spbu.width, 0))
        image_spbu.close()
        image.paste(im=image_spbu_logo, box=(-50, 300), mask=image_spbu_logo)
        image_spbu_logo.close()
        return image

    def image_title(self, title, date):
        x, y = self.x - 15, self.y - 15
        image = self.current_image
        draw = ImageDraw.Draw(image)
        draw.text(xy=(x, y), text=title, font=TimetableIMG.font_h1, fill="black")
        y += TimetableIMG.font_h1.size + 30
        draw.text(xy=(x, y), text=date, font=TimetableIMG.font_h2, fill="black")
        y += TimetableIMG.font_h2.size + 30
        draw.line(xy=[(x, y), (image.width-x, y)], fill="black", width=5)
        y += 20
        self.x, self.y = x, y
        image.save(self.path_final_img)

    def insert_timetable(self, timetable: str):
        text = re.findall(r">([^<]+)</", timetable)
        image = self.current_image
        draw = ImageDraw.Draw(image)
        draw.text(xy=(self.x, self.y), text=text[0], font=TimetableIMG.font_h2, fill="black")
        skip = 10
        indent = 120
        self.y += TimetableIMG.font_h2.size + skip
        x, y = self.x + indent, self.y
        for i in range(1, len(text), 5):
            if text[i + 1].find('\n') == -1:
                draw.text(xy=(x, y), text="  {}".format(text[i + 1]), font=TimetableIMG.font_bold, fill="black")
                y += TimetableIMG.font_bold.size + skip
            else:
                draw.multiline_text(xy=(x, y), align="left", text="  {}".format(text[i + 1]),
                                    font=TimetableIMG.font_bold, fill="black")
                y += (TimetableIMG.font_bold.size + skip) * 2
            draw.text(xy=(x, y), text="  {}".format(text[i + 2]), font=TimetableIMG.font_italic, fill="black")
            y += TimetableIMG.font_italic.size + skip
            if text[i + 3].find('\n') == -1:
                draw.text(xy=(x, y), text="  {}".format(text[i + 3]), font=TimetableIMG.font_reqular, fill="black")
                y += TimetableIMG.font_reqular.size + skip
            else:
                draw.multiline_text(xy=(x, y), align="left", text="  {}".format(text[i + 3]),
                                    font=TimetableIMG.font_reqular, fill="black")
                y += (TimetableIMG.font_reqular.size + skip) * 2
            draw.text(xy=(x, y), text="  {}".format(text[i + 4]), font=TimetableIMG.font_italic, fill="black")
            y += TimetableIMG.font_italic.size + skip
            draw.line(xy=[(x + 4, self.y + skip), (x + 4, y - skip//2)], fill="red", width=5)
            draw.multiline_text(xy=(10, self.y + skip),
                                text="{}\n{}".format(text[i].split('–')[0], text[i].split('–')[1]),
                                font=TimetableIMG.font_h3, fill="black")
            y += skip
            self.x, self.y = x, y
        self.y += TimetableIMG.font_reqular.size + skip
        self.x -= indent
        image.save(self.path_final_img)
