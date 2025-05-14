from flask import Flask, render_template, send_file, request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io

app = Flask(__name__)

FONT_NAME = "static/JasonHandwriting4.ttf"
IMAGE_FILE = "static/S__14991387.jpg"

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

IMAGE_FILE = "static/S__14991387.jpg"
FONT_NAME = "static/JasonHandwriting4.ttf"

def create_image(date_str, event_type="休"):
    try:
        img = Image.open(IMAGE_FILE).convert("RGB")
    except FileNotFoundError:
        return None

    try:
        font = ImageFont.truetype(FONT_NAME, size=380)
        activity_font = ImageFont.truetype(FONT_NAME, size=240) 
    except IOError:
        return None

    try:
        date_obj = datetime.strptime(date_str, '%m/%d')
        date_str = f"{date_obj.month}/{date_obj.day}"
    except ValueError:
        pass

    draw = ImageDraw.Draw(img)
    fill_color = (66, 31, 12)
    line_spacing = 250

    if event_type in ["會議", "課程"]:
        # 畫「日期」文字
        date_width, date_height = draw.textbbox((0, 0), date_str, font=font)[2:4]
        date_x = (img.width - date_width) // 2 - 250
        date_y = 270
        draw.text((date_x, date_y), date_str, font=font, fill=fill_color)

        # 計算日期底部位置
        date_bottom = date_y + date_height

        # 畫直向活動文字，底部對齊日期
        for i, char in enumerate(event_type):
            text_width, text_height = draw.textbbox((0, 0), char, font=activity_font)[2:4]
            text_x = date_x + date_width + 20 + i * line_spacing  # 活動在右側
            text_y = date_bottom - text_height  # 計算字的底部位置對齊日期底部
            draw.text((text_x, text_y), char, font=activity_font, fill=fill_color)

    else:
        # 僅畫一次：日期 + 活動 一起畫成橫向
        full_text = f"{date_str}{event_type}"
        text_width, text_height = draw.textbbox((0, 0), full_text, font=font)[2:4]
        x = (img.width - text_width) // 2
        y = 270
        draw.text((x, y), full_text, font=font, fill=fill_color)

    return img

@app.route('/')
def index():
    today = datetime.today()
    current_date = today
    return render_template('index.html', today=today)

@app.route('/generate-image')
def generate_image():
    date_str = request.args.get('date', '')
    event_type = request.args.get('type', '休')
    if not date_str:
        return "日期參數遺失", 400

    img = create_image(date_str, event_type)

    if img:
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    else:
        return "無法生成圖片", 500

@app.route('/download')
def download_image():
    date_str = request.args.get('date', '')
    event_type = request.args.get('type', '休')
    if not date_str:
        return "日期參數遺失", 400

    date_obj = datetime.strptime(date_str, '%m/%d')
    img = create_image(date_str, event_type)

    if img:
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        dt = datetime.today()
        filename = f"output_{date_obj.month:02d}{date_obj.day:02d}_{dt.hour:02d}{dt.minute:02d}{dt.second:02d}.png"
        return send_file(img_io, as_attachment=True, download_name=filename, mimetype='image/png')
    else:
        return "無法生成圖片", 500

if __name__ == "__main__":
    app.run(debug=True)
