"""
╔══════════════════════════════════════════════════════════╗
║              STARK FEED — ChromeCraft Edition            ║
║          Blunt. Raw. AI-Driven Niche Intelligence.       ║
╚══════════════════════════════════════════════════════════╝

Run:
  pip install flet newsdataapi google-genai
  flet run main.py
"""

import flet as ft
import os
import asyncio
import threading

# ─────────────────────────────────────────────
#  API KEYS
# ─────────────────────────────────────────────
NEWS_API_KEY   = "pub_2accc5bc0fb54304b04a7c3e5854b8e0"
GEMINI_API_KEY = "AIzaSyDpHFzie2cdpjzVctq6D3Lq3K1q-0yk35s"

# ─────────────────────────────────────────────
#  APP ICON PLACEHOLDER
#  Drop your icon into assets/ folder
# ─────────────────────────────────────────────
APP_ICON_PATH = "assets/stark_icon.png"

# ─────────────────────────────────────────────
#  DEFAULT NICHES
# ─────────────────────────────────────────────
DEFAULT_NICHES = [
    "AI", "Fintech", "Indian Startups",
    "Crypto", "Electric Vehicles", "Space Tech",
    "Cybersecurity", "Biotech",
]

# ─────────────────────────────────────────────
#  CHROMECRAFT PALETTE
# ─────────────────────────────────────────────
BG_DEEP      = "#0b0f14"
BG_CARD      = "#1a1f2e"
BG_INPUT     = "#12161f"
ACCENT_CYAN  = "#00ffcc"
ACCENT_BLUE  = "#00ccff"
ACCENT_MID   = "#00e5e5"
TEXT_PRIMARY = "#e8f0fe"
TEXT_MUTED   = "#6b7a99"
TEXT_DIM     = "#3d4a6b"
CHIP_ACTIVE  = "#00ffcc"
CHIP_IDLE    = "#1e2a3d"
DANGER       = "#ff4d6d"

# ─────────────────────────────────────────────
#  GEMINI ANALYST PERSONA PROMPT
# ─────────────────────────────────────────────
ANALYST_PROMPT = """
You are STARK — a blunt, no-BS senior business analyst with 20 years of experience.
You don't soften bad news. You call trends early and are brutally honest.

Given the following news headlines and summaries about "{niche}", write a sharp intelligence brief.

Your output MUST follow this exact structure with these three headers:

**The Reality**
[2-3 sentences. What is actually happening right now, cutting through the noise.]

**The Impact**
[2-3 sentences. Who wins, who loses. What changes in the next 6-12 months.]

**The Move**
[1-2 sentences. The single most important action a smart operator should take right now.]

--- NEWS INPUT ---
{articles}
---

Be concise. Be direct. No fluff. No disclaimers.
"""


# ══════════════════════════════════════════════
#  FETCH NEWS
# ══════════════════════════════════════════════
def fetch_news(niche: str) -> list[dict]:
    try:
        from newsdataapi import NewsDataApiClient
    except ImportError:
        raise ImportError("Run: pip install newsdataapi")

    client = NewsDataApiClient(apikey=NEWS_API_KEY)
    response = client.news_api(q=niche, language="en", size=5)

    articles = []
    results = response.get("results") or []
    for item in results:
        articles.append({
            "title":       item.get("title", "No title"),
            "description": item.get("description") or item.get("content") or "",
            "link":        item.get("link", ""),
        })
    return articles


# ══════════════════════════════════════════════
#  GENERATE AI SUMMARY
# ══════════════════════════════════════════════
def generate_summary(niche: str, articles: list[dict]) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("Run: pip install google-genai")

    article_block = ""
    for i, art in enumerate(articles, 1):
        article_block += (
            f"{i}. {art['title']}\n"
            f"   {art['description'][:300]}\n\n"
        )

    prompt = ANALYST_PROMPT.format(niche=niche, articles=article_block)

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=600,
        ),
    )
    return response.text.strip()


# ══════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════
def loading_ring() -> ft.Column:
    return ft.Column(
        [
            ft.ProgressRing(color=ACCENT_CYAN, width=36, height=36, stroke_width=3),
            ft.Text("Pulling intel...", size=12, color=TEXT_MUTED,
                    font_family="Space Grotesk"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
    )


# ══════════════════════════════════════════════
#  SUMMARY CARD
# ══════════════════════════════════════════════
def build_summary_card(niche: str, summary_text: str, page: ft.Page) -> ft.Container:

    def copy_clicked(e):
        page.set_clipboard(summary_text)
        snack = ft.SnackBar(
            content=ft.Text("📋 Copied to clipboard", color=BG_DEEP,
                            font_family="Space Grotesk"),
            bgcolor=ACCENT_CYAN,
            duration=2000,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # Parse sections
    sections = []
    current_header = None
    current_body_lines = []
    section_icons = {
        "The Reality": "📡",
        "The Impact":  "⚡",
        "The Move":    "🎯",
    }
    section_colors = {
        "The Reality": ACCENT_CYAN,
        "The Impact":  ACCENT_BLUE,
        "The Move":    "#ff9f43",
    }

    for line in summary_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("**") and stripped.endswith("**"):
            if current_header:
                sections.append((current_header, " ".join(current_body_lines).strip()))
            current_header = stripped.strip("*").strip()
            current_body_lines = []
        elif stripped:
            current_body_lines.append(stripped)

    if current_header:
        sections.append((current_header, " ".join(current_body_lines).strip()))

    if not sections:
        sections = [("Brief", summary_text)]

    section_widgets = []
    for header, content in sections:
        icon  = section_icons.get(header, "•")
        color = section_colors.get(header, ACCENT_CYAN)

        section_widgets.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(icon, size=14),
                                ft.Text(
                                    header.upper(),
                                    size=11,
                                    weight=ft.FontWeight.W_700,
                                    color=color,
                                    font_family="Orbitron",
                                    letter_spacing=1.5,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text(
                                content,
                                size=13,
                                color=TEXT_PRIMARY,
                                font_family="Space Grotesk",
                                selectable=True,
                            ),
                            padding=ft.padding.only(left=4, top=4),
                        ),
                    ],
                    spacing=6,
                ),
                padding=ft.padding.symmetric(vertical=10, horizontal=4),
            )
        )
        section_widgets.append(
            ft.Divider(height=1, color=TEXT_DIM, thickness=0.4)
        )

    if section_widgets:
        section_widgets.pop()

    card_content = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            niche.upper(),
                            size=10,
                            color=BG_DEEP,
                            weight=ft.FontWeight.W_700,
                            font_family="Orbitron",
                            letter_spacing=1.8,
                        ),
                        bgcolor=ACCENT_CYAN,
                        border_radius=4,
                        padding=ft.padding.symmetric(vertical=3, horizontal=8),
                    ),
                    ft.Text(
                        "STARK ANALYSIS",
                        size=10,
                        color=TEXT_MUTED,
                        font_family="Orbitron",
                        letter_spacing=1.2,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CONTENT_COPY_ROUNDED,
                        icon_color=TEXT_MUTED,
                        icon_size=16,
                        tooltip="Copy to clipboard",
                        on_click=copy_clicked,
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.with_opacity(0.08, ACCENT_CYAN),
                        ),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Divider(height=1, color=TEXT_DIM, thickness=0.5),
            ft.Container(height=4),
            *section_widgets,
        ],
        spacing=0,
    )

    return ft.Container(
        content=card_content,
        bgcolor=BG_CARD,
        border_radius=16,
        padding=ft.padding.symmetric(vertical=16, horizontal=18),
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, ACCENT_CYAN)),
        shadow=ft.BoxShadow(
            blur_radius=24,
            color=ft.Colors.with_opacity(0.12, ACCENT_CYAN),
            offset=ft.Offset(0, 4),
        ),
        margin=ft.margin.symmetric(vertical=8),
    )


def build_error_card(message: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=DANGER, size=18),
                        ft.Text(
                            "ERROR",
                            size=11,
                            color=DANGER,
                            weight=ft.FontWeight.W_700,
                            font_family="Orbitron",
                            letter_spacing=1.5,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                ft.Text(message, color="#ff8fa3", selectable=True,
                        font_family="Space Grotesk", size=13),
            ]
        ),
        bgcolor=ft.Colors.with_opacity(0.06, DANGER),
        border_radius=12,
        padding=ft.padding.all(16),
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, DANGER)),
        margin=ft.margin.symmetric(vertical=8),
    )


# ══════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════
def main(page: ft.Page):
    page.title      = "STARK Feed"
    page.bgcolor    = BG_DEEP
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts      = {
        "Orbitron":      "https://fonts.gstatic.com/s/orbitron/v31/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nysimBoWgz.woff2",
        "Space Grotesk": "https://fonts.gstatic.com/s/spacegrotesk/v16/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gowFXDfPvr_TB20.woff2",
    }
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ACCENT_CYAN,
            secondary=ACCENT_BLUE,
            surface=BG_CARD,
            background=BG_DEEP,
        ),
    )
    page.window.width  = 420
    page.window.height = 860

    # State
    storage_key = "stark_niches"
    active_niche = ft.Ref[str]()
    active_niche.current = DEFAULT_NICHES[0]

    def load_niches() -> list[str]:
        try:
            stored = page.client_storage.get(storage_key)
            if stored and isinstance(stored, list) and len(stored) > 0:
                return stored
        except Exception:
            pass
        return DEFAULT_NICHES.copy()

    def save_niches(niches: list[str]):
        try:
            page.client_storage.set(storage_key, niches)
        except Exception:
            pass

    niches: list[str] = load_niches()

    niche_row_ref    = ft.Ref[ft.Row]()
    result_col_ref   = ft.Ref[ft.Column]()
    search_field_ref = ft.Ref[ft.TextField]()
    add_dialog_ref   = ft.Ref[ft.AlertDialog]()

    # ── Niche Chip ──────────────────────────────
    def build_chip(label: str, active: bool = False) -> ft.GestureDetector:
        def on_tap(e):
            active_niche.current = label
            refresh_chips()
            run_analysis(label)

        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Text(
                    label,
                    size=11,
                    color=BG_DEEP if active else TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                    font_family="Space Grotesk",
                    no_wrap=True,
                ),
                bgcolor=CHIP_ACTIVE if active else CHIP_IDLE,
                border_radius=20,
                padding=ft.padding.symmetric(vertical=7, horizontal=14),
                border=ft.border.all(1, ACCENT_CYAN if active else TEXT_DIM),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            ),
            on_tap=on_tap,
        )

    def refresh_chips():
        if niche_row_ref.current:
            niche_row_ref.current.controls = [
                build_chip(n, active=(n == active_niche.current))
                for n in niches
            ]
            page.update()

    # ── Analysis Runner ─────────────────────────
    def set_result(widget):
        if result_col_ref.current:
            result_col_ref.current.controls = [widget]
            page.update()

    def run_analysis(niche: str):
        set_result(
            ft.Container(
                content=loading_ring(),
                alignment=ft.alignment.center,
                height=180,
            )
        )

        def worker():
            try:
                articles = fetch_news(niche)
                if not articles:
                    set_result(build_error_card(
                        f"No articles found for '{niche}'. Try a different term."
                    ))
                    return
                summary = generate_summary(niche, articles)
                set_result(build_summary_card(niche, summary, page))
            except Exception as ex:
                set_result(build_error_card(f"{type(ex).__name__}: {ex}"))

        threading.Thread(target=worker, daemon=True).start()

    # ── Add Niche Dialog ────────────────────────
    def close_dialog(e=None):
        add_dialog_ref.current.open = False
        page.update()

    def add_niche(e=None):
        val = (search_field_ref.current.value or "").strip()
        if val and val not in niches:
            niches.append(val)
            save_niches(niches)
            active_niche.current = val
            refresh_chips()
            run_analysis(val)
        close_dialog()
        if search_field_ref.current:
            search_field_ref.current.value = ""

    add_dialog = ft.AlertDialog(
        ref=add_dialog_ref,
        modal=True,
        bgcolor=BG_CARD,
        shape=ft.RoundedRectangleBorder(radius=16),
        title=ft.Text(
            "ADD NICHE",
            size=13,
            color=ACCENT_CYAN,
            font_family="Orbitron",
            letter_spacing=2,
            weight=ft.FontWeight.W_700,
        ),
        content=ft.Container(
            content=ft.TextField(
                ref=search_field_ref,
                hint_text="e.g. Quantum Computing",
                hint_style=ft.TextStyle(color=TEXT_MUTED, font_family="Space Grotesk"),
                text_style=ft.TextStyle(color=TEXT_PRIMARY, font_family="Space Grotesk"),
                bgcolor=BG_INPUT,
                border_color=TEXT_DIM,
                focused_border_color=ACCENT_CYAN,
                cursor_color=ACCENT_CYAN,
                border_radius=10,
                on_submit=add_niche,
            ),
            width=260,
            padding=ft.padding.only(top=8),
        ),
        actions=[
            ft.TextButton(
                "CANCEL",
                style=ft.ButtonStyle(color=TEXT_MUTED),
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "ADD",
                bgcolor=ACCENT_CYAN,
                color=BG_DEEP,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    text_style=ft.TextStyle(
                        font_family="Orbitron",
                        weight=ft.FontWeight.W_700,
                        letter_spacing=1.5,
                    ),
                ),
                on_click=add_niche,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(add_dialog)

    def open_add_dialog(e):
        add_dialog_ref.current.open = True
        page.update()

    # ── Header ──────────────────────────────────
    header = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Text("⚡", size=22),
                    width=36, height=36,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.12, ACCENT_CYAN),
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    [
                        ft.Text(
                            "STARK FEED",
                            size=18,
                            weight=ft.FontWeight.W_900,
                            color=ACCENT_CYAN,
                            font_family="Orbitron",
                            letter_spacing=3,
                        ),
                        ft.Text(
                            "CHROMECRAFT INTELLIGENCE",
                            size=8,
                            color=TEXT_MUTED,
                            font_family="Orbitron",
                            letter_spacing=2.5,
                        ),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                    icon_color=ACCENT_CYAN,
                    icon_size=24,
                    tooltip="Add niche",
                    on_click=open_add_dialog,
                    style=ft.ButtonStyle(
                        overlay_color=ft.Colors.with_opacity(0.08, ACCENT_CYAN),
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=ft.padding.only(left=18, right=10, top=52, bottom=12),
        bgcolor=ft.Colors.with_opacity(0.6, BG_CARD),
        border=ft.border.only(
            bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.15, ACCENT_CYAN))
        ),
    )

    # ── Niche Bar ───────────────────────────────
    niche_scroll = ft.Container(
        content=ft.Row(
            ref=niche_row_ref,
            controls=[
                build_chip(n, active=(n == active_niche.current))
                for n in niches
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(vertical=12, horizontal=16),
        bgcolor=ft.Colors.with_opacity(0.3, BG_CARD),
        border=ft.border.only(
            bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.1, ACCENT_CYAN))
        ),
    )

    # ── Result Area ─────────────────────────────
    idle_placeholder = ft.Container(
        content=ft.Column(
            [
                ft.Text("◈", size=40, color=TEXT_DIM),
                ft.Container(height=8),
                ft.Text(
                    "SELECT A NICHE",
                    size=11,
                    color=TEXT_DIM,
                    font_family="Orbitron",
                    letter_spacing=2,
                ),
                ft.Text(
                    "Tap a chip above to pull\nreal-time AI intelligence",
                    size=12,
                    color=TEXT_MUTED,
                    font_family="Space Grotesk",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    result_column = ft.Column(
        ref=result_col_ref,
        controls=[idle_placeholder],
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        expand=True,
    )

    result_area = ft.Container(
        content=result_column,
        expand=True,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

    # ── Status Bar ──────────────────────────────
    status_bar = ft.Container(
        content=ft.Row(
            [
                ft.Container(width=6, height=6, bgcolor=ACCENT_CYAN, border_radius=3),
                ft.Text("LIVE", size=9, color=ACCENT_CYAN,
                        font_family="Orbitron", letter_spacing=1.5),
                ft.Text("  ·  Powered by Gemini 1.5 Flash + NewsData.io",
                        size=9, color=TEXT_DIM, font_family="Space Grotesk"),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
        padding=ft.padding.symmetric(horizontal=18, vertical=8),
        bgcolor=ft.Colors.with_opacity(0.4, BG_CARD),
        border=ft.border.only(
            top=ft.BorderSide(1, ft.Colors.with_opacity(0.1, ACCENT_CYAN))
        ),
    )

    # ── Layout ──────────────────────────────────
    page.add(
        ft.Column(
            [header, niche_scroll, result_area, status_bar],
            spacing=0,
            expand=True,
        )
    )

    run_analysis(active_niche.current)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
