from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def calculate_lived_weeks(birth_date):
    today = datetime.now().date()
    lived_days = (today - birth_date).days
    return lived_days // 7

def generate_life_table(birth_date, gender):
    lived_weeks = calculate_lived_weeks(birth_date)

    cell_size = 10
    cols = 52  # тижнів у році
    rows = 67 if gender == 'Чоловік' else 73
    margin_x, margin_y = 80, 80
    width = cols * cell_size + margin_x
    height = rows * cell_size + margin_y

    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 8)
    except IOError:
        font = ImageFont.load_default()
        font_small = font

    # Заголовок
    draw.text((width // 2 - 100, 10), "Твоє життя в тижнях", fill='navy', font=font)

    # Підписи тижнів (по горизонталі)
    for col in range(0, cols, 5):
        x = 60 + col * cell_size
        draw.text((x, 50), str(col + 1), fill='blue', font=font_small)

    # Якщо останній стовпчик не був підписаний — підписати
    if (cols - 1) % 5 != 0:
        x = 60 + (cols - 1) * cell_size
        draw.text((x, 50), str(cols), fill='blue', font=font_small)

    # Підписи років (по вертикалі)
    for row in range(0, rows, 5):
        y = 60 + row * cell_size
        draw.text((50, y), str(row), fill='blue', font=font_small)

    # Якщо останній рядок не був підписаний — підписати
    if (rows - 1) % 5 != 0:
        y = 60 + (rows - 1) * cell_size
        draw.text((50, y), str(rows - 1), fill='blue', font=font_small)

    # Малюємо клітинки
    week_counter = 0
    for row in range(rows):
        for col in range(cols):
            x0 = 60 + col * cell_size
            y0 = 60 + row * cell_size
            x1 = x0 + cell_size - 1
            y1 = y0 + cell_size - 1

            color = 'red' if week_counter < lived_weeks else 'white'
            draw.rectangle([x0, y0, x1, y1], fill=color, outline='gray')
            week_counter += 1

    # --- Горизонтальна стрілка "Номер недели"
    arrow_y = 40
    arrow_length = 100
    start_x = 60
    draw.line([(start_x, arrow_y), (start_x + arrow_length, arrow_y)], fill='blue', width=2)
    draw.polygon([
        (start_x + arrow_length, arrow_y),
        (start_x + arrow_length - 6, arrow_y - 4),
        (start_x + arrow_length - 6, arrow_y + 4)
    ], fill='blue')
    draw.text((start_x, arrow_y - 15), "Номер тижня", fill='blue', font=font)

    # --- Вертикальна стрілка "Возраст"
    arrow_x = 35
    arrow_length_v = 80
    start_y = 50
    draw.line([(arrow_x, start_y), (arrow_x, start_y + arrow_length_v)], fill='blue', width=2)
    draw.polygon([
        (arrow_x, start_y + arrow_length_v),
        (arrow_x - 4, start_y + arrow_length_v - 6),
        (arrow_x + 4, start_y + arrow_length_v - 6)
    ], fill='blue')

    vertical_text = "Вік"

    # Рахуємо точні розміри тексту
    bbox = font_small.getbbox(vertical_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Створюємо тимчасове зображення під текст з запасом
    temp_img = Image.new('RGBA', (text_width + 15, text_height + 15), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    # Малюємо текст (зміщення на 5 пікселів, щоб не зрізався при повороті)
    temp_draw.text((5, 5), vertical_text, fill='blue', font=font)

    # Повертаємо на 90 градусів і враховуємо expand=True
    rotated_text_img = temp_img.rotate(90, expand=True)

    # Вставляємо повернуте зображення на основне (з врахуванням прозорості)
    img.paste(rotated_text_img, (10, 70), rotated_text_img)  # третій аргумент — прозорість

    output_path = "life_table.png"
    img.save(output_path)
    return output_path
