# выделяем индексы еды, которую едят по несколько кусочков
from bot import update_daily_intake
from models import *
import torch
from dict import *
from models import load_models
model1, image_processor, model2, tokenizer2, model3, tokenizer3 = load_models()
portion_list=[0, 10, 100, 12, 14,17,20,21,25,29,31,46,6,63]



def calories(url):
  image = Image.open(requests.get(url, stream=True).raw)
  enc_image = model2.encode_image(image)

  inputs = image_processor(image, return_tensors="pt")
  with torch.no_grad():
      logits = model1(**inputs).logits

  predicted_label = logits.argmax(-1).item()

  #для категорий еды, которую едят по несколько кусочков делаем доп проверку
  coef=1
  if predicted_label in portion_list:
    prompt=f"how many {model1.config.id2label[predicted_label]} pieces are there in picture. Give me a number"
    num=model2.answer_question(enc_image, prompt, tokenizer2)
    try:
      coef=int(num)
    except ValueError:
      pass

  predicted_meal=rus_id2label[predicted_label]
  PFC=rus_label2cal[predicted_meal]
  reply=f'Скорее всего, вы едите {rus_id2label[predicted_label]}. В этом блюде {coef*PFC[0]} ккал, {coef*PFC[1]} грамм белков, {coef*PFC[2]} грамм жиров и {coef*PFC[3]} грамм углеводов.'

  return reply

def advice(url):
    image = Image.open(requests.get(url, stream=True).raw)
    enc_image = model2.encode_image(image)
    advice=(model2.answer_question(enc_image, "Act like nutriciolog. What additional elements could you recommend to balance out this meal? Please ensure that the suggested additions complement the existing meal.", tokenizer2))
    # Токенизация входного текста
    input_ids = tokenizer3(advice, return_tensors="pt").input_ids
    # Перевод текста
    outputs = model3.generate(input_ids)
    rus_advice = tokenizer3.decode(outputs[0], skip_special_tokens=True)

    return rus_advice

import re

def process_and_save_calories(user_id, today, url):
    """
    Обрабатывает изображение, извлекает данные о калориях и БЖУ,
    и сохраняет их в таблицу DailyIntake.
    """
    # Вызов функции `calories` для получения текста результата
    reply = calories(url)

    # Регулярное выражение для извлечения чисел из строки
    match = re.search(r'(\d+)\s*ккал.*?(\d+)\s*грамм белков.*?(\d+)\s*грамм жиров.*?(\d+)\s*грамм углеводов', reply)
    if match:
        calories_value = int(match.group(1))
        protein_value = int(match.group(2))
        fat_value = int(match.group(3))
        carbs_value = int(match.group(4))

        # Обновление данных в таблице `DailyIntake`
        update_daily_intake(user_id, today, calories_value, protein_value, fat_value, carbs_value)

        return f"Данные добавлены:\nКалории: {calories_value}, Белки: {protein_value}, Жиры: {fat_value}, Углеводы: {carbs_value}"
    else:
        return "Не удалось распознать данные о калориях и БЖУ. Попробуйте снова."


from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def create_progress_image(max_cal, max_prot, max_fat, max_carb,
                          curr_cal, curr_prot, curr_fat, curr_carb):
    # Размер изображения
    width, height = 600, 400

    # Загрузка фонового изображения
    try:
        response = requests.get("https://www.helpguide.org/wp-content/uploads/2023/02/Choosing-Healthy-Fats.jpeg")
        background_img = Image.open(BytesIO(response.content)).convert("RGB")
        background_img = background_img.resize((width, height))
    except Exception as e:
        raise RuntimeError(f"Error loading background image: {e}")

    # Создание нового изображения поверх фона
    img = background_img.copy()
    draw = ImageDraw.Draw(img)

    # Подключение шрифта с поддержкой кириллицы
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size=148)  # Увеличение размера шрифта
    except IOError:
        try:
            # Альтернативный вариант: скачать шрифт из сети
            response = requests.get("https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf")
            font = ImageFont.truetype(BytesIO(response.content), size=148, encoding='UTF-8')
        except Exception:
            # Если ничего не получилось, используем стандартный шрифт
            font = ImageFont.load_default()

    # Рисуем текст "Your Progress" сверху по центру
    draw.text((width // 2-100, 10), "Your Progress", font=ImageFont.load_default(size=30), fill=(255, 0, 0))

    # Цвета и прогресс-бары
    bar_color = (0, 0, 255)  # Синий для прогресса
    background_color = (211, 211, 211)  # Серый для фона баров

    # Коэффициенты для прогресса
    def calc_width(current, maximum):
        return int((current / maximum) * (width - 50)) if maximum > 0 else 0

    # Прогресс-бары
    bars = [
        ("Calories", curr_cal, max_cal),
        ("Protein", curr_prot, max_prot),
        ("Fat", curr_fat, max_fat),
        ("Carbs", curr_carb, max_carb)
    ]
    y_offset = 100
    for label, current, maximum in bars:
        draw.text((20, y_offset - 20), f"{label}: {current}/{maximum}", font=font, fill=(0, 0, 0))
        draw.rectangle([20, y_offset, width - 20, y_offset + 30], fill=background_color)
        draw.rectangle([20, y_offset, 20 + calc_width(current, maximum), y_offset + 30], fill=bar_color)
        y_offset += 60

    # Сохранение изображения
    image_path = "progress.png"
    img.save(image_path)
    return image_path
