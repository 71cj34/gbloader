import time
import webbrowser
from typing import Any, List, Optional

import requests


def main() -> None:
    try:
        with open("load.txt", "r") as f:
            text: str = f.read()
            urls: List[str] = [u.strip() for u in text.split(",") if u.strip()]
    except FileNotFoundError:
        print("File load.txt not found.")
        return

    multilink = []
    for url in urls:
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
            if len(data["_aFiles"]) == 1:
                print(f"Mod #{mod_id} has one version, preparing download...")
                link = data["_aFiles"][0]["_sDownloadUrl"]
                name = data["_aFiles"][0]["_sFile"]

                with requests.get(link, stream=True) as r:
                    r.raise_for_status()
                    with open(name, "wb") as f:
                        for chunk in r.iter_content(chunk_size=4096 * 2048):
                            if chunk:
                                f.write(chunk)
                print(f"Mod #{mod_id} has one version, successfully downloaded.\n")
            else:
                multilink.append(url)
                print(f"Mod #{mod_id} has multiple versions.\n")
        except Exception as e:
            print(f"An error occurred for ID {mod_id}: {e}")
            continue
    print("All downloads finished. The following mods must be downloaded manually: ")
    for i in range(len(multilink)):
        print("   - " + multilink[i])
    a = input(f"Open {len(multilink)} tabs in browser?")
    for i in range(len(multilink)):
        webbrowser.open(f"{multilink[i]}#FilesModule")


if __name__ == "__main__":
    main()
