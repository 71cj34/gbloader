import pathlib
import shutil
import subprocess
import sys

szip = "7z.exe"

if not shutil.which(szip):
    print(f"Error: 7-Zip executable not found at '{szip}'.")
    sys.exit(1)

current_dir = pathlib.Path(".")

archive_extensions = {".7z", ".zip", ".rar", ".tar", ".gz", ".bz2", ".xz"}

for item in current_dir.iterdir():
    if item.is_file() and item.suffix.lower() in archive_extensions:
        archive_name = item.name
        output_folder = item.stem

        print(f"Extracting '{archive_name}' to folder '{output_folder}'...")

        command = [
            szip,
            "x",
            str(item.absolute()),
            f"-o{output_folder}",
            "-y",
        ]

        try:
            result = subprocess.run(command, check=False)

            if result.returncode == 0:
                print(f"Successfully extracted record into '{output_folder}'.")
            else:
                print(
                    f"Error: Failed to extract '{archive_name}'. 7-Zip exited with code: {result.returncode}"
                )
        except Exception as e:
            print(f"An unexpected error occurred while processing {archive_name}: {e}")

print("Batch extraction complete.")
