"""快速生成logo
横向：pp Hello world
竖直：pp Hello world 1
"""
# 主要代码部分 https://github.com/akarrin/ph-logo/
import base64
import io

from EAbotoy import MsgTypes
from EAbotoy.contrib import get_cache_dir
from EAbotoy.decorators import these_msgtypes
from EAbotoy.model import WeChatMsg
from EAbotoy.sugar import Picture
from PIL import Image, ImageDraw, ImageFont

LEFT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT = 2
LEFT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH = 1 / 4
RIGHT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT = 1
RIGHT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH = 1 / 4
RIGHT_PART_RADII = 10
BG_COLOR = "#000000"
BOX_COLOR = "#F7971D"
LEFT_TEXT_COLOR = "#FFFFFF"
RIGHT_TEXT_COLOR = "#000000"
FONT_SIZE = 50

FONT_PATH = get_cache_dir("phlogo") / "ArialEnUnicodeBold.ttf"
if not FONT_PATH.exists():
    print("phlogo插件: 下载字体中....")
    import os

    import httpx

    try:
        with httpx.stream(
                "GET",
                "https://github.com/opq-osc/botoy-plugins/releases/download/phlogo%E6%89%80%E9%9C%80%E5%AD%97%E4%BD"
                "%93/ArialEnUnicodeBold.ttf",
        ) as resp:
            print("连接字体资源成功")
            total_size = int(resp.headers["content-length"])
            downloaded_size = 0
            with open(FONT_PATH, "wb") as f:
                for chunk in resp.iter_bytes():
                    percent = int(100 * downloaded_size / total_size)
                    print("\r|{:100}|{}%".format("#" * percent, percent), end="")
                    f.write(chunk)
                    downloaded_size += 1024
        print("\n下载字体完成")
    except Exception:
        if FONT_PATH.exists():
            os.remove(FONT_PATH)
            raise

FONT_PATH = str(FONT_PATH)


def create_left_part_img(text: str, font_size: int, type_="h"):
    font = ImageFont.truetype(FONT_PATH, font_size)
    font_width, font_height = font.getsize(text)
    offset_y = font.font.getsize(text)[1][1]
    if type_ == "h":
        blank_height = font_height * 2
    else:
        blank_height = font_height
    right_blank = int(
        font_width / len(text) * LEFT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH
    )
    img_height = font_height + offset_y + blank_height * 2
    image_width = font_width + right_blank
    image_size = image_width, img_height
    image = Image.new("RGBA", image_size, BG_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((0, blank_height), text, fill=LEFT_TEXT_COLOR, font=font)
    return image


def create_right_part_img(text: str, font_size: int):
    radii = RIGHT_PART_RADII
    font = ImageFont.truetype(FONT_PATH, font_size)
    font_width, font_height = font.getsize(text)
    offset_y = font.font.getsize(text)[1][1]
    blank_height = font_height * RIGHT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT
    left_blank = int(
        font_width / len(text) * RIGHT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH
    )
    image_width = font_width + 2 * left_blank
    image_height = font_height + offset_y + blank_height * 2
    image = Image.new("RGBA", (image_width, image_height), BOX_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((left_blank, blank_height), text, fill=RIGHT_TEXT_COLOR, font=font)

    # 圆
    magnify_time = 10
    magnified_radii = radii * magnify_time
    circle = Image.new(
        "L", (magnified_radii * 2, magnified_radii * 2), 0
    )  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, magnified_radii * 2, magnified_radii * 2), fill=255)  # 画白色圆形

    # 画4个角（将整圆分离为4个部分）
    magnified_alpha_width = image_width * magnify_time
    magnified_alpha_height = image_height * magnify_time
    alpha = Image.new("L", (magnified_alpha_width, magnified_alpha_height), 255)
    alpha.paste(circle.crop((0, 0, magnified_radii, magnified_radii)), (0, 0))  # 左上角
    alpha.paste(
        circle.crop((magnified_radii, 0, magnified_radii * 2, magnified_radii)),
        (magnified_alpha_width - magnified_radii, 0),
    )  # 右上角
    alpha.paste(
        circle.crop(
            (magnified_radii, magnified_radii, magnified_radii * 2, magnified_radii * 2)
        ),
        (
            magnified_alpha_width - magnified_radii,
            magnified_alpha_height - magnified_radii,
        ),
    )  # 右下角
    alpha.paste(
        circle.crop((0, magnified_radii, magnified_radii, magnified_radii * 2)),
        (0, magnified_alpha_height - magnified_radii),
    )  # 左下角
    alpha = alpha.resize((image_width, image_height), Image.ANTIALIAS)
    image.putalpha(alpha)
    return image


def combine_img_horizontal(
        left_text: str, right_text, font_size: int = FONT_SIZE
) -> str:
    left_img = create_left_part_img(left_text, font_size)
    right_img = create_right_part_img(right_text, font_size)
    blank = 30
    bg_img_width = left_img.width + right_img.width + blank * 2
    bg_img_height = left_img.height
    bg_img = Image.new("RGBA", (bg_img_width, bg_img_height), BG_COLOR)
    bg_img.paste(left_img, (blank, 0))
    bg_img.paste(
        right_img,
        (blank + left_img.width, int((bg_img_height - right_img.height) / 2)),
        mask=right_img,
    )
    buffer = io.BytesIO()
    bg_img.save(buffer, format="png")
    return base64.b64encode(buffer.getvalue()).decode()


def combine_img_vertical(left_text: str, right_text, font_size: int = FONT_SIZE) -> str:
    left_img = create_left_part_img(left_text, font_size, type_="v")
    right_img = create_right_part_img(right_text, font_size)
    blank = 15
    bg_img_width = max(left_img.width, right_img.width) + blank * 2
    bg_img_height = left_img.height + right_img.height + blank * 2
    bg_img = Image.new("RGBA", (bg_img_width, bg_img_height), BG_COLOR)
    bg_img.paste(left_img, (int((bg_img_width - left_img.width) / 2), blank))
    bg_img.paste(
        right_img,
        (int((bg_img_width - right_img.width) / 2), blank + left_img.height),
        mask=right_img,
    )
    buffer = io.BytesIO()
    bg_img.save(buffer, format="png")
    return base64.b64encode(buffer.getvalue()).decode()


@these_msgtypes(MsgTypes.TextMsg)
def receive_wx_msg(ctx: WeChatMsg):
    if ctx.Content.startswith("pp "):
        args = [i.strip() for i in ctx.Content.split(" ") if i.strip()]
        if len(args) >= 3:
            left = args[1]
            right = args[2]
            f = combine_img_horizontal
            if len(args) >= 4:
                if args[3] == "1":
                    f = combine_img_vertical
            Picture(pic_base64=f(left, right))
