import flet as ft
import os
from segmentation.TS import run_TS
from converter.meshconverter_nii import nii_mask_2_stl 

def main(page: ft.Page):
    page.title = "Pyramid(PyRadioMics-Detector)"
    page.scroll = ft.ScrollMode.AUTO

    dicom_dir = ft.TextField(label="DICOM 폴더", read_only=True)
    output_dir = ft.TextField(label="출력 폴더", read_only=True)
    organ_field = ft.TextField(label="장기 이름", hint_text="예: pancreas")
    log_output = ft.TextField(label="로그", multiline=True, read_only=True, expand=True)

    def log(msg):
        log_output.value += f"{msg}\n"
        page.update()

    def choose_dicom_dir(e):
        def result(e: ft.FilePickerResultEvent):
            if e.path:
                dicom_dir.value = os.path.normpath(e.path)
                page.update()
        page.dialog = ft.FilePicker(on_result=result)
        page.dialog.get_directory_path()

    def choose_output_dir(e):
        def result(e: ft.FilePickerResultEvent):
            if e.path:
                output_dir.value = os.path.normpath(e.path)
                page.update()
        page.dialog = ft.FilePicker(on_result=result)
        page.dialog.get_directory_path()

    def start_pipeline(e):
        dicom_path = dicom_dir.value
        out_path = output_dir.value
        organ = organ_field.value.strip().lower()

        if not all([dicom_path, out_path, organ]):
            log("하나는 전체를 위해 전체는 하나를 위해 그러니까 다 채워봐!!!!!!!!")
            return

        os.makedirs(out_path, exist_ok=True) 

        log("두근두근 Segmentation 시작")
        success = run_TS(dicom_path, out_path, organ)
        if not success:
            log("또또또 Totalsegmentator 실수했네")
            return

        nii_path = os.path.join(out_path, f"{organ}.nii.gz")
        stl_path = os.path.join(out_path, f"{organ}.stl")

        log("두근두근 STL 변환 중")
        if nii_mask_2_stl(nii_path, stl_path):
            log(f"역시 난 똑띠야: {stl_path}")
        else:
            log("또또또 실수했네")

    page.add(
        ft.Row([
            dicom_dir,
            ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=choose_dicom_dir)
        ]),
        ft.Row([
            output_dir,
            ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=choose_output_dir)
        ]),
        organ_field,
        ft.ElevatedButton("누르면 시작", on_click=start_pipeline),
        log_output
    )

ft.app(target=main)

