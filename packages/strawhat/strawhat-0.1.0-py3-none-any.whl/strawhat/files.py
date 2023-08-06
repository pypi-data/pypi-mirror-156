import json

# ------------------- File Management Funcs -------------------


def read_json(file_name, file_path):
    with open(file_path + file_name, "r") as f:
        return json.load(f)


def write_json(file_name, file_path, data):
    with open(file_path + file_name, "w+") as f:
        json.dump(data, f, indent=4)


def write_file(file_name, file_path, file_data):
    with open(file_path + file_name, "w+") as f:
        f.write(file_data)


def read_file(file_name, file_path):
    with open(file_path + file_name, "r") as f:
        return f.read()


def read_byte(file_name, file_path):
    with open(file_path + file_name, "rb") as f:
        return f.read()


def change_file_ext(file_name, extention):
    file_name_sans_ext = ".".join(file_name.split(".")[:-1])
    return ".".join([file_name_sans_ext, extention])
