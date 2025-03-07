# Console Unlocker
A mod that unlocks the in-game dev-console.

## Usage
Press the **~** (Tilde) key to open the console.

### Commands
These are some of the commands:
```
additem     <ItemId> [Quantity]
addranditem <ItemId> [Quantity]     Add an item to the inventory with proper Extra Effects generated
addskill    <SkillId> [SkillLevel]
addjm       <MeridianPoints>        Add meridian points to the player
addmoney    <Money>
addsexp     <MartialPoints>         Add martial points to the player
setspeed    <Speed>                 Set the player's walk/run speed, can get reset with some world interactions
```

### Id List
- [Wandering Sword Item Ids v1.23.26](https://pastebin.com/9GmwrMbh)
- [Wandering Sword Skill Ids v1.23.26](https://pastebin.com/qYWMcHdc)

#### Extracting Id List
- Unpack the relevant `.locres` localization files from the Game's `.pak` file (`Wandering_Sword-WindowsNoEditor.pak`), using tools like [FModel](https://github.com/4sval/FModel), [repak](https://github.com/trumank/repak), or UnrealPak, etc.
- Which can then be exported to .csv using tools like [UnrealLocres](https://github.com/akintos/UnrealLocres).

- For example, here's the path to the Items and Skills localization files in the game's pak:
    ```
    Wandering_Sword/Content/Localization/Items道具表/en/Items道具表.locres
    Wandering_Sword/Content/Localization/Skills技能表/en/Skills技能表.locres
    ```
