import sys

from PIL import Image


def encode_to_base36(num: int) -> str:
    """Кодирует число в base-36: 0-9, A-Z, a-z"""
    if num < 0:
        raise ValueError("Number must be non-negative")
    
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    if num < len(charset):
        return charset[num]
    
    result = []
    while num > 0:
        result.append(charset[num % len(charset)])
        num //= len(charset)
    return ''.join(reversed(result))


def generate_halftone_svg(
        image_path: str,
        output_path: str,
        cols: int = 80,
        max_radius: int = 8,
        animation_variants: int = 12):
    '''Генерирует SVG с полутоновым эффектом из изображения.'''
    import random
    from collections import defaultdict

    img = Image.open(image_path).convert('L')
    aspect_ratio = img.height / img.width
    rows = int(cols * aspect_ratio)
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)

    step = max_radius * 2 + 2
    width = cols * step
    height = rows * step

    # Генерируем CSS-классы для разных задержек
    animation_classes = []
    for i in range(animation_variants):
        delay = (i / animation_variants) * 3
        encoded_i = encode_to_base36(i)
        # Убрать .0 для целых чисел: 1.0s → 1s
        if delay == int(delay):
            delay_str = f"{int(delay)}"
        else:
            delay_str = f"{delay:.1f}".lstrip('0')
        animation_classes.append(f".{encoded_i}{{--d:{delay_str}s}}")

    # Собираем элементы группируя по классам: {class: [(radius, cx, cy), ...]}
    elements_by_class = defaultdict(list)
    unique_radii = set()

    for y in range(rows):
        for x in range(cols):
            brightness = img_resized.getpixel((x, y))
            factor = (255 - brightness) / 255.0

            if factor < 0.15:
                continue

            radius = int(factor * max_radius)
            if radius == 0:
                continue
            
            cx = x * step + step // 2
            cy = y * step + step // 2

            anim_class = random.randint(0, animation_variants - 1)
            encoded_class = encode_to_base36(anim_class)
            
            elements_by_class[encoded_class].append((radius, cx, cy))
            unique_radii.add(radius)

    # Создаем <defs> с определениями кружков для каждого радиуса
    defs = '<defs>'
    for radius in sorted(unique_radii):
        encoded_radius = encode_to_base36(radius)
        defs += f'<circle id="{encoded_radius}" r="{radius}"/>'
    defs += '</defs>'

    # Создаем группы по классам
    groups = []
    for anim_class in sorted(elements_by_class.keys()):
        group_elements = elements_by_class[anim_class]
        uses = ''.join(
            f'<use href="#{encode_to_base36(radius)}" x="{cx}" y="{cy}"/>'
            for radius, cx, cy in group_elements
        )
        if uses:
            groups.append(f'<g class="{anim_class}">{uses}</g>')

    animation_css = "".join(animation_classes)
    groups_html = "".join(groups)

    svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%"><style>svg{{background:transparent}}circle{{fill:#80000090;transform-origin:center;animation:noise 1s ease-in-out infinite alternate;animation-delay:var(--d);transition:all .5s ease-out}} @keyframes noise{{0%{{opacity:.7;transform:scale(1)}}50%{{opacity:1}}100%{{opacity:.5;transform:scale(.995)}}}}.frozen circle{{animation:none!important;opacity:1!important;transform:none!important}}{animation_css}</style>{defs}<g id="dots">{groups_html}</g></svg>'''

    with open(output_path, 'w') as f:
        f.write(svg_template)
    print(f"SVG успешно сгенерирован: {output_path}")

if __name__ == '__main__':
    file_name_in = sys.argv[-1]
    generate_halftone_svg(file_name_in, f'{file_name_in.split(".")[0]}j.svg', cols=63, max_radius=7)
