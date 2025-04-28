from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import io
import os

app = Flask(__name__)

FONT_NAME = "JasonHandwriting4.ttf"
IMAGE_FILE = "static/S__14991387.jpg"

def format_date(dt):
    return f"{dt.month}/{dt.day}"

def format_display_date(dt):
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    label = f"{dt.month}/{dt.day}({weekdays[dt.weekday()]})"
    if dt.year != datetime.today().year:
        label += f" - {dt.year}"
    return label

def is_holiday(dt):
    return dt.weekday() >= 5

def create_image(date_str, is_red=False):
    try:
        img = Image.open(IMAGE_FILE).convert("RGB")
        font = ImageFont.truetype(FONT_NAME, size=380)
        draw = ImageDraw.Draw(img)
        text_width, text_height = draw.textbbox((0, 0), date_str + '休', font=font)[2:4]
        x = (img.width - text_width) // 2
        y = 270
        fill_color = (68, 31, 13) if is_red else (40, 20, 0)
        draw.text((x, y), date_str + '休', font=font, fill=fill_color)
        return img
    except Exception as e:
        print("錯誤：", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.today()
    full_date_list = [today + timedelta(days=i) for i in range(-7, 8)]
    display_dates = [(d.strftime('%Y-%m-%d'), format_display_date(d)) for d in full_date_list]

    selected_date_str = request.form.get("date")
    image_data = None

    if selected_date_str:
        dt = datetime.strptime(selected_date_str, "%Y-%m-%d")
        date_only = format_date(dt)
        img = create_image(date_only, is_red=is_holiday(dt))
        if img:
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            image_data = f"data:image/png;base64,{img_io.getvalue().hex()}"  # optional, for inline img

    return render_template("index.html", dates=display_dates, image=selected_date_str if image_data else None)

@app.route('/download', methods=['POST'])
def download():
    selected_date_str = request.form.get("date")
    if selected_date_str:
        dt = datetime.strptime(selected_date_str, "%Y-%m-%d")
        date_only = format_date(dt)
        img = create_image(date_only, is_red=is_holiday(dt))
        if img:
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            filename = f"output_{dt.month:02d}{dt.day:02d}.png"
            return send_file(img_io, as_attachment=True, download_name=filename, mimetype='image/png')
    return "生成失敗", 400
