import flet as ft
import main as backend
import threading
import os
from tkinter import Tk, filedialog

def main(page: ft.Page):
    page.title = "FaceSort AI"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.bgcolor = "#b0d1f2"
    page.window.width = 1000
    page.window.height = 800
    
    # TextField for folder path input
    folder_input = ft.TextField(
        hint_text="Click Browse or paste folder path here",
        width=500,
        border_color="#0B57D0",
        focused_border_color="#0B57D0",
        text_size=14,
        height=50,
    )
    
    status_text = ft.Text("", color="#333333", size=14)
    progress_bar = ft.ProgressBar(width=500, visible=False, color="#0B57D0")
    
    def show_results(output_folder):
        print(f"show_results called with: {output_folder}")
        # Clear page and show results
        page.clean()
        print("Page cleaned")
        
        results_grid = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=160,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=20,
        )
        
        if not os.path.exists(output_folder):
            print(f"Output folder doesn't exist: {output_folder}")
            page.add(ft.Text("Error: Output folder not found.", color="#E53935"))
            page.update()
            return
        
        print(f"Scanning folder: {output_folder}")
        folder_count = 0
        for person_name in os.listdir(output_folder):
            person_path = os.path.join(output_folder, person_name)
            if os.path.isdir(person_path):
                folder_count += 1
                print(f"Processing person folder: {person_name}")
                images = [f for f in os.listdir(person_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                print(f"  Found {len(images)} images")
                if not images:
                    continue
                    
                thumb_path = os.path.join(person_path, images[0])
                print(f"  Thumbnail: {thumb_path}")
                name_field = ft.TextField(
                    value=person_name,
                    text_align=ft.TextAlign.CENTER,
                    dense=True,
                    border=ft.InputBorder.UNDERLINE,
                    content_padding=5,
                    text_size=14
                )
                
                def save_name(e, old_path=person_path, tf=name_field, old_name=person_name):
                    new_name = tf.value.strip()
                    new_path = os.path.join(output_folder, new_name)
                    
                    if new_name and new_name != old_name:
                        if not os.path.exists(new_path):
                            os.rename(old_path, new_path)
                            tf.border_color = "#43A047"
                            page.update()
                            print(f"Renamed {old_name} to {new_name}")
                        else:
                            tf.error_text = "Name exists"
                            page.update()
                
                name_field.on_submit = save_name
                
                profile_card = ft.Column(
                    controls=[
                        ft.Container(
                            width=120,
                            height=120,
                            border_radius=60,
                            border=ft.Border.all(2, "#0B57D0"),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.Image(
                                src=thumb_path,
                                width=120,
                                height=120,
                            ),
                        ),
                        name_field
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
                results_grid.controls.append(profile_card)
        
        print(f"Total folders processed: {folder_count}")
        print(f"Grid controls count: {len(results_grid.controls)}")
        
        results_view = ft.Column(
            expand=True,
            controls=[
                ft.Text("Faces Found", size=30, weight=ft.FontWeight.BOLD, color="#0B57D0"),
                ft.Text("Click a name to edit, then press Enter to save.", size=14, color="#666666"),
                ft.Container(height=20),
                results_grid
            ]
        )
        
        page.add(results_view)
        print("Results view added to page")
        page.update()
        print("Page updated!")
    # Browse button using tkinter filedialog (more reliable)
    def browse_folder(e):
        # Hide the Tk root window
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
        width=100,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="#E3E8EF",
            color="#1A1C1E",
        ),
        on_click=browse_folder
    )
    
    def on_folder_input_change(e):
        # Enable start button if path is not empty
        if folder_input.value and folder_input.value.strip():
            start_btn.disabled = False
            start_btn.opacity = 1.0
        else:
            start_btn.disabled = True
            start_btn.opacity = 0.5
        page.update()
    
    folder_input.on_change = on_folder_input_change
    
    def start_processing(e):
        folder_path = folder_input.value.strip()
        
        if not folder_path:
            status_text.value = "Please enter a folder path"
            status_text.color = "#E53935"
            page.update()
            return
        
        if not os.path.exists(folder_path):
            status_text.value = f"Folder not found: {folder_path}"
            status_text.color = "#E53935"
            page.update()
            return
        
        # Disable UI during processing
        start_btn.disabled = True
        start_btn.opacity = 0.5
        folder_input.disabled = True
        progress_bar.visible = True
        progress_bar.value = 0
        status_text.value = "Processing images..."
        status_text.color = "#0B57D0"
        page.update()
        
        def progress_callback(progress_value):
            progress_bar.value = progress_value
            page.update()
        
        def run_backend():
            try:
                output_folder = backend.process_folder(folder_path, progress_callback)
                print(f"Backend complete. Output folder: {output_folder}")
                
                # Direct UI update (should work if Flet allows thread updates)
                status_text.value = f"✓ Done! Loading results..."
                status_text.color = "#43A047"
                page.update()
                
                print("About to show results...")
                # Show results grid
                show_results(output_folder)
                print("Results shown!")
                
            except Exception as ex:
                import traceback
                traceback.print_exc()
                status_text.value = f"Error: {str(ex)}"
                status_text.color = "#E53935"
                start_btn.disabled = False
                start_btn.opacity = 1.0
                folder_input.disabled = False
                progress_bar.visible = False
                page.update()
        
        # Run in background thread to avoid freezing UI
        thread = threading.Thread(target=run_backend, daemon=True)
        thread.start()
    
    start_btn = ft.ElevatedButton(
        "Start Sorting",
        disabled=True,
        opacity=0.5,
        width=200,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="#0B57D0",
            color="#FFFFFF",
        ),
        on_click=start_processing
    )
    
    # Create and add main column with all controls
    main_column = ft.Column(
        controls=[
            ft.Text("FaceSort AI", size=50, weight=ft.FontWeight.BOLD, color="#0B57D0"),
            ft.Container(height=20),
            ft.Text("Organize your memories", size=30, weight=ft.FontWeight.BOLD, color="#1A1C1E"),
            ft.Text("Select or paste the folder path containing your images.", size=16, color="#333333"),
            
            ft.Container(height=40),
            
            # Row with text field and browse button
            ft.Row(
                controls=[
                    folder_input,
                    browse_btn,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            
            ft.Container(height=10),
            status_text,
            progress_bar,
            
            ft.Container(height=20),
            start_btn
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )
    
    page.add(main_column)


ft.app(target=main)