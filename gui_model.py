import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

from segmentation.TS import run_TS
from converter.meshconverter_nii import nii_mask_2_stl

class PyramidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyramid (PyRadioMics-Detector)")
        
        tk.Label(root, text="DICOM 폴더").grid(row=0, column=0, sticky="w")
        self.dicom_dir_entry = tk.Entry(root, width=60)
        self.dicom_dir_entry.grid(row=0, column=1)
        tk.Button(root, text="찾기", command=self.choose_dicom_dir).grid(row=0, column=2)

        tk.Label(root, text="출력 폴더").grid(row=1, column=0, sticky="w")
        self.output_dir_entry = tk.Entry(root, width=60)
        self.output_dir_entry.grid(row=1, column=1)
        tk.Button(root, text="찾기", command=self.choose_output_dir).grid(row=1, column=2)

        tk.Label(root, text="장기 이름").grid(row=2, column=0, sticky="w")
        self.organ_entry = tk.Entry(root, width=60)
        self.organ_entry.grid(row=2, column=1, columnspan=2)

        self.start_button = tk.Button(root, text="누르면 시작", command=self.start_pipeline)
        self.start_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.log_output = scrolledtext.ScrolledText(root, height=15, width=80, state='disabled')
        self.log_output.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    def log(self, message):
        self.log_output.config(state='normal')
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.config(state='disabled')
        self.log_output.see(tk.END)

    def choose_dicom_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.dicom_dir_entry.delete(0, tk.END)
            self.dicom_dir_entry.insert(0, os.path.normpath(path))

    def choose_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, os.path.normpath(path))

    def start_pipeline(self):
        dicom_path = self.dicom_dir_entry.get()
        out_path = self.output_dir_entry.get()
        organ = self.organ_entry.get().strip().lower()

        if not all([dicom_path, out_path, organ]):
            messagebox.showwarning("경고", "하나는 전체를 위해 전체는 하나를 위해 그러니까 다 채워봐!!!!!!!!")
            return

        os.makedirs(out_path, exist_ok=True)

        self.log("두근두근 Segmentation 시작")
        success = run_TS(dicom_path, out_path, organ)
        if not success:
            self.log("또또또 Totalsegmentator 실수했네")
            return

        nii_path = os.path.join(out_path, f"{organ}.nii.gz")
        stl_path = os.path.join(out_path, f"{organ}.stl")

        self.log("두근두근 STL 변환 중")
        if nii_mask_2_stl(nii_path, stl_path):
            self.log(f"역시 난 똑띠야: {stl_path}")
        else:
            self.log("또또또 실수했네")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyramidApp(root)
    root.mainloop()
