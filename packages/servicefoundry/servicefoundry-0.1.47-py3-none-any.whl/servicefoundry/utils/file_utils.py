import os
import tarfile


def make_executable(file_path):
    mode = os.stat(file_path).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(file_path, mode)


def create_file_from_content(file_path, content, executable=False):
    with open(file_path, "w") as text_file:
        text_file.write(content)
    if executable:
        make_executable(file_path)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        for fn in os.listdir(source_dir):
            p = os.path.join(source_dir, fn)
            tar.add(p, arcname=fn)
