import flet as ft
import main as backend
def main(page: ft.page):
    page.title = "FaceSort AI"
    page.theme_more=ft.ThemeMode.SYSTEM
    page.bgcolor="#b0d1f2"
    page.window_width=1000
    page.window_height=800
    page.vertical_alignment=ft.MainAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    selected_path=ft.Text("No folder selected",color=ft.Colors.GREY_500,italic=True)
    start_btn=ft.ElevatedButton("Start", disabled=True, opacity=0.5)
    def on_folder_picked(e: ft.filePickerResultEvent):
        if e.path:
            selected_path.value=e.path
            start_btn.disabled=False
            start_btn.opacity=1.0
            start_btn.update()
            selected_path.update()
        else:
            pass
    file_picker=ft.FilePicker(on_result=on_folder_picked,dialog_title="Select Folder with Images",dialog_type=ft.FilePickerDialogType.FOLDER)
    page.overlay.append(file_picker)