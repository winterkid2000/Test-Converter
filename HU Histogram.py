import os
import argparse
import numpy as np
import nibabel as nib
import dicom2nifti
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from nibabel.orientations import aff2axcodes, axcodes2ornt, ornt_transform, apply_orientation

def dcm2nii(dicom_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    try:
        dicom2nifti.convert_directory(dicom_path, output_path, reorient=True)
        for f in os.listdir(output_path):
            if f.endswith(".nii.gz"):
                return os.path.join(output_path, f)
    except Exception as e:
        print(f"DICOM 내놔!!!!!!: {dicom_path} - {e}")
    return None

def set_axis(source_img: nib.Nifti1Image, target_img: nib.Nifti1Image) -> np.ndarray:
    source_ax = aff2axcodes(source_img.affine)
    target_ax = aff2axcodes(target_img.affine)
    if source_ax == target_ax:
        return source_img.get_fdata()
    source_ornt = axcodes2ornt(source_ax)
    target_ornt = axcodes2ornt(target_ax)
    transform = ornt_transform(source_ornt, target_ornt)
    data = source_img.get_fdata()
    return apply_orientation(data, transform)

def hu_ext(ct_array, mask_array):
    return ct_array[mask_array > 0].flatten()

def process_all(dicom_root, mask_root, mode, output_root):
    os.makedirs(output_root, exist_ok=True)
    patient_ids = sorted(os.listdir(dicom_root))
    for pid in tqdm(patient_ids, desc=f"Processing {mode}"):
        dicom_path = os.path.join(dicom_root, pid, mode)
        mask_path = os.path.join(mask_root, pid, f"{mode}{pid}.nii")
        temp_output_path = os.path.join("temp_nifti", pid, mode)

        if not os.path.exists(dicom_path):
            print(f"DICOM을 안 주면 어떻게 해!!!!!!!!!!: {dicom_path}")
            continue
        if not os.path.exists(mask_path):
            print(f"마스크 없으면 감기 걸려: {mask_path}")
            continue

        nii_ct_path = dcm2nii(dicom_path, temp_output_path)
        if not nii_ct_path:
            continue

        try:
            ct_img = nib.load(nii_ct_path)
            mask_img = nib.load(mask_path)

            ct_array = ct_img.get_fdata()
            mask_array = set_axis(mask_img, ct_img)

            if ct_array.shape != mask_array.shape:
                print(f"무엇이 무엇이 똑같을까 {pid}: CT{ct_array.shape}, Mask{mask_array.shape}")
                continue

            hu_values = hu_ext(ct_array, mask_array)
            if hu_values.size == 0:
                print(f"마스크 없으면 코로나 걸리는데: {pid}")
                continue

            bins = np.arange(-1000, 2001)
            hist, edges = np.histogram(hu_values, bins=bins)

            filename_prefix = f"{pid}_{mode}"
            df = pd.DataFrame({
                'HU Bin': edges[:-1],
                'Count': hist,
                'Frequency': hist / hist.sum()
            })
            df.to_csv(os.path.join(output_root, f"{filename_prefix}_histogram.csv"), index=False)

            plt.figure()
            plt.bar(edges[:-1], hist, width=1)
            plt.xlabel("HU Value")
            plt.ylabel("Count")
            plt.title(f"HU Histogram - {filename_prefix}")
            plt.tight_layout()
            plt.savefig(os.path.join(output_root, f"{filename_prefix}_histogram.png"))
            plt.close()

        except Exception as e:
            print(f"디버깅 해야 하네 ㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ: {pid} - {e}")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HU Histogram Extractor from DICOM + NIfTI Mask")
    parser.add_argument("--dicom_root", required=True, help="DICOM Root Folder")
    parser.add_argument("--mask_root", required=True, help="NIfTI Mask Root Folder")
    parser.add_argument("--output", required=True, help="Output Folder for Histograms")
    parser.add_argument("--phase", required=True, choices=["PRE", "POST"], help="Phase (PRE or POST)")

    args = parser.parse_args()
    process_all(args.dicom_root, args.mask_root, args.phase, args.output)
