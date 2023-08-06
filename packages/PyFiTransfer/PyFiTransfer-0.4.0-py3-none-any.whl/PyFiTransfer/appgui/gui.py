import PySimpleGUI as sg

layout: list = [
    [sg.Text('PyFiTransfer')], [sg.HSeparator()],
    [
        sg.Text('Source Directory:', s=(12, 1)),
        sg.VSeperator(),
        sg.Input(key='-SourceFolderInput-', expand_x=True),
        sg.VSeperator(),
        sg.FolderBrowse(
            key='-SourceFolder-',
            target=(sg.ThisRow, -2),
            tooltip=
            'Browse for directory containing the files you wish to transfer.')
    ],
    [
        sg.Text('File Destination:', s=(12, 1)),
        sg.VSeperator(),
        sg.Input(key='-TargetFolderInput-', expand_x=True),
        sg.VSeperator(),
        sg.FolderBrowse(
            key='-TargetFolder-',
            target=(sg.ThisRow,
                    -2),
            tooltip='Browse for target directory you wish to transfer files to.'
        )
    ],
    [
        sg.Text('File Extension:', s=(12, 1)),
        sg.VSeperator(),
        sg.Input(key='-FileExtensionInput-', expand_x=True),
    ],
    [
        sg.Button('Start Transfer',
                  key='-Transfer-',
                  button_color=('white', 'green'))
    ],
    [
        sg.ProgressBar(max_value=50,
                       size=(30, 10),
                       orientation='horizontal',
                       key='-ProgressBar-',
                       expand_x=True)
    ], [sg.HSeparator()],
    [
        sg.Multiline(s=(30, 30),
                     expand_x=True,
                     expand_y=True,
                     disabled=True,
                     key='-Log-',
                     reroute_stdout=True,
                     write_only=True,
                     auto_refresh=True,
                     autoscroll=True)
    ], [sg.HSeparator()], [sg.Exit(button_color=('white', 'firebrick4'))]
]

window: sg.Window = sg.Window('PyFiTransfer',
                              layout,
                              auto_size_buttons=True,
                              text_justification='c',
                              element_justification='c')
