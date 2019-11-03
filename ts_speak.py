from PIL import Image, ImageFont, ImageDraw
from textwrap import wrap

def draw_tss(text):
    offset = 10
    t_im, tw, th = text_bubble(text)
    im = Image.new('RGB', (2*offset + tw + 135, 2*offset + th + 46), (237, 238, 237))
    head = Image.open('resources/head.png', 'r')
    name = Image.open('resources/name.png', 'r')
    im.paste(head, (offset + 0, offset + 8))
    im.paste(name, (offset + 151, offset + 0))
    im.paste(t_im, (offset + 133, offset + 47))
    im.save("ts.png")

def draw_bg(width, height):
    im = Image.new('RGB', (height, width), (237, 238, 237))
    return im


def t_wrap(text):
    return "\n".join(wrap(text, width=14))

def draw_text(text):
    text = t_wrap(text)
    font = ImageFont.truetype("PingFang.ttc", size=46)
    t_im = Image.new('RGB', (10, 10), (255, 255, 255))
    draw = ImageDraw.Draw(t_im)
    w, h = draw.multiline_textsize(text, font=font)
    t_im = Image.new('RGB', (w, h + 73), (255, 255, 255))
    draw = ImageDraw.Draw(t_im)
    draw.multiline_text((0, 30), text, font=font, fill=(0, 0, 0, 255))
    return t_im, w, h + 73

def text_bubble(text):
    t_im, tw, th = draw_text(text)
    bg = Image.new('RGB', (tw + 92, th), (237, 238, 237))
    bg.paste(t_im, (53, 0))
    lu = Image.open('resources/bb_lu.png', 'r')
    ru = Image.open('resources/bb_ru.png', 'r')
    lb = Image.open('resources/bb_lb.png', 'r')
    rb = Image.open('resources/bb_rb.png', 'r')
    bg.paste(lu, (0, -1))
    bg.paste(ru, (53 + tw, 0))
    bg.paste(lb, (14, th - 40))
    bg.paste(rb, (53 + tw, th - 40))
    diff = th-126
    if (diff > 0):
        white = Image.new('RGB', (39, diff+1), (255, 255, 255))
        bg.paste(white, (15, 85))
        bg.paste(white, (53 + tw, 86))

    return bg, tw + 92, th
