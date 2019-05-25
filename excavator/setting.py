from configparser import ConfigParser

cp = ConfigParser()
cp.read("./excavator/config.conf")


def ai_camp() -> int:
    section = cp.sections()[0]
    return int(cp.items(section)[0][1])
