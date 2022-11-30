from winregistry.robot.keywords import Keywords

ROBOT_LIBRARY_SCOPE = "GLOBAL"


class robot(Keywords):  # pylint: disable=invalid-name
    """
    Minimalist Python library aimed at working with Windows Registry.
    https://github.com/shpaker/winregistry
        Examples:
        | ${path}               | HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run |
        | Write Registry Entry  | ${path}           | Notepad | notepad.exe               |
        | ${autorun} =          | Read Registry Key | ${path} |                           |
        | Log                   | ${autorun}        |         |                           |
        | Delete Registry Entry | ${path}           | Notepad |                           |
    """
