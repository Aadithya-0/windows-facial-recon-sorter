import flet as ft
import main as backend
import threading
import os
from tkinter import Tk, filedialog

# --- Color palette ---
BG_COLOR = "#0F1923"
SURFACE_COLOR = "#1A2634"
CARD_COLOR = "#223344"
ACCENT = "#4FC3F7"
ACCENT_DARK = "#0288D1"
TEXT_PRIMARY = "#ECEFF1"
TEXT_SECONDARY = "#90A4AE"
BORDER_SUBTLE = "#2E4057"
SUCCESS = "#66BB6A"
ERROR = "#EF5350"


def main(page: ft.Page):
    page.title = "FaceSort AI"
    page.bgcolor = BG_COLOR
    page.window.width = 1050
    page.window.height = 820
    page.padding = 30
    page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"}
    page.theme = ft.Theme(font_family="Inter")

    # ── Reusable widgets ──
    folder_input = ft.TextField(
        hint_text="Paste folder path or click Browse",
        hint_style=ft.TextStyle(color=TEXT_SECONDARY),
        width=480,
        border_color=BORDER_SUBTLE,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        cursor_color=ACCENT,
        text_size=14,
        height=48,
        border_radius=10,
        bgcolor=SURFACE_COLOR,
    )

    status_text = ft.Text("", color=TEXT_SECONDARY, size=13)
    progress_label = ft.Text("", color=TEXT_SECONDARY, size=12)
    progress_bar = ft.ProgressBar(width=480, visible=False, color=ACCENT, bgcolor=BORDER_SUBTLE)

    # ── Gallery view (all photos for one person) ──
    def show_person_photos(person_name, person_path, output_folder):
        page.clean()

        images = [f for f in os.listdir(person_path)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        def go_back(e):
            show_results(output_folder)

        photo_grid = ft.GridView(
            expand=1,
            runs_count=4,
            max_extent=240,
            child_aspect_ratio=1.0,
            spacing=16,
            run_spacing=16,
        )

        for img_name in images:
            img_path = os.path.join(person_path, img_name)
            photo_card = ft.Container(
                border_radius=14,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                bgcolor=CARD_COLOR,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=12,
                    color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
                content=ft.Image(
                    src=img_path,
                    fit="cover",
                    expand=True,
                ),
            )
            photo_grid.controls.append(photo_card)

        header = ft.Container(
            padding=ft.padding.only(bottom=12),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_ROUNDED,
                        icon_color=ACCENT,
                        icon_size=26,
                        on_click=go_back,
                        tooltip="Back",
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            bgcolor=SURFACE_COLOR,
                        ),
                    ),
                    ft.Container(width=8),
                    ft.Text(person_name, size=26, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                    ft.Container(width=6),
                    ft.Container(
                        bgcolor=ACCENT_DARK,
                        border_radius=12,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        content=ft.Text(f"{len(images)} photos", size=12, color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.W_600),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        page.add(ft.Column(expand=True, spacing=0, controls=[header, photo_grid]))
        page.update()

    # ── Results grid (all detected faces) ──
    def show_results(output_folder):
        page.clean()

        results_grid = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=180,
            child_aspect_ratio=0.82,
            spacing=20,
            run_spacing=24,
        )

        if not os.path.exists(output_folder):
            page.add(ft.Text("Output folder not found.", color=ERROR))
            page.update()
            return

        for person_name in sorted(os.listdir(output_folder)):
            person_path = os.path.join(output_folder, person_name)
            if not os.path.isdir(person_path):
                continue

            images = [f for f in os.listdir(person_path)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            if not images:
                continue

            thumb_path = os.path.join(person_path, images[0])

            name_field = ft.TextField(
                value=person_name,
                text_align=ft.TextAlign.CENTER,
                dense=True,
                border=ft.InputBorder.NONE,
                content_padding=ft.padding.symmetric(horizontal=6, vertical=4),
                text_size=13,
                color=TEXT_PRIMARY,
                cursor_color=ACCENT,
                text_style=ft.TextStyle(weight=ft.FontWeight.W_600),
            )

            def save_name(e, old_path=person_path, tf=name_field, old_name=person_name):
                new_name = tf.value.strip()
                new_path = os.path.join(output_folder, new_name)
                if new_name and new_name != old_name:
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        tf.focused_border_color = SUCCESS
                        page.update()
                    else:
                        tf.error_text = "Name taken"
                        page.update()

            name_field.on_submit = save_name

            def on_thumb_click(e, pname=person_name, ppath=person_path):
                show_person_photos(pname, ppath, output_folder)

            # ── Profile card ──
            profile_card = ft.Container(
                bgcolor=CARD_COLOR,
                border_radius=16,
                padding=ft.padding.only(top=18, bottom=10, left=10, right=10),
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=14,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
                content=ft.Column(
                    controls=[
                        # Circular avatar
                        ft.Container(
                            width=90,
                            height=90,
                            border_radius=45,
                            border=ft.Border.all(3, ACCENT),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            on_click=on_thumb_click,
                            ink=True,
                            tooltip=f"View all photos",
                            shadow=ft.BoxShadow(
                                spread_radius=0, blur_radius=10,
                                color=ft.Colors.with_opacity(0.25, ACCENT),
                                offset=ft.Offset(0, 0),
                            ),
                            content=ft.Image(
                                src=thumb_path,
                                width=90,
                                height=90,
                                fit="cover",
                            ),
                        ),
                        ft.Container(height=8),
                        # Name label
                        name_field,
                        # Photo count badge
                        ft.Text(
                            f"{len(images)} photo{'s' if len(images) != 1 else ''}",
                            size=11,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
            )
            results_grid.controls.append(profile_card)

        # Header bar
        header = ft.Container(
            padding=ft.padding.only(bottom=16),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Faces Found", size=28, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                    ft.Text("Click a face to view all photos  ·  Edit names inline, press Enter to save",
                            size=13, color=TEXT_SECONDARY),
                ],
            ),
        )

        page.add(ft.Column(expand=True, spacing=0, controls=[header, results_grid]))
        page.update()

    # ── Browse folder ──
    def browse_folder(e):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        root.destroy()
        if folder_path:
            folder_input.value = folder_path
            start_btn.disabled = False
            start_btn.opacity = 1.0
            page.update()

    browse_btn = ft.ElevatedButton(
        "Browse",
        icon=ft.Icons.FOLDER_OPEN_ROUNDED,
        width=120,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=SURFACE_COLOR,
            color=TEXT_PRIMARY,
            side=ft.BorderSide(1, BORDER_SUBTLE),
        ),
        on_click=browse_folder,
    )

    def on_folder_input_change(e):
        has_text = bool(folder_input.value and folder_input.value.strip())
        start_btn.disabled = not has_text
        start_btn.opacity = 1.0 if has_text else 0.4
        page.update()

    folder_input.on_change = on_folder_input_change

    # ── Processing ──
    def start_processing(e):
        folder_path = folder_input.value.strip()
        if not folder_path:
            status_text.value = "Please enter a folder path"
            status_text.color = ERROR
            page.update()
            return
        if not os.path.exists(folder_path):
            status_text.value = f"Folder not found: {folder_path}"
            status_text.color = ERROR
            page.update()
            return

        start_btn.disabled = True
        start_btn.opacity = 0.4
        folder_input.disabled = True
        progress_bar.visible = True
        progress_label.visible = True
        progress_bar.value = 0
        status_text.value = "Scanning for images…"
        status_text.color = ACCENT
        page.update()

        def progress_callback(done, total, filename, skipped):
            pct = done / total if total else 0
            progress_bar.value = pct
            short_name = filename if len(filename) <= 30 else filename[:27] + "…"
            tag = "cached" if skipped else "processing"
            progress_label.value = f"{done}/{total}  ·  {tag}: {short_name}"
            status_text.value = f"Processing images… {int(pct * 100)}%"
            page.update()

        def run_backend():
            try:
                output_folder = backend.process_folder(folder_path, progress_callback)
                status_text.value = "Done! Loading results…"
                status_text.color = SUCCESS
                progress_label.value = ""
                page.update()
                show_results(output_folder)
            except Exception as ex:
                import traceback
                traceback.print_exc()
                status_text.value = f"Error: {ex}"
                status_text.color = ERROR
                start_btn.disabled = False
                start_btn.opacity = 1.0
                folder_input.disabled = False
                progress_bar.visible = False
                progress_label.visible = False
                page.update()

        page.run_thread(run_backend)

    start_btn = ft.ElevatedButton(
        "Start Sorting",
        icon=ft.Icons.AUTO_AWESOME_ROUNDED,
        disabled=True,
        opacity=0.4,
        width=200,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ACCENT_DARK,
            color="#FFFFFF",
        ),
        on_click=start_processing,
    )

    # ── Landing page ──
    landing = ft.Column(
        controls=[
            ft.Container(height=40),
            ft.Text("FaceSort AI", size=48, weight=ft.FontWeight.W_700, color=ACCENT),
            ft.Container(height=6),
            ft.Text("Organize your memories by face", size=20, color=TEXT_SECONDARY),
            ft.Container(height=50),
            ft.Container(
                bgcolor=SURFACE_COLOR,
                border_radius=16,
                padding=40,
                width=660,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=20,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(0, 6),
                ),
                content=ft.Column(
                    controls=[
                        ft.Text("Select a folder", size=16, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                        ft.Container(height=12),
                        ft.Row(
                            controls=[folder_input, browse_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                        ),
                        ft.Container(height=14),
                        status_text,
                        progress_bar,
                        progress_label,
                        ft.Container(height=18),
                        ft.Row(
                            controls=[start_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    page.add(landing)


ft.app(target=main)