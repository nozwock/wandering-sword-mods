```
usage: main.py [-h] -i FILE [-o FILE] [-f] [--factor FLOAT] [--uassetgui PATH]
               [--repak PATH]

Multiply the resource and experience gain for some items in the Gathers table
by a factor

options:
  -h, --help         show this help message and exit
  -i, --input FILE   Path to Game's '.pak' file or 'Gathers.json' exported
                     from it via UAssetGUI
  -o, --output FILE
  -f, --force
  --factor FLOAT     [default: 3] Multiplicative factor for resource and
                     experience gain on item gathering
  --uassetgui PATH   Path to UAssetGUI (https://github.com/atenfyr/UAssetGUI)
  --repak PATH       Path to trumank/repak (https://github.com/trumank/repak)
```
