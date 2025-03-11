import json
import platform
import shutil
import subprocess
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from typing import Any


def log_cmd(args: list):
    print(f"\033[0;1m+ {' '.join(map(lambda it: str(it), args))}\033[0m")
    return args


def is_file(path: Path, parser: ArgumentParser):
    if not path.is_file():
        parser.error(f"File not found '{path}'")


def json_loads(fromfile: Path) -> Any:
    with open(
        fromfile,
        encoding="utf-8-sig",
    ) as f:
        return json.loads(f.read())


def json_dumps(obj: Any, tofile: Path):
    with open(tofile, "wb") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2).encode())


def convert_uasset_json(
    uassetgui: Path,
    tojson: bool,
    input_paths: list[Path],
    output_paths: list[Path],
    version: tuple[int, int] = (4, 26),
):
    def convert(input_path: Path, output_path: Path):
        args = [
            uassetgui,
            "tojson" if tojson else "fromjson",
            input_path,
            output_path,
            f"VER_UE{version[0]}_{version[1]}",
        ]

        match platform.system():
            case "Linux":
                args[2:4] = [
                    it.decode()
                    for it in subprocess.run(
                        ["winepath", "-0", "-w", *args[2:4]],
                        capture_output=True,
                        check=True,
                    ).stdout.split(b"\0")
                    if it.decode().strip()
                ]

                # note: Assuming the only public build of UAssetGUI is a Window PE
                subprocess.run(
                    log_cmd(["wine"] + args), check=True, capture_output=True
                )
            case "Windows":
                subprocess.run(log_cmd(args), check=True, capture_output=True)
            case _:
                raise Exception("Unsupported system")

    assert len(input_paths) == len(output_paths)

    for input_path, output_path in zip(input_paths, output_paths):
        convert(input_path, output_path)


def patch_gathers_asset_json(asset_table: dict, mfactor: float):
    assert asset_table["$type"].find("UAssetAPI") != -1

    data_table = asset_table["Exports"][0]["Table"]["Data"]

    for gather_item in data_table:
        should_modify = False
        actions_list = None

        for it in gather_item["Value"]:
            if it["Name"] == "GatherType" and it["Value"] in [
                "EGatherType::Mineral",
                "EGatherType::Grass",
                "EGatherType::Wood",
            ]:
                should_modify = True

            if it.get("ArrayType") == "StructProperty" and it["Name"] == "Actions":
                actions_list = it["Value"]

            if should_modify and actions_list:
                for gather_action_setting in filter(
                    lambda it: it["StructType"] == "GatherActionSetting",
                    actions_list,
                ):
                    for action_setting in filter(
                        lambda it: it.get("StructType") == "ActionSetting",
                        gather_action_setting["Value"],
                    ):
                        num_obj = next(
                            filter(
                                lambda it: it["Name"] == "Num",
                                action_setting["Value"],
                            ),
                            None,
                        )
                        if num_obj and num_obj["Value"] > 0:
                            num_obj["Value"] = num_obj["Value"] * mfactor

                break


def patch_fishing_asset_json(asset_table: dict, mfactor: int):
    assert asset_table["$type"].find("UAssetAPI") != -1

    data_table = asset_table["Exports"][0]["Table"]["Data"]

    for fishing_item in data_table:
        exp_obj = next(
            filter(lambda it: it["Name"] == "Exp", fishing_item["Value"]), None
        )
        if exp_obj and exp_obj["Value"] > 0:
            exp_obj["Value"] = exp_obj["Value"] * mfactor


if __name__ == "__main__":
    script_dir = Path(__file__).absolute().parent

    parser = ArgumentParser(
        description="Multiply the resource and experience gain for some items in the Gathers table by a factor, and fishing experience gain in the Fishing table"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        metavar="FILE",
        type=Path,
        help="Path to the Game's '.pak' file",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        type=Path,
    )
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument(
        "--gather-factor",
        metavar="FLOAT",
        default=3,
        type=float,
        help="[default: 3] Multiplicative factor for resource and experience gain on item gathering",
    )
    parser.add_argument(
        "--fishing-factor",
        metavar="INT",
        default=5,
        type=int,
        help="[default: 5] Multiplicative factor for experience gain on fishing",
    )
    parser.add_argument(
        "--uassetgui",
        required=True,
        metavar="FILE",
        type=Path,
        help="Path to UAssetGUI (https://github.com/atenfyr/UAssetGUI)",
    )
    parser.add_argument(
        "--repak",
        required=True,
        metavar="FILE",
        type=Path,
        help="Path to trumank/repak (https://github.com/trumank/repak)",
    )

    args = parser.parse_args()

    for it in (args.input, args.uassetgui, args.repak):
        is_file(it, parser)

    args.fishing_factor = max(args.fishing_factor, 1)
    args.gather_factor = max(args.gather_factor, 1)

    output_path = args.output or Path(f"{args.input.stem}.Patched{args.input.suffix}")

    if output_path.exists() and not args.force:
        parser.error(f"File already exists '{output_path}'")

    if args.input.suffix.lower() != ".pak":
        parser.error("Only '.pak' files are allowed as input")

    tables_dir = "Wandering_Sword/Content/JH/Tables"
    with tempfile.TemporaryDirectory() as workdir:
        workdir = Path(workdir)
        subprocess.run(
            log_cmd(
                [
                    args.repak,
                    "unpack",
                    "-f",
                    "-i",
                    f"{tables_dir}/Gathers.*",
                    "-i",
                    f"{tables_dir}/Fishing.*",
                    "-o",
                    workdir,
                    args.input,
                ]
            ),
            check=True,
            capture_output=True,
        )

        tables_workdir = workdir.joinpath(tables_dir)

        gathers_uasset_path = tables_workdir.joinpath("Gathers.uasset")
        gathers_json_path = workdir.joinpath("Gathers.json")

        fishing_uasset_path = tables_workdir.joinpath("Fishing.uasset")
        fishing_json_path = workdir.joinpath("Fishing.json")

        convert_uasset_json(
            args.uassetgui,
            tojson=True,
            input_paths=[gathers_uasset_path, fishing_uasset_path],
            output_paths=[gathers_json_path, fishing_json_path],
        )

        gathers_asset = json_loads(gathers_json_path)
        patch_gathers_asset_json(gathers_asset, args.gather_factor)
        json_dumps(gathers_asset, gathers_json_path)

        fishing_asset = json_loads(fishing_json_path)
        patch_fishing_asset_json(fishing_asset, args.fishing_factor)
        json_dumps(fishing_asset, fishing_json_path)

        convert_uasset_json(
            args.uassetgui,
            tojson=False,
            input_paths=[gathers_json_path, fishing_json_path],
            output_paths=[gathers_uasset_path, fishing_uasset_path],
        )

        for it in (gathers_json_path, fishing_json_path):
            it.unlink(True)

        subprocess.run(
            log_cmd(
                [
                    args.repak,
                    "pack",
                    "--compression",
                    "Zlib",  # Zlib compression seems to work, even with the default V8B
                    workdir,
                ]
            ),
            check=True,
            capture_output=True,
        )

        shutil.move(workdir.parent.joinpath(f"{workdir.name}.pak"), output_path)

    print(f"Saved to '{output_path}'")
