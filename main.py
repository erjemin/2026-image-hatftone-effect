import sys

from PIL import Image


def encode_to_base36(num):
    """Кодирует число в base-36: 0-9, A-Z, a-z"""
    if num < 0:
        raise ValueError("Number must be non-negative")
    
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    if num < len(charset):
        return charset[num]
    
    result = []
    while num > 0:
        result.append(charset[num % len(charset)])
        num //= len(charset)
    return ''.join(reversed(result))


def generate_halftone_svg(image_path, output_path, cols=80, max_radius=6, animation_variants=12):
    import random

    img = Image.open(image_path).convert('L')
    aspect_ratio = img.height / img.width
    rows = int(cols * aspect_ratio)
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)

    step = max_radius * 2 + 2
    width = cols * step
    height = rows * step

    svg_elements = []

    # Генерируем CSS-классы для разных задержек
    animation_classes = []
    for i in range(animation_variants):
        delay = (i / animation_variants) * 3
        encoded_i = encode_to_base36(i)
        animation_classes.append(f".a{encoded_i}{{--d:{delay:.2f}s}}")

    for y in range(rows):
        for x in range(cols):
            brightness = img_resized.getpixel((x, y))
            factor = (255 - brightness) / 255.0

            if factor < 0.15:
                continue

            radius = factor * max_radius
            cx = x * step + step // 2
            cy = y * step + step // 2

            # Каждой точке свой класс с уникальной задержкой
            anim_class = random.randint(0, animation_variants - 1)
            encoded_class = encode_to_base36(anim_class)
            svg_elements.append(
                f'<circle cx="{cx}" cy="{cy}" r="{int(radius)}" class="a{encoded_class}"/>'
            )

    animation_css = "".join(animation_classes)

    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%"><style>svg{{background:transparent}}circle{{fill:#80000090;transform-origin:center;animation:noise 1s ease-in-out infinite alternate;animation-delay:var(--d);transition:all 0.5s ease-out}} @keyframes noise{{0%{{opacity:0.7;transform:scale(1)}}50%{{opacity:1}}100%{{opacity:0.5;transform:scale(0.99)}}}} .frozen circle{{animation:none!important;opacity:1!important;transform:none!important}} {animation_css}</style><g id="dots">{"".join(svg_elements)}</g></svg>"""

    with open(output_path, 'w') as f:
        f.write(svg_template)
    print(f"SVG успешно сгенерирован: {output_path}")

if __name__ == '__main__':
    file_name_in = sys.argv[-1]
    generate_halftone_svg(file_name_in, f'{file_name_in.split(".")[0]}j.svg', cols=90, max_radius=5)
