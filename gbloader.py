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


@dataclass
class dataCollection:
    item: List[modData] = field(default_factory=list)


datas: dataCollection = dataCollection()


def getData(url: str) -> Optional[modData]:
    time.sleep(0.1)

    if not url:
        return None

    mod_id: str = url.strip().split("/")[-1]

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

    # o(1) lookup
    folder_map = {f.name: f for f in pathlib.Path(".").iterdir() if f.is_dir()}

    for url in urls:
        mod_item: Optional[modData] = getData(url)

        if not mod_item:
            print(f"Could not retrieve data for {url}")
            continue

        # check if one of the potential filenames in this mod_item matches the real filename
        match_folder: Optional[pathlib.Path] = None
        for fname in mod_item.filenames:
            if fname in folder_map:
                match_folder = folder_map[fname]
                break

        if match_folder:
            print(f"Match found: {mod_item.modname} -> {match_folder.name}")
            config_path = match_folder / ".JASM_ModConfig.json"

            # 1. update json config
            try:
                config_data = {}
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                config_data["CustomName"] = mod_item.modname
                config_data["Author"] = mod_item.subname
                config_data["ModUrl"] = f"https://gamebanana.com/mods/{mod_item.id}"
                config_data["ImagePath"] = ".JASM_Cover.jpg"

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4)
            except Exception as e:
                print(f"Failed to update config for {match_folder.name}: {e}")

            # 2. add image
            img_path = match_folder / ".JASM_Cover.jpg"
            try:
                img_res = requests.get(mod_item.photourl, stream=True, timeout=15)
                img_res.raise_for_status()
                with open(img_path, "wb") as f:
                    for chunk in img_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Image saved: {img_path}")
            except Exception as e:
                print(f"Failed to download image: {e}")
        else:
            print(
                f"No local folder match found for {mod_item.modname} (ID: {mod_item.id})"
            )


if __name__ == "__main__":
    main()
