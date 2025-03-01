local PlayerNpcId = 0
local NpcIds = {
    ["mowen"] = 5015,
    ["xiaotong"] = 8500,
    ["ouyangxue"] = 17005,
    ["yaoji"] = 17115,
}

-- No fuzzy, just simple substring startswith
---@param s string
---@return number?
local function FindFirstNpc(s)
    s = "^" .. string.gsub(s, "%W", "") -- keep only alphanum
    local matchedId, maxSubstringLen
    for name, id in pairs(NpcIds) do
        if string.match(name, s) then
            if matchedId then
                if #s > maxSubstringLen then
                    matchedId, maxSubstringLen = id, #s
                end
            else
                matchedId, maxSubstringLen = id, #s
            end
        end
    end

    return matchedId
end

local function CommandErrToDevice(ErrMsg, Usage, Device)
    Device:Log(string.format("Error: %s\n%s", ErrMsg, Usage))
end

local NPCFuncLib
NPCFuncLib = FindFirstOf("NPCFuncLib")
if not NPCFuncLib:IsValid() then
    NPCFuncLib = StaticConstructObject(
        StaticFindObject("/Script/JH.NPCFuncLib"),
        StaticFindObject("/Script/Engine.BlueprintFunctionLibrary")
    )
end

local Commands = {
    ChangeAffinity = {
        name = "changeaffinity",
        usage = "Usage: changeaffinity {NpcId|NpcName} [AffinityDelta]",
        callback = function (self, _, Args, Device)
            -- todo: Maybe only have the commands be run when the player isn't in main menu
            if #Args < 1 or #Args > 2 then
                CommandErrToDevice("Invalid command usage", self.usage, Device)
                return true
            end

            if #Args == 1 then
                table.insert(Args, 10)
            end

            if not tonumber(Args[1]) then -- if arg isn't a number
                Args[1] = FindFirstNpc(Args[1])
                if not Args[1] then
                    CommandErrToDevice("No such NPC found", self.usage, Device)
                    return true
                end
            end

            local NPCManager = FindFirstOf("NPCManager")
            if not NPCManager:IsValid() then
                CommandErrToDevice("Failed to access required Objects", self.usage, Device)
                return true
            end

            for i = 1, math.min(2, #Args) do
                Args[i] = tonumber(Args[i])
            end

            if not (Args[1] and Args[2]) then
                CommandErrToDevice("Improper argument types", self.usage, Device)
                return true
            end

            NPCManager:ChangeFriendliness(Args[1], PlayerNpcId, Args[2], true)

            return true
        end
    },
    GetAffinity = {
        name = "getaffinity",
        usage = "Usage: getaffinity {NpcId|NpcName}",
        callback = function (self, _, Args, Device)
            if #Args ~= 1  then
                CommandErrToDevice("Invalid command usage", self.usage, Device)
                return true
            end

            local NPCManager = FindFirstOf("NPCManager")
            if not NPCManager:IsValid() or not NPCFuncLib:IsValid() then
                CommandErrToDevice("Failed to access required Objects", self.usage, Device)
                return true
            end

            if not tonumber(Args[1]) then -- if arg isn't a number
                Args[1] = FindFirstNpc(Args[1])
                if not Args[1] then
                    CommandErrToDevice("No such NPC found", self.usage, Device)
                    return true
                end
            else
                Args[1] = tonumber(Args[1])
            end

            if not Args[1] then
                CommandErrToDevice("Improper argument types", self.usage, Device)
                return true
            end

            Device:Log(string.format(
                "%s Affinity: %s",
                NPCFuncLib:GetNPCNameById(Args[1]):ToString(),
                tostring(NPCManager:GetFriendliness(Args[1]))
            ))

            return true
        end
    }
}

for _, command in pairs(Commands) do
    RegisterConsoleCommandHandler(command.name, function (_, Args, Device)
        return command:callback(_, Args, Device)
    end)
end

