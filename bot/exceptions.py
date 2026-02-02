"""봇 예외 클래스 정의

명령어 처리 중 발생할 수 있는 예외들을 정의합니다.
"""


class BotException(Exception):
    """봇 기본 예외 클래스"""
    pass


class CharacterNotFoundException(BotException):
    """캐릭터를 찾을 수 없을 때 발생"""
    pass


class ItemNotFoundException(BotException):
    """아이템을 찾을 수 없을 때 발생"""
    pass


class ItemNotInInventoryException(BotException):
    """아이템이 인벤토리에 없을 때 발생"""
    pass


class InvalidInputException(BotException):
    """잘못된 입력이 제공되었을 때 발생"""
    pass


class DatabaseException(BotException):
    """데이터베이스 작업 중 오류 발생"""
    pass
