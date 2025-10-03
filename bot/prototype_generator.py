import os
import requests
import logging
import yaml
from playwright.sync_api import sync_playwright

from config import OUTPUT_DIR, SERVER_URL

logger = logging.getLogger(__name__)

# ---------- Загрузка prompts.yaml ----------
def load_prompts(path=None) -> dict:
    if path is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_dir, "prompts.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Не найден {path}.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

PROMPT_TEMPLATES = load_prompts()

# ---------- Конфигурация ----------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

# ---------- Сборка промпта ----------
def build_prompt(brief: dict) -> str:
    project_type = brief.get("project", "Generic")
    template = PROMPT_TEMPLATES.get(project_type)
    if not template:
        template = """
        Generate an HTML prototype.

        Requirements:
        - Project: {project}
        - Functions: {functions}
        - Audience: {audience}
        - Style: {style}

        Output only valid HTML + inline CSS.
        """
    return template.format(
        project=brief.get("project", "Untitled"),
        functions=", ".join(brief.get("functions", [])),
        audience=brief.get("audience", "—"),
        style=brief.get("style", "Minimal"),
    )

# ---------- Request to OpenRouter ----------
def generate_html_with_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a frontend developer. "
                    "Generate only valid HTML5 with inline CSS. "
                    "The entire interface (texts, buttons, menus, labels) must be strictly in Russian. "
                    "Do not include explanations, comments, Markdown, or LaTeX. "
                    "The output must start with <!DOCTYPE html><html> and end with </html>."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    try:
        logger.info(f"Sending request to OpenRouter (model={OPENROUTER_MODEL})...")
        logger.debug(f"Prompt:\n{prompt}")

        r = requests.post(url, headers=headers, json=data, timeout=120)
        r.raise_for_status()

        resp = r.json()
        # more robust parsing
        content = (
            resp.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
            or resp.get("choices", [{}])[0]
            .get("messages", [{}])[0]
            .get("content", "")
        )

        return content.strip()
    except Exception as e:
        logger.error(f"Error while calling OpenRouter API: {e}")
        return f"Generation error: {e}"


# ---------- Сохранение HTML ----------
def save_html(html: str, path="output/prototype.html"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(path)


def make_screenshot(html_path: str, screenshot_path="output/prototype.png"):
    """
    Создаёт PNG-скриншот страницы из локального HTML-файла.
    """
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])  # no-sandbox важно в Docker
        page = browser.new_page()
        # Открываем локальный HTML-файл
        page.goto(f"file://{html_path}")
        # Делаем скриншот всей страницы
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()

    return os.path.abspath(screenshot_path)


# ---------- Главная функция ----------
def generate_prototype(brief: dict):
    prompt = build_prompt(brief)
    html = generate_html_with_openrouter(prompt)

    # сохраняем html
    html_path = save_html(html, path=os.path.join(OUTPUT_DIR, "prototype.html"))
    png_path = make_screenshot(html_path, screenshot_path=os.path.join(OUTPUT_DIR, "prototype.png"))

    # --- Подстановка адреса ---
    # если SERVER_URL не задан в .env → подставляем localhost
    base_url = SERVER_URL or "http://localhost:8080"

    html_link = f"{base_url}/previews/{os.path.basename(html_path)}"
    png_link = f"{base_url}/previews/{os.path.basename(png_path)}"

    return {
        "html_path": html_path,
        "png_path": png_path,
        "html_link": html_link,
        "png_link": png_link,
    }
