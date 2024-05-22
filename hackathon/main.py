from database import initialize_database
from hackathon import (
    find_and_save_regions,
    reconstruct_image
)
import gradio as gr
import os
import platform
import subprocess
import uuid
import random


def simple_generate(output_dir, image1, image2):
    generate(output_dir, [image1, image2])


def advanced_generate(output_dir, image1, image2, image3):
    generate(output_dir, [image1, image2, image3])


def generate(output_dir, image_paths):
    db_path = f"{output_dir}/database.db"
    initialize_database(db_path)
    find_and_save_regions(
        image_paths=image_paths,
        db_path=db_path,
        output_dir=output_dir
    )


def reconstruct(output_dir, image_index):
    reconstruct_image(
        image_index=image_index,
        db_path=f"{output_dir}/database.db",
        output_path=f"{output_dir}/reconstructed_image{image_index}.avif"
    )


def defect_generation(count):
    images = [
        (random.choice([
            "../images/predicted_defect_pcb_1.jpg",
            "../images/predicted_defect_pcb_2.jpg",
            "../images/predicted_defect_pcb_3.jpg",
            "../images/predicted_defect_pcb_4.jpg",
            "../images/predicted_defect_pcb_5.jpg"
        ]), f"Predicted Defect#{i+1}")
        for i in range(count)
    ]
    return images


def open_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

    if platform.system().lower() == "darwin":
        subprocess.Popen(["open", path])
    else:
        os.startfile(path)


def open_directory_label():
    if platform.system().lower() == "darwin":
        return "Open in Finder"
    else:
        return "Open in Explorer"


def convert_bytes_into_size_text(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes_into_size_text(file_info.st_size)


if __name__ == "__main__":
    with gr.Blocks() as demo:
        with gr.Tab("Simple Image"):
            with gr.Row():
                with gr.Column():
                    simple_image1 = "../images/source1.jpg"
                    simple_file1 = gr.File(simple_image1, visible=False)
                    gr.Image(simple_image1, label=f"{file_size(simple_image1)}", interactive=False)
                with gr.Column():
                    simple_image2 = "../images/source2.jpg"
                    simple_file2 = gr.File(simple_image2, visible=False)
                    gr.Image(simple_image2, label=f"{file_size(simple_image2)}", interactive=False)
            with gr.Row():
                with gr.Column():
                    simple_output_dir = gr.Textbox(label="Output Directory", value=f"../images/output/{uuid.uuid4()}")
                    simple_output_dir_open = gr.Button(f"{open_directory_label()}")
                simple_generate_button = gr.Button("Generate", variant="primary")
            with gr.Row():
                with gr.Column():
                    simple_reconstruct1_number = gr.Number(label="Image Index", value=1, interactive=False)
                simple_reconstruct1_button = gr.Button("Reconstruct#1")
            with gr.Row():
                with gr.Column():
                    simple_reconstruct2_number = gr.Number(label="Image Index", value=2, interactive=False)
                simple_reconstruct2_button = gr.Button("Reconstruct#2")
        with gr.Tab("Advanced Image"):
            with gr.Row():
                with gr.Column():
                    advanced_image1 = "../images/source_pcb_1.png"
                    advanced_file1 = gr.File(advanced_image1, visible=False)
                    gr.Image(advanced_image1, label=f"{file_size(advanced_image1)}", interactive=False)
                with gr.Column():
                    advanced_image2 = "../images/source_pcb_2.png"
                    advanced_file2 = gr.File(advanced_image2, visible=False)
                    gr.Image(advanced_image2, label=f"{file_size(advanced_image2)}", interactive=False)
                with gr.Column():
                    advanced_image3 = "../images/source_pcb_3.png"
                    advanced_file3 = gr.File(advanced_image3, visible=False)
                    gr.Image(advanced_image3, label=f"{file_size(advanced_image2)}", interactive=False)
            with gr.Row():
                with gr.Column():
                    advanced_output_dir = gr.Textbox(label="Output Directory", value=f"../images/output/{uuid.uuid4()}")
                    advanced_output_dir_open = gr.Button(f"{open_directory_label()}")
                advanced_generate_button = gr.Button("Generate", variant="primary")
            with gr.Row():
                with gr.Column():
                    advanced_reconstruct1_number = gr.Number(label="Image Index", value=1, interactive=False)
                advanced_reconstruct1_button = gr.Button("Reconstruct#1")
            with gr.Row():
                with gr.Column():
                    advanced_reconstruct2_number = gr.Number(label="Image Index", value=2, interactive=False)
                advanced_reconstruct2_button = gr.Button("Reconstruct#2")
            with gr.Row():
                with gr.Column():
                    advanced_reconstruct3_number = gr.Number(label="Image Index", value=3, interactive=False)
                advanced_reconstruct3_button = gr.Button("Reconstruct#3")
        with gr.Tab("Defect Simulation"):
            with gr.Row():
                with gr.Column():
                    gr.Gallery([("../images/source_pcb_1.png", "Good#1")], label="Good")
                with gr.Column():
                    gr.Gallery([("../images/source_pcb_2.png", "Bad#1"), ("../images/source_pcb_3.png", "Bad#2")], label="Bad")
            with gr.Row():
                with gr.Column():
                    defect_generation_number = gr.Number(label="Generations", value=1, minimum=1, maximum=5, interactive=True)
                defect_generation_button = gr.Button("Defect Simulation", variant="primary")
            with gr.Row():
                defect_gallery = gr.Gallery(columns=5, label="Predicted Defects")

        simple_output_dir_open.click(open_directory, inputs=simple_output_dir)
        simple_generate_button.click(simple_generate, inputs=[simple_output_dir, simple_file1, simple_file2])
        simple_reconstruct1_button.click(reconstruct, inputs=[simple_output_dir, simple_reconstruct1_number])
        simple_reconstruct2_button.click(reconstruct, inputs=[simple_output_dir, simple_reconstruct2_number])

        advanced_output_dir_open.click(open_directory, inputs=advanced_output_dir)
        advanced_generate_button.click(advanced_generate, inputs=[advanced_output_dir, advanced_file1, advanced_file2, advanced_file3])
        advanced_reconstruct1_button.click(reconstruct, inputs=[advanced_output_dir, advanced_reconstruct1_number])
        advanced_reconstruct2_button.click(reconstruct, inputs=[advanced_output_dir, advanced_reconstruct2_number])
        advanced_reconstruct3_button.click(reconstruct, inputs=[advanced_output_dir, advanced_reconstruct3_number])

        defect_generation_button.click(defect_generation, inputs=defect_generation_number, outputs=defect_gallery)

    demo.launch()
