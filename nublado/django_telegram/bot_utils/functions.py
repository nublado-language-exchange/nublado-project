from telegram import Message


def parse_command_last_arg_text(
    message: Message,
    maxsplit: int = 1
):
    """Returns the text for commands that receive text as its last arg"""
    # Message text is the command and given arguments (e.g., /command arg some text)
    message_text = message.text
    if maxsplit >= 1:
        command_and_args = message_text.split(None, maxsplit)
        if len(command_and_args) >= maxsplit + 1:
            arg_text = command_and_args[maxsplit]
            return arg_text
        else:
            return None
    else:
        return False
