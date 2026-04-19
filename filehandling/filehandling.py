import os

def make_output(dest_folder):
    try:
        os.makedirs(dest_folder, exist_ok=True)
    except PermissionError as e:
        print(f"Error while setting up output directory: \"{e}\". Closing process."
              f"Help message: Has permission been granted to create a folder?")
    except Exception as e:
        print("Error while setting up output directory:", e, "Closing process")

def create_output_path(dest_folder,file_name):
    output_path = os.path.join(dest_folder, file_name)
    root, ext = os.path.splitext(file_name)
    count = 1
    while os.path.exists(output_path):
        output_path = os.path.join(dest_folder, f"{root} ({count}){ext}")
        count += 1
    return output_path