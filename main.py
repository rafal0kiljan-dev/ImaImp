import pandas as pd
import streamlit as st

# Standard Library
import os
import tempfile
import platform
import subprocess
from PIL import Image
import time

import io
import tempfile
# --------------------------------------
# Global Variables
# --------------------------------------


# Operation System
PLATFORM = platform.system()


# Directory of the script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# Directory of the models
MODEL_DIR = os.path.join(SCRIPT_DIR, "resrgan/models")


# Path to RESRGAN executable
if PLATFORM == "Windows":
    RESRGAN_PATH = os.path.join(SCRIPT_DIR, "resrgan/realesrgan-ncnn-vulkan.exe")
else: # Linux
    RESRGAN_PATH = os.path.join(SCRIPT_DIR, "resrgan/realesrgan-ncnn-vulkan")
    # Make sure the executable has the correct permissions
    subprocess.call(['chmod', 'u+x', RESRGAN_PATH])

#"realesr-animevideov3-x4"
# Predefined model list
HARDCODED_MODELS = [
    "realesrgan-x4plus",
    "realesr-animevideov3-x4",
    "realesrgan-x4plus-anime",
    "UltraSharp-4x",
    "AnimeSharp-4x"
]


# Default values:
DEFAULT_MODEL_INDEX = 0
DEFAULT_SELECTION_MODE = 0 # Layer
DEFAULT_KEEP_COPY_LAYER = False
DEFAULT_SCALE_FACTOR = 1.0


# Scale factor range
SCALE_START = 0.1
SCALE_END = 8.0
SCALE_INCREMENT = 0.05

def check_suffix(uploaded_file):
    ext = uploaded_file.name
    suf = ".jpg"
    if ext.endswith(".mp4") == True:
        suf = ".mp4"
    elif ext.endswith(".jpg") == True:
        suf = ".jpg"
    elif ext.endswith(".png") == True:
        suf = ".png"
    else:
        suf = ".jpg"
    return suf
    
def check_suffix_for_output(uploaded_file):
    ext = uploaded_file
    suf = "JPEG"
    if ext.endswith(".jpg") == True:
        suf = "JPEG"
    elif ext.endswith(".png") == True:
        suf = "PNG"
    elif ext.endswith(".mp4") == True:
        suf = "MP4"
    else:
        suf = "JPEG"
    return suf

def _run_resrgan(uploaded_file, temp_output_file, model, shell):
    suf = check_suffix(uploaded_file)
    print(suf)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suf) as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input_path = temp_input.name

    # Use file paths in subprocess
    upscale_process = subprocess.Popen([
        RESRGAN_PATH,
        "-i", temp_input_path,
        "-o", temp_output_file,
        "-s", "4",
        "-n", model
    ], shell=shell)
    
    upscale_process.wait()
    temp_input.close()
    os.remove(temp_input_path)
    
    
MODEL_COLOR_DIR = os.path.join(SCRIPT_DIR, "COLOR_GAN/models")
COLOR_PATH = os.path.join(SCRIPT_DIR, "COLOR_GAN/COLOR_GAN.exe")
COLOR_DIR = os.path.join(SCRIPT_DIR, "COLOR_GAN")
    
def _run_color_gan(uploaded_file):
    suf = check_suffix(uploaded_file)
    namefile = "temp"+suf
    temp_output_path = os.path.join(COLOR_DIR,"result_colored_out"+suf)
    print(temp_output_path)
    with open(os.path.join(COLOR_DIR,'temp'+suf), "wb") as f:
        f.write(uploaded_file.read())
    os.system(os.path.join(COLOR_DIR,'run_color_gan.bat'))
    f.close()
    img = Image.open(os.path.join(COLOR_DIR,'result_colored_out.png'))
    img.save(temp_output_path)
    """
    with open(temp_output_path, "wb") as result:
        result.write(img.read())
        result.close()
    """
    while not os.path.exists(temp_output_path):
        print("Waiting for file...")

        time.sleep(0.2)
        """
    with open(temp_output_path, "wb") as result:
        r = os.path.join(COLOR_DIR,'result_colored_out.jpg')
        result.write(r.read())
    f.close()
    result.close()
    """
    os.remove(os.path.join(COLOR_DIR,'temp'+suf))

def _find_additional_models():
    '''Function to find additional upscale models in the "resrgan/models" folder'''
    # List all files in the models directory
    all_files = os.listdir(MODEL_DIR)
    # Filter out .bin and .param files
    bin_files = {os.path.splitext(f)[0] for f in all_files if f.endswith('.bin')}
    param_files = {os.path.splitext(f)[0] for f in all_files if f.endswith('.param')}
    # Find paired models
    paired_models = bin_files & param_files
    # Filter out hardcoded models
    models = [model for model in paired_models if model not in HARDCODED_MODELS]
    return models  
    
st.title("AI image upscaling")  

@st.dialog("Choose the style.")
def vote1():
    style = st.radio("Select one option",["Anime / Cartoon", "Photo / Movie"],index=None,)   
    uploaded_files = st.file_uploader("Upload data", accept_multiple_files=True, type=["jpg","png","mp4"])  
    model_index = 0
    if style == "Anime / Cartoon":
        model_index = 2
    else:
        model_index = 0
    model = HARDCODED_MODELS[model_index]

    if len(uploaded_files) >= 1:
        uploaded_file = uploaded_files[0]
        suf = check_suffix(uploaded_file)
        print(suf)
        with st.spinner("Wait for it...", show_time=True):
            temp_output_file = tempfile.NamedTemporaryFile(suffix=suf, delete=False)
            temp_output_path = temp_output_file.name
            
            shell = True if PLATFORM == "Windows" else False
            _run_resrgan(uploaded_file, temp_output_path, model, shell)
            SUF=check_suffix_for_output(temp_output_path)
            if SUF != "MP4":
                img = Image.open(temp_output_path)
                st.image(img, output_format=SUF)
            else:
                video_file = open(temp_output_path, "rb")
                video_bytes = video_file.read()
                st.video(video_bytes)
        st.success("Done!")
        temp_output_file.close() 
        os.remove(temp_output_path)
left, middle, right = st.columns(3)

@st.dialog("Choose file")
def vote2():
    uploaded_files = st.file_uploader("Upload data", accept_multiple_files=True, type=["jpg","png","mp4"])
    if len(uploaded_files) >= 1:
        uploaded_file = uploaded_files[0]
        suf = check_suffix(uploaded_file)
        print(suf)
        with st.spinner("Wait for it...", show_time=True):
            _run_color_gan(uploaded_file)
            temp_output_path = COLOR_DIR+"\\result_colored_out"+suf
            SUF=check_suffix_for_output(uploaded_file.name)
            if SUF != "MP4":
                print(temp_output_path)
                img = Image.open(temp_output_path)
                st.image(img, output_format=SUF)
            else:
                video_file = open(temp_output_path, "rb")
                video_bytes = video_file.read()
                st.video(video_bytes)
        st.success("Done!")
        #temp_output_file.close() 
        os.remove(temp_output_path)
@st.dialog("Cast your vote")
def vote3():
    st.write("Not ready")
    
if left.button("Upscale", width="stretch"):
    vote1()
if middle.button("Colored", width="stretch"):
    vote2()
if right.button("Option 3", width="stretch"):
    vote3()
