from random import uniform
from time import sleep
from PyFiTransfer.appevents.events import events, exit_program, logger
from PyFiTransfer.appgui.gui import sg, window


def GUI_loop() -> None:
    """GUI program event loop.

    ---

    :return: run GUI program.
    :rtype: None
    """

    while True:
        event, vals = window.read()

        logger.info(f'{event} : {vals}')

        if event in [sg.WIN_CLOSED, 'Exit']:
            break

        if event == '-Transfer-':
            if len(vals['-SourceFolderInput-']) < 1:
                sg.Popup('Make sure all fields are filled out!')
                continue
            if len(vals['-TargetFolderInput-']) < 1:
                sg.Popup('Make sure all fields are filled out!')
                continue
            if len(vals['-FileExtensionInput-']) < 1:
                sg.Popup('Make sure all fields are filled out!')
                continue
            transfer: int = events.transfer(vals['-SourceFolderInput-'],
                                            vals['-TargetFolderInput-'],
                                            vals['-FileExtensionInput-'],
                                            gui=True)
            if transfer > 0:
                for _ in range(50):
                    window.refresh()
                    sleep(uniform(0.01, 0.25))
                    window['-ProgressBar-'].update(_ + 1)
                print(f'Successfully transferred {transfer} files!\n')
            window['-ProgressBar-'].update(0)

    window.close()

    return exit_program.success()
