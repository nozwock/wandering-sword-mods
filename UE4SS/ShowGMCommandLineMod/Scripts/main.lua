local UEHelpers = require("UEHelpers")


-- See Mods/Keybinds/Scripts/main.lua for other valid keys that can be used
local consoleToggleKey = Key.F1


---@param msg string
local function Log(msg)
	print("[ShowGMCommandLine] " .. msg)
end

--- Runs callback once PlayerController is available
---@param InitCallback function
local function RegisterMod(InitCallback)
	if pcall(UEHelpers.GetPlayerController) then
		-- For hot-reloading
		InitCallback()
	else
		local InitHookIds
		local PreId, PostId = RegisterHook("/Script/Engine.PlayerController:ClientRestart", function()
			if InitHookIds then
				UnregisterHook("/Script/Engine.PlayerController:ClientRestart", table.unpack(InitHookIds))
			else
				Log("Failed to unregister Init hook")
			end

			InitCallback()
		end)

		InitHookIds = { PreId, PostId }
	end
end


RegisterMod(function()
	local JHNeoUISubsystem = StaticFindObject("/Script/JH.Default__JHNeoUISubsystem")
	assert(JHNeoUISubsystem:IsValid())

	RegisterKeyBind(consoleToggleKey, function()
		ExecuteInGameThread(function()
			JHNeoUISubsystem:ShowGMCommandLine()
		end)
	end)
end)
