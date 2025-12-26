import json
import pathlib
import time
from dataclasses import dataclass, field
from typing import Any, List, Optional

import requests


@dataclass
class modData:
    id: str
    modname: str
    subname: str
    photourl: str
    filenames: List[str] = field(default_factory=list)


def getData(url: str) -> Optional[modData]:
    time.sleep(0.1)
    if not url:
        return None

    mod_id = url.strip().rstrip("/").split("/")[-1].split("?")[0]

    try:
        response: requests.Response = requests.get(
            f"https://gamebanana.com/apiv11/Mod/{mod_id}/ProfilePage", timeout=10
        )
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        preview_media: dict[str, Any] = data.get("_aPreviewMedia", {})
        images: List[dict[str, Any]] = preview_media.get("_aImages", [])
        submitter: dict[str, Any] = data.get("_aSubmitter", {})
        filesarray: List[dict[str, Any]] = data.get("_aFiles", [])

        filenamesarray: list[str] = [file["_sFile"] for file in filesarray]

        if images:
            first_image: dict[str, Any] = images[0]
            pic: str = f"{first_image['_sBaseUrl']}/{first_image['_sFile']}"
        else:
            return None

        return modData(
            id=mod_id,
            modname=data.get("_sName", "Unknown"),
            subname=submitter.get("_sName", "Unknown"),
            photourl=pic,
            filenames=filenamesarray,
        )

    except Exception as e:
        print(f"An error occurred for ID {mod_id}: {e}")
        return None


def main() -> None:
    try:
        with open("load.txt", "r") as f:
            text: str = f.read()
            urls: List[str] = [u.strip() for u in text.split(",") if u.strip()]
    except FileNotFoundError:
        print("File load.txt not found.")
        return

    all_folders_map = {f.name: f for f in pathlib.Path(".").iterdir() if f.is_dir()}

    for url in urls:
        mod_item: Optional[modData] = getData(url)
        if not mod_item:
            continue

        matching_folders: list[pathlib.Path] = []
        for fname in mod_item.filenames:
            if fname in all_folders_map:
                matching_folders.append(all_folders_map[fname])

        if not matching_folders:
            print(f"No local match found for {mod_item.modname} ({mod_item.id})")
            continue

        for target_folder in matching_folders:
            print(f"Updating: {mod_item.modname} -> {target_folder.resolve()}")

            config_path = target_folder / ".JASM_ModConfig.json"
            img_path = target_folder / ".JASM_Cover.jpg"

            # 1. update/create json config
            try:
                config_data: dict[str, Any] = {}
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        try:
                            config_data = json.load(f)
                        except json.JSONDecodeError:
                            config_data = {}

                config_data["CustomName"] = mod_item.modname
                config_data["Author"] = mod_item.subname
                config_data["ModUrl"] = f"https://gamebanana.com/mods/{mod_item.id}"
                config_data["ImagePath"] = ".JASM_Cover.jpg"

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4)
            except Exception as e:
                print(f"Failed to update config in {target_folder}: {e}")

            # 2. add/download image
            if not img_path.exists():
                try:
                    img_res = requests.get(mod_item.photourl, stream=True, timeout=15)
                    img_res.raise_for_status()
                    with open(img_path, "wb") as f:
                        for chunk in img_res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Image saved to: {img_path}")
                except Exception as e:
                    print(f"Failed to download image: {e}")


if __name__ == "__main__":
    main()
