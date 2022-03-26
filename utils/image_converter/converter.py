from PIL import Image, ImageDraw, ImageFont


class TimetablePicture:
    """Class for creating a schedule image from text"""
    final_img_width = 1150
    final_img_height = 2560

    def __init__(self, path_final_img):
        self.path_final_img = path_final_img

    @staticmethod
    def create_foundation() -> Image:
        image_spbu = Image.open('utils/image_converter/pictures_for_use/spbu.png')
        image_spbu_logo = Image.open('utils/image_converter/pictures_for_use/spbu_logo.png')
        image = Image.new(mode="RGB",
                          size=(TimetablePicture.final_img_width, TimetablePicture.final_img_height),
                          color="white")
        image.paste(im=image_spbu, box=(image.width - image_spbu.width, 10))
        image_spbu.close()
        image.paste(im=image_spbu_logo, box=(30, 700), mask=image_spbu_logo)
        image_spbu_logo.close()
        return image

    def image_title(self, image, title, date):
        draw = ImageDraw.Draw(image)
        font_h1 = ImageFont.truetype(font="utils/image_converter/FiraSansFonts/FiraSans-Medium.ttf", size=60)
        font_h2 = ImageFont.truetype(font="utils/image_converter/FiraSansFonts/FiraSans-Medium.ttf", size=50)
        x, y = 30, 30
        draw.text(xy=(x, y), text=title, font=font_h1, fill="black")
        y += font_h1.size + 30
        draw.text(xy=(x, y), text=date, font=font_h2, fill="black")
        y += font_h2.size + 30
        draw.line(xy=[(x, y), (image.width-x, y)], fill="black")

        image.save(self.path_final_img)


if __name__ == "__main__":
    schedule_pic = TimetablePicture("output.png")
    foundation = schedule_pic.create_foundation()
    schedule_pic.image_title(foundation)
