RegisterKeyBind(Key.OEM_THREE --[[Tidle]], function ()
    local JHNeoUISubsystem = FindFirstOf("JHNeoUISubsystem")
    ExecuteInGameThread(function ()
        JHNeoUISubsystem:ShowGMCommandLine()
    end)
end)

