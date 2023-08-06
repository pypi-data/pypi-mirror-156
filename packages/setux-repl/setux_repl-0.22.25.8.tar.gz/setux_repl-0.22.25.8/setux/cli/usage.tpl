{banner}

setux "config"
setux [Target] [Module | Manager | Command] [*args | **kwargs]

Deploy Module, Call Manager or Execute Command on Target


"config":
    Edit Setux Config


Target:
    May be set:
        - On the command line as the first arg
        - In the environement as "setux_target"
        - In the config dict as the "target" key
    defaults to "local"


Module, Manager or Command:
    - Deploy Module ( see the "modules" command )
        ex:
            deploy infos

    - Call Manager ( see the "managers" command)
        ex :
            pip installed

    - Get or Set Manager's Property
        ex :
            system hostname
            system hostname:server

    - Modules, as well as system, Package and Service managers can be shortcut
        ex:
            infos           <> deploy infos
            install vim     <> Package install vim
            restart ssh     <> Service restart ssh
            hostname        <> system hostname
            hostname:server <> system hostname:server

    - Execute Command ( see the "help" command )
        ex:
            run ps -ef
            edit /et/hostname

    - if not specified :
        enter REPL on Target
