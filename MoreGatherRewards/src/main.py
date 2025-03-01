import json
import platform
import shutil
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from functools import reduce
from pathlib import Path


def is_file(path: Path, parser: ArgumentParser):
    if not path.is_file():
        parser.error(f"File not found '{path}'")


def patch_asset_json(asset_table: dict):
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
                        num_obj = reduce(
                            lambda _, it: it if it["Name"] == "Num" else None,
                            action_setting["Value"],
                            None,
                        )
                        if num_obj and num_obj["Value"] > 0:
                            num_obj["Value"] = num_obj["Value"] * args.factor

                break


def convert_uasset_json(
    uassetgui: Path,
    tojson: bool,
    input_path: Path,
    output_path: Path,
    version: tuple[int, int] = (4, 26),
):
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

            subprocess.run(
                ["wine"] + args,
                check=True,
            )
        case "Windows":
            subprocess.run(
                args,
                check=True,
            )
        case _:
            raise Exception("Unsupported system")


if __name__ == "__main__":
    script_dir = Path(__file__).absolute().parent

    parser = ArgumentParser(
        description="Multiply the resource and experience gain for some items in the Gathers table by a factor"
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="FILE",
        required=True,
        type=Path,
        help="Path to Game's '.pak' file or 'Gathers.json' exported from it via UAssetGUI",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        type=Path,
    )
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument(
        "--factor",
        metavar="FLOAT",
        default=3,
        type=float,
        help="[default: 3] Multiplicative factor for resource and experience gain on item gathering",
    )
    parser.add_argument(
        "--uassetgui",
        metavar="PATH",
        type=Path,
        help="Path to UAssetGUI (https://github.com/atenfyr/UAssetGUI)",
    )
    parser.add_argument(
        "--repak",
        metavar="PATH",
        type=Path,
        help="Path to trumank/repak (https://github.com/trumank/repak)",
    )

    args = parser.parse_args()
    is_file(args.input, parser)

    output_path = args.output or Path(f"{args.input.stem}.Patched{args.input.suffix}")

    if output_path.exists() and not args.force:
        parser.error(f"File already exists '{output_path}'")

    match args.input.suffix.lower().strip("."):
        case "json":
            gathers: dict
            with open(
                args.input,
                encoding="utf-8-sig",
            ) as f:
                gathers = json.loads(f.read())

            patch_asset_json(gathers)

            with open(output_path, "wb") as f:
                f.write(json.dumps(gathers, ensure_ascii=False, indent=2).encode())
        case "pak":
            pak_required_msg = "required to process '.pak' files:"
            if not args.uassetgui:
                parser.error(f"{pak_required_msg} --uassetgui")
            is_file(args.uassetgui, parser)

            if not args.repak:
                parser.error(f"{pak_required_msg} --repak")
            is_file(args.repak, parser)

            gathers_dir = "Wandering_Sword/Content/JH/Tables"
            with tempfile.TemporaryDirectory() as workdir:
                workdir = Path(workdir)
                subprocess.run(
                    [
                        args.repak,
                        "unpack",
                        "-f",
                        "-i",
                        f"{gathers_dir}/Gathers.*",
                        "-o",
                        workdir,
                        args.input,
                    ],
                    check=True,
                )

                gathers_uasset_path = workdir.joinpath(gathers_dir).joinpath(
                    "Gathers.uasset"
                )
                gathers_json_path = workdir.joinpath("Gathers.json")

                convert_uasset_json(
                    args.uassetgui,
                    tojson=True,
                    input_path=gathers_uasset_path,
                    output_path=gathers_json_path,
                )

                gather: dict
                with open(
                    gathers_json_path,
                    encoding="utf-8-sig",
                ) as f:
                    gathers = json.loads(f.read())

                patch_asset_json(gathers)

                with open(gathers_json_path, "wb") as f:
                    f.write(json.dumps(gathers, ensure_ascii=False, indent=2).encode())

                convert_uasset_json(
                    args.uassetgui,
                    tojson=False,
                    input_path=gathers_json_path,
                    output_path=gathers_uasset_path,
                )

                gathers_json_path.unlink(True)

                # note: Not using compression since that seem to break the pak generated by repak
                subprocess.run(
                    [
                        args.repak,
                        "pack",
                        workdir,
                    ],
                    check=True,
                )

                shutil.move(workdir.parent.joinpath(f"{workdir.name}.pak"), output_path)
        case _:
            parser.error(f"Can't handle file of type '{args.input.suffix}'")

    print(f"Saved to '{output_path}'", file=sys.stderr)
