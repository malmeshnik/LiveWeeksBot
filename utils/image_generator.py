from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def calculate_lived_weeks(birth_date, gender):
    """
    Розрахувати кількість прожитих тижнів та залишок
    """
    today = datetime.now().date()
    lived_days = (today - birth_date).days
    lived_weeks = lived_days // 7
    
    # Визначаємо загальну кількість тижнів залежно від статі
    total_weeks = 3744 if gender == 'female' else 3432  # 72*52 або 66*52
    
    return lived_weeks, total_weeks - lived_weeks

def generate_life_table(birth_date, gender):
    """
    Генерує зображення таблиці життя
    """
    lived_weeks, remaining_weeks = calculate_lived_weeks(birth_date, gender)
    
    # Розміри таблиці
    cell_size = 15
    cells_per_row = 52
    rows = 72 if gender == 'female' else 66
    
    # Створюємо зображення з потрібними розмірами
    width = cells_per_row * cell_size + 50  # додатковий простір для номерів років
    height = rows * cell_size + 30  # додатковий простір для заголовка
    
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Завантажуємо шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
    
    # Малюємо заголовок
    title = "Таблиця життя" + (" (Жінка - 72 роки)" if gender == 'female' else " (Чоловік - 66 років)")
    draw.text((width//2 - 100, 5), title, fill='black', font=font)
    
    # Малюємо клітинки
    week_count = 0
    for row in range(rows):
        # Номер року зліва
        draw.text((5, row * cell_size + 30), str(row + 1), fill='black', font=font)
        
        for col in range(cells_per_row):
            x = col * cell_size + 50
            y = row * cell_size + 30
            
            if week_count < lived_weeks:
                # Прожиті тижні - червоні
                fill_color = 'red'
            else:
                # Майбутні тижні - сірі
                fill_color = 'lightgrey'
                
            # Малюємо клітинку
            draw.rectangle([(x, y), (x + cell_size - 1, y + cell_size - 1)], 
                          outline='black', fill=fill_color)
            week_count += 1
    
    # Зберігаємо файл
    file_path = f"life_table_{gender}.png"
    img.save(file_path)
    return file_path