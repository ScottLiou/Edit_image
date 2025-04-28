from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import io
import base64

app = Flask(__name__)

FONT_NAME = "static/JasonHandwriting4.ttf"
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
    img = Image.open(IMAGE_FILE).convert("RGB")
    font = ImageFont.truetype(FONT_NAME, size=380)
    draw = ImageDraw.Draw(img)

    text = date_str + '休'
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    x = (img.width - text_width) // 2
    y = 270
    fill_color = (68, 31, 13) if is_red else (40, 20, 0)
    draw.text((x, y), text, font=font, fill=fill_color)
    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.today()
    current_date = today

    if request.method == 'POST':
        if 'date' in request.form:
            current_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        elif 'delta' in request.form:
            delta = int(request.form['delta'])
            base_date = datetime.strptime(request.form['base_date'], '%Y-%m-%d')
            current_date = base_date + timedelta(days=delta)

    date_only = format_date(current_date)
    is_red = is_holiday(current_date)
    img = create_image(date_only, is_red)

    buf = io.BytesIO()
    img.thumbnail((300, 300))
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    full_date_list = [today + timedelta(days=i) for i in range(-365, 366)]
    dates = [(d.strftime('%Y-%m-%d'), format_display_date(d)) for d in full_date_list]

    return render_template(
        'index.html',
        image_data=img_b64,
        selected_date=current_date.strftime('%Y-%m-%d'),
        dates=dates,
        current_date=current_date
    )

@app.route('/download', methods=['POST'])
def download():
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    date_only = format_date(date)
    is_red = is_holiday(date)
    img = create_image(date_only, is_red)
    now = datetime.now()
    filename = f"output_{date.month:02d}{date.day:02d}_{now.hour:02d}{now.minute:02d}{now.second:02d}.png"

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
