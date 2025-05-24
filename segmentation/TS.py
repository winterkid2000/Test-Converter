import os
import subprocess

def run_TS(dicom_folder: str, output_folder: str, organ: str) -> bool:
    try:
        os.makedirs(output_folder, exist_ok=True)

        command = [
            "TotalSegmentator",
            "-i", dicom_folder,
            "-o", output_folder,
            "--ml",
            "--roi_subset", organ,
            "--output_type", "nifti"
        ]

        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      
        jeopchakjae_output = os.path.join(output_folder, f"{organ}.nii.gz")
        if not os.path.exists(jeopchakjae_output):
          
            auto_file = next((f for f in os.listdir(output_folder) if f.endswith(".nii.gz")), None)
            if auto_file:
                os.rename(os.path.join(output_folder, auto_file), jeopchakjae_output)

        return os.path.exists(jeopchakjae_output)

    except Exception as e:
        print(f"Segmentation 오류: {e}")
        return False

