import logging
import os

# log = logging.getLogger("DEBUG_LOG")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "\n# %(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s: \n%(message)s"
)

console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

file_path_info = f"./_temp/logs/main_info.log"
file_path_debug = f"./_temp/logs/main_debug.log"
for file_path in (file_path_info, file_path_debug):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if file_path.endswith("_info.log"):
        file_handler_info = logging.FileHandler(
            filename=file_path, mode="a", encoding="utf-8"
        )
        file_handler_info.setLevel(logging.INFO)
        file_handler_info.setFormatter(formatter)
        log.addHandler(file_handler_info)
    elif file_path.endswith("_debug.log"):
        file_handler_debug = logging.FileHandler(
            filename=file_path, mode="a", encoding="utf-8"
        )
        file_handler_debug.setLevel(logging.DEBUG)
        file_handler_debug.setFormatter(formatter)
        log.addHandler(file_handler_debug)
