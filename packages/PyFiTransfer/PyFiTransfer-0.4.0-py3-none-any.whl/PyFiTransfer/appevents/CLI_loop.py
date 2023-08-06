from msvcrt import getch

from PyFiTransfer.appevents.events import events, exit_program, logger


def CLI_loop() -> None:
    """CLI program event loop.

    ---

    :return: run CLI program.
    :rtype: None
    """

    origin: str = events._get_src_dir()
    logger.info(f'Got containing directory:\n>> "{origin}"\n')

    targetDir: str = events._get_dest_dir()
    logger.info(f'Got target destination:\n>> "{targetDir}"\n')

    fileExt: str = events._get_ext()
    logger.info(
        f'Got extension of files to be transferred:\n>> ".{fileExt}"\n')

    if events._verify_dir(origin) and events._verify_dir(targetDir):
        logger.info("Starting file transfer...\n")

        if not events.transfer(origin, targetDir, fileExt, gui=False):
            print('\nPress any key to exit...')
            getch()
            return exit_program.error("File transfer failed!")
        print('\nPress any key to exit...')
        getch()
        return exit_program.success()
    return exit_program.error(f'No files found with extension: "{fileExt}"')
