import keyring


def set_key(program: str, user: str, passw: str) -> None:
    keyring.set_password(program, user, passw)


def get_key(program: str, user: str) -> str:
    return keyring.get_password(program, user)


def rm_key(program: str, user: str) -> None:
    try:
        # Delete password from keyring
        keyring.delete_password(program, user)

    except (keyring.errors.PasswordDeleteError):
        # Already deleted
        pass
