import pathlib
import shutil
import subprocess
import sys

szip = "7z.exe"

if not shutil.which(szip):
    print(f"Error: 7-Zip executable not found at '{szip}'.")
    sys.exit(1)

current_dir = pathlib.Path(".")
output_parent = current_dir / "extracted"
output_parent.mkdir(exist_ok=True)

archive_extensions = {".7z", ".zip", ".rar", ".tar", ".gz", ".bz2", ".xz"}

for item in current_dir.iterdir():
    if item.is_file() and item.suffix.lower() in archive_extensions:
        archive_name = item.name

        output_folder = output_parent / archive_name

        print(f"Extracting '{archive_name}' to '{output_folder}'...")

        command = [
            szip,
            "x",
            str(item.absolute()),
            f"-o{str(output_folder.absolute())}",
            "-y",
        ]

        try:
            result = subprocess.run(command, check=False)

            if result.returncode == 0:
                print(f"Successfully extracted into '{output_folder}'.")
            else:
                print(
                    f"Error: Failed to extract '{archive_name}'. 7-Zip exited with code: {result.returncode}"
                )
        except Exception as e:
            print(f"An unexpected error occurred while processing {archive_name}: {e}")

print(f"Batch extraction complete. Files are in: {output_parent.absolute()}")
