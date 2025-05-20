# GUI-based manual alignment and y-threholding tool for 3D images
import os
from tifffile import imread, imwrite
import napari
import numpy as np
from scipy.ndimage import shift
from magicgui import magicgui
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget
import tkinter as tk
from tkinter import filedialog
import tkinter as tk
from tkinter import filedialog


import tkinter as tk
from tkinter import filedialog

def manual_aligner(file1_path, file2_path, scale = [100, 3.45, 3.45]):
    has_two_channels = file2_path is not None

    assert os.path.exists(file1_path), f"File 1 does not exist: {file1_path}"
    zstack1 = imread(file1_path)


    if has_two_channels:
        assert os.path.exists(file2_path), f"File 2 does not exist: {file2_path}"
        zstack2 = imread(file2_path)

    settings = {'y_threshold': 1000}

    # open viewer
    viewer = napari.Viewer()
    viewer.window._qt_window.activateWindow()
    viewer.window._qt_window.raise_()

    container = QWidget()
    layout = QVBoxLayout()

    # add the z-stacks to the viewer
    scale_xy = scale
    scale_xy[0] = 1
    viewer.add_image(zstack1, name='ZStack1', colormap='magenta', scale = scale)
    if has_two_channels:
        viewer.add_image(zstack2, name='ZStack2', colormap='green', opacity=0.5, scale = scale)

    # line for threshold
    y_pos = 1000  # initial y position for the line

    all_lines = []
    for z in range(zstack1.shape[0]):
        line_coords = np.array([
            [z, y_pos, 0],
            [z, y_pos, zstack1.shape[2]]
        ]) 
        all_lines.append(line_coords)

    viewer.add_shapes(all_lines,
                    shape_type='line',
                    edge_color='yellow',
                    edge_width=30,
                    name='horizontal line',
                    scale = scale_xy)
    
    # slider gui for y threshold
    @magicgui(
        auto_call=True,
        y_threshold={"widget_type": "Slider", "min": 0, "max": zstack1.shape[1], "step": 1},
    )
    def y_threshold_control(y_threshold=1000):
        settings['y_threshold'] = y_threshold

        all_lines = []
        for z in range(zstack1.shape[0]):
            line_coords = np.array([
                [z, y_threshold, 0],
                [z, y_threshold, zstack1.shape[2]]
            ]) 
            all_lines.append(line_coords)

        # update the line coordinates
        viewer.layers['horizontal line'].data = all_lines

    layout.addWidget(y_threshold_control.native)


    # slider GUI for xyz translation
    if has_two_channels:

        @magicgui(
            auto_call=True,
            z_shift={"widget_type": "Slider", "min": -20, "max": 20, "step": 1},
            y_shift={"widget_type": "Slider", "min": -200, "max": 200, "step": 1},
            x_shift={"widget_type": "Slider", "min": -200, "max": 200, "step": 1},
        )
        def shift_control(z_shift=0, y_shift=0, x_shift=0):
            settings['z_shift'] = z_shift
            settings['y_shift'] = y_shift
            settings['x_shift'] = x_shift

            viewer.layers['ZStack2'].translate = [x * y for x, y in zip([z_shift, y_shift, x_shift], scale)]

        viewer.window.add_dock_widget(shift_control, area='right')

    container.setLayout(layout)
    viewer.window.add_dock_widget(container, area='right')

    napari.run()

    # 

    print("y_threshold:", settings['y_threshold'])
    if has_two_channels:
        print("z_shift:", settings['z_shift'])
        print("y_shift:", settings['y_shift'])
        print("x_shift:", settings['x_shift'])

        # apply the shift to the second z-stack
        zstack2 = shift(zstack2, [settings['z_shift'], settings['y_shift'], settings['x_shift']])
                        
        # crop the z-stacks to the same size
        min_z, min_y, min_x = np.min(np.array([zstack1.shape, zstack2.shape]), axis=0)
        zstack1 = zstack1[:min_z, :min_y, :min_x]
        zstack2 = zstack2[:min_z, :min_y, :min_x]

        # save new z-stack
        file2_path_new = os.path.splitext(file2_path)[0] + "_new.tif"
        imwrite(file2_path_new, zstack2)
        print(f"Shifted file saved as: {file2_path_new}")

    # mask anterior part of zstack1
    background_value = np.percentile(zstack1, 0.1)
    zstack1[:,: settings["y_threshold"], :] = background_value

    file1_path_new = os.path.splitext(file1_path)[0] + "_new.tif"
    imwrite(file1_path_new, zstack1)
    print(f"Masked file saved as: {file1_path_new}")

    # check new files
    confirm_new_images(zstack1, zstack2 if has_two_channels else None)



def confirm_new_images(zstack1, zstack2=None):
    viewer = napari.Viewer()
    viewer.window._qt_window.activateWindow()
    viewer.window._qt_window.raise_()

    viewer.add_image(zstack1, name='ZStack1 (new)', colormap='magenta')
    if zstack2 is not None:
        viewer.add_image(zstack2, name='ZStack2 (new)', colormap='green', opacity=0.5)

    napari.run()


def select_files():
    file_paths = {"file1": None, "file2": None}

    def browse_file1():
        file_paths["file1"] = filedialog.askopenfilename(
            title="Select first file",
            filetypes=[("Image files", "*.tif *.png *.jpg"), ("All files", "*.*")]
        )
        if file_paths["file1"]:
            label1.config(text=f"File 1: {file_paths['file1']}")

    def browse_file2():
        file_paths["file2"] = filedialog.askopenfilename(
            title="Select second file (optional)",
            filetypes=[("Image files", "*.tif *.png *.jpg"), ("All files", "*.*")]
        )
        if file_paths["file2"]:
            label2.config(text=f"File 2: {file_paths['file2']}")
        else:
            label2.config(text="File 2: Not selected")

    def confirm_selection():
        root.destroy()  

    root = tk.Tk()
    root.title("Select Files")

    tk.Button(root, text="Browse File 1", command=browse_file1).pack(padx=20, pady=5)
    label1 = tk.Label(root, text="File 1: Not selected")
    label1.pack(padx=20, pady=5)

    tk.Button(root, text="Browse File 2 (optional)", command=browse_file2).pack(padx=20, pady=5)
    label2 = tk.Label(root, text="File 2: Not selected")
    label2.pack(padx=20, pady=5)

    tk.Button(root, text="Confirm and Exit", command=confirm_selection).pack(padx=20, pady=10)

    root.mainloop()

    return file_paths["file1"], file_paths["file2"]



### test code
if __name__ == "__main__":
    # Select files using the file dialog
    file1_path, file2_path = select_files()
    # Call the manual_aligner function with the selected file paths
    manual_aligner(file1_path, file2_path, scale = [100, 3.45, 3.45])
