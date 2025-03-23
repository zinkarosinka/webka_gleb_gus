import json
import re
from transliterate import translit
from datetime import datetime


def generate_slug(name):
    # Транслитерация и очистка
    slug = translit(name, 'ru', reversed=True)
    slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
    return re.sub(r'[-\s]+', '-', slug)


def parse_products(text):
    products = []
    current_product = {}
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if re.match(r'^\d+\.$', line):
            if current_product:
                products.append(current_product)
                current_product = {}
        elif 'ГЛЕБ ГУСАРОВ' in line:
            current_product['name'] = line.split('ГЛЕБ ГУСАРОВ')[-1].strip()
        elif line.startswith('·'):
            if 'features' not in current_product:
                current_product['features'] = []
            current_product['features'].append(line[1:].strip())
        elif 'Цвет поставщика:' in line:
            current_product['color'] = line.split(': ')[-1].strip()
        elif 'Основной материал:' in line:
            current_product['material'] = line.split(': ')[-1].strip()
        elif 'Место производства:' in line:
            current_product['manufacture'] = line.split(': ')[-1].strip()

    if current_product:
        products.append(current_product)
    return products


def create_json_data(products):
    base_date = datetime(2023, 10, 15)
    return [
        {
            "model": "catalog.product",
            "pk": idx + 1,  # Начинаем с 1, т.к. категории уже есть
            "fields": {
                "category": 2,
                "name": product['name'],
                "slug": generate_slug(product['name']),
                "description": "\n".join([
                    "Особенности:",
                    *[f"- {feat}" for feat in product.get('features', [])],
                    f"Цвет: {product.get('color', '')}",
                    f"Состав: {product.get('material', '')}",
                    f"Производство: {product.get('manufacture', '')}"
                ]),
                "price": "0.00",  # Заменить на реальные значения
                "image": f"products/{base_date.strftime('%Y/%m/%d')}/{generate_slug(product['name'])}.jpg",
                "available": True,
                "stock": 10,
                "created": base_date.isoformat(),
                "updated": base_date.isoformat()
            }
        } for idx, product in enumerate(products)
    ]


# Чтение данных из файла
with open('catlop.txt', 'r', encoding='utf-8') as f:
    text_data = f.read()

# Парсинг и генерация данных
parsed_products = parse_products(text_data)
result_json = [
    # Категории
    {
        "model": "catalog.category",
        "pk": 1,
        "fields": {
            "name": "Электроника",
            "slug": "elektronika"
        }
    },
    {
        "model": "catalog.category",
        "pk": 2,
        "fields": {
            "name": "Одежда",
            "slug": "odezhda"
        }
    },
    *create_json_data(parsed_products)
]

# Сохранение в файл
with open('catalog_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(result_json, f, ensure_ascii=False, indent=4)

print("JSON успешно сгенерирован в файле catalog_fixture.json")