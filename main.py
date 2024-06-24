import tkinter as tk
from tkinter import ttk, messagebox
from locator import active_facility_id_name, match_facility_name, match_institution_name, match_institution_id
from PIL import Image, ImageTk
from graphing_analytics import *

# Function to filter combobox options based on input
def search(event):
    value = var.get()
    if value == '':
        drop['values'] = options  # Reset options if search input is empty
    else:
        data = []
        for item in options:
            if value.lower() in item.lower():
                data.append(item)
        drop['values'] = data  # Set filtered options based on search input

# Function to handle 'Find' button click
def update_graph(img_buf):
    # Load the image from the buffer
    img = Image.open(img_buf)
    img = ImageTk.PhotoImage(img)

    image_label.configure(image=img)
    image_label.image = img

    return img


def resize_img(img):
    new_size = (1000, 1000)
    resized_image = img.resize(new_size, Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    return img


def click():
    label2_text.set("")
    sv = var.get().strip()
    if not sv:
        img = update_graph(all_image_buf)
        image_label = tk.Label(root, image=img)
    try:
        selected_value = int(sv.split(" ")[0])
        facility_name_var.set(f"{match_facility_name(selected_value)}")
        institution_name_var.set(f"{match_institution_name(selected_value)}")
        institution_id_var.set(f"{match_institution_id(selected_value)}")

        # Update label2 text
        label2_text.set(f"Facility Name: {facility_name_var.get()}   Facility ID: {selected_value}   Institution Name: {institution_name_var.get()}   Institution ID: {institution_id_var.get()}")
        img = update_graph(init(selected_value))
        image_label = tk.Label(root, image=img)
        # Show label2
        label2.pack()
    except Exception as e:
        print(e)
        messagebox.showwarning("Entry not found", f"{sv} is not available as a facility.")


# Create main window
root = tk.Tk()
root.geometry("1000x700")
root.title("Facility Statistics")


# Retrieve active facility IDs and names
options = active_facility_id_name()

# Frame 1: Facility Selection
frame1 = tk.Frame(root)
frame1.pack(pady=20)

label = tk.Label(frame1, text="Please choose a facility:")
label.pack()

var = tk.StringVar()
drop = ttk.Combobox(frame1, textvariable=var)
drop['values'] = options  # Set initial options in combobox
drop.pack()

drop.bind('<KeyRelease>', search)  # Bind KeyRelease event to search function
drop.bind('<<ComboboxSelected>>', lambda event: var.set(drop.get()))  # Set selected value on selection

# 'Find' Button
enter_button = tk.Button(frame1, text='Find', command=click)
enter_button.pack()

# Frame 2: Display Selected Facility Information
frame2 = tk.Frame(root)
frame2.pack(pady=20)

facility_name_var = tk.StringVar()
institution_name_var = tk.StringVar()
institution_id_var = tk.StringVar()
label2_text = tk.StringVar()

label2 = tk.Label(frame2, textvariable=label2_text, wraplength=700)

all_image_buf = init("all")
img = Image.open(all_image_buf)
# img = Image.open(init("1152"))
img = resize_img(img)
# Create a label to display the image
image_label = tk.Label(root, image=img)
image_label.pack(pady=20)

# Start the main tkinter event loop
root.mainloop()

