from flask import Flask, render_template, send_file, request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io

app = Flask(__name__)

FONT_NAME = "static/JasonHandwriting4.ttf"
IMAGE_FILE = "static/S__14991387.jpg"

def create_image(date_str):
    try:
        img = Image.open(IMAGE_FILE).convert("RGB")
    except FileNotFoundError:
        return None

    try:
        font = ImageFont.truetype(FONT_NAME, size=380)
    except IOError:
        return None

    # 將 "01/01" 或 "12/03" 類格式轉為 "1/1" 或 "12/3"
    try:
        date_obj = datetime.strptime(date_str, '%m/%d')
        date_str = f"{date_obj.month}/{date_obj.day}"
    except ValueError:
        pass  # 若格式不符，保留原樣（避免崩潰）

    draw = ImageDraw.Draw(img)
    text_width, text_height = draw.textbbox((0, 0), date_str + '休', font=font)[2:4]
    x = (img.width - text_width) // 2
    y = 270
    fill_color = (66, 31, 12)
    draw.text((x, y), date_str + '休', font=font, fill=fill_color)

    return img

@app.route('/')
def index():
    today = datetime.today()
    current_date = today
    return render_template('index.html', today=today)

@app.route('/generate-image')
def generate_image():
    date_str = request.args.get('date', '')
    if not date_str:
        return "日期參數遺失", 400

    date_obj = datetime.strptime(date_str, '%m/%d')
    img = create_image(date_str)

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
    img = create_image(date_str)

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
