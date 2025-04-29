from flask import Flask, render_template, send_file, request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io

app = Flask(__name__)

FONT_NAME = "static/JasonHandwriting4.ttf"
IMAGE_FILE = "static/S__14991387.jpg"

def create_image(date_str, is_red=False):
    try:
        img = Image.open(IMAGE_FILE).convert("RGB")
    except FileNotFoundError:
        return None

    try:
        font = ImageFont.truetype(FONT_NAME, size=380)
    except IOError:
        return None

    draw = ImageDraw.Draw(img)
    text_width, text_height = draw.textbbox((0, 0), date_str + '休', font=font)[2:4]
    x = (img.width - text_width) // 2
    y = 270
    fill_color = (68, 31, 13) if is_red else (40, 20, 0)
    draw.text((x, y), date_str + '休', font=font, fill=fill_color)

    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-image')
def generate_image():
    date_str = request.args.get('date', '')
    if not date_str:
        return "日期參數遺失", 400

    date_obj = datetime.strptime(date_str, '%m/%d')
    is_red = date_obj.weekday() >= 5  # 週末為假日
    img = create_image(date_str, is_red)

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
    if not date_str:
        return "日期參數遺失", 400

    date_obj = datetime.strptime(date_str, '%m/%d')
    is_red = date_obj.weekday() >= 5  # 週末為假日
    img = create_image(date_str, is_red)

    if img:
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, as_attachment=True, download_name=f"{date_str}_image.png", mimetype='image/png')
    else:
        return "無法生成圖片", 500

if __name__ == "__main__":
    app.run(debug=True)
