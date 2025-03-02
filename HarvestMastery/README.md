```
usage: main.py [-h] -i FILE [-o FILE] [-f] [--gather-factor FLOAT]
               [--fishing-factor INT] --uassetgui PATH --repak PATH

Multiply the resource and experience gain for some items in the Gathers table
by a factor

options:
  -h, --help            show this help message and exit
  -i, --input FILE      Path to the Game's '.pak' file
  -o, --output FILE
  -f, --force
  --gather-factor FLOAT
                        [default: 3] Multiplicative factor for resource and
                        experience gain on item gathering
  --fishing-factor INT  [default: 5] Multiplicative factor experience gain on
                        fishing
  --uassetgui PATH      Path to UAssetGUI
                        (https://github.com/atenfyr/UAssetGUI)
  --repak PATH          Path to trumank/repak
                        (https://github.com/trumank/repak)
```

