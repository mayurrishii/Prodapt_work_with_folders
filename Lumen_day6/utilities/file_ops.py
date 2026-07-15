from pathlib import Path


def write_file(file_path, content):
    Path(file_path).write_text(content, encoding="utf-8")


def read_file(file_path):
    return Path(file_path).read_text(encoding="utf-8")


def search_in_file(file_path, keyword):
    content = read_file(file_path)
    return keyword in content
