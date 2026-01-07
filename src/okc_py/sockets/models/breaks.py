"""Модели для ответов сокета перерывов."""

import re
from html.parser import HTMLParser

from pydantic import BaseModel, Field


class BreakUser(BaseModel):
    """Пользователь на перерыве."""

    number: int = Field(description="Номер по порядку")
    fullname: str = Field(default="", description="ФИО сотрудника")
    start_time: str = Field(default="", description="Время начала перерыва")
    duration: str = Field(default="", description="Длительность перерыва")

    model_config = {"populate_by_name": True}


class DischargeUser(BaseModel):
    """Пользователь на разгрузке."""

    number: int = Field(description="Номер по порядку")
    fullname: str = Field(default="", description="ФИО сотрудника")
    start_time: str = Field(default="", description="Время начала разгрузки")
    duration: str = Field(default="", description="Длительность разгрузки")

    model_config = {"populate_by_name": True}


class QueueOperator(BaseModel):
    """Оператор в очереди."""

    number: int = Field(description="Номер по порядку")
    fullname: str = Field(default="name", description="ФИО сотрудника")
    delay: int = Field(default=0, description="Задержка")
    without_rest: str = Field(default="", description="Время без отдыха")
    spent: str = Field(default="", description="Потрачено времени")
    remaining: str = Field(default="", description="Осталось времени")
    allowed: str = Field(default="", description="Разрешено времени")
    avg_discharge_time: str = Field(default="", description="Среднее время разгрузки")

    model_config = {"populate_by_name": True}


class _TableRowParser(HTMLParser):
    """Простой парсер для извлечения данных из строк таблицы."""

    def __init__(self):
        super().__init__()
        self.in_td = False
        self.current_data = ""
        self.row_data: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.in_td = True
            self.current_data = ""

    def handle_endtag(self, tag):
        if tag == "td":
            self.in_td = False
            self.row_data.append(self.current_data.strip())

    def handle_data(self, data):
        if self.in_td:
            self.current_data += data

    def get_row_data(self, html: str) -> list[str]:
        """Парсит строку таблицы и возвращает список ячеек."""
        self.row_data = []
        self.feed(html)
        return self.row_data


class BreakLineData(BaseModel):
    """Данные о перерывах для линии.

    Содержит HTML таблицы с информацией о перерывах и разгрузках,
    а также числовые показатели доступных слотов.
    """

    table: str = Field(default="", description="HTML таблица перерывов")
    break_number: int = Field(
        alias="breakNumber", default=0, description="Количество доступных перерывов"
    )
    discharge: str = Field(default="", description="HTML таблица разгрузок")
    discharge_number: int = Field(
        alias="dischargeNumber", default=0, description="Количество доступных разгрузок"
    )
    open_discharges_count: int = Field(
        alias="openDischargesCount",
        default=0,
        description="Количество открытых разгрузок",
    )

    model_config = {"populate_by_name": True}

    def get_break_users(self) -> list[BreakUser]:
        """Парсит HTML таблицу перерывов и возвращает список пользователей.

        Returns:
            Список пользователей на перерыве
        """
        users: list[BreakUser] = []
        if not self.table:
            return users

        # Извлекаем строки таблицы
        rows = re.findall(r"<tr[^>]*>.*?</tr>", self.table, re.DOTALL)
        parser = _TableRowParser()

        for row in rows:
            # Пропускаем строки с colspan (это информационные строки)
            if "colspan" in row:
                continue

            cells = parser.get_row_data(row)
            if len(cells) >= 4:
                try:
                    number = int(cells[0]) if cells[0].isdigit() else 0
                    if number > 0:  # Пропускаем заголовки и пустые строки
                        users.append(
                            BreakUser(
                                number=number,
                                fullname=cells[1],
                                start_time=cells[2],
                                duration=cells[3],
                            )
                        )
                except (ValueError, IndexError):
                    continue

        return users

    def get_discharge_users(self) -> list[DischargeUser]:
        """Парсит HTML таблицу разгрузок и возвращает список пользователей.

        Returns:
            Список пользователей на разгрузке
        """
        users: list[DischargeUser] = []
        if not self.discharge:
            return users

        # Извлекаем строки таблицы
        rows = re.findall(r"<tr[^>]*>.*?</tr>", self.discharge, re.DOTALL)
        parser = _TableRowParser()

        for row in rows:
            # Пропускаем строки с colspan (это информационные строки)
            if "colspan" in row:
                continue

            cells = parser.get_row_data(row)
            if len(cells) >= 4:
                try:
                    number = int(cells[0]) if cells[0].isdigit() else 0
                    if number > 0:  # Пропускаем заголовки и пустые строки
                        users.append(
                            DischargeUser(
                                number=number,
                                fullname=cells[1],
                                start_time=cells[2],
                                duration=cells[3],
                            )
                        )
                except (ValueError, IndexError):
                    continue

        return users


class PageData(BaseModel):
    """Данные события pageData от WebSocket.

    Содержит полную информацию о перерывах по линиям и очереди операторов.
    Обновляется периодически при изменениях.
    """

    lines: dict[str, BreakLineData] = Field(
        default_factory=dict,
        description="Словарь с данными по линиям (line5, line10, line15)",
    )
    queue: str = Field(default="", description="HTML таблица очереди операторов")

    model_config = {"populate_by_name": True}

    def get_line(self, line_name: str) -> BreakLineData | None:
        """Получить данные для конкретной линии.

        Args:
            line_name: Имя линии (например, "line5", "line10", "line15")

        Returns:
            Данные линии или None, если линия не найдена
        """
        return self.lines.get(line_name)

    @property
    def line_names(self) -> list[str]:
        """Список названий доступных линий.

        Returns:
            Список имен линий
        """
        return list(self.lines.keys())

    def parse_queue_operators(self) -> list[QueueOperator]:
        """Парсит HTML таблицу очереди и возвращает список операторов.

        Returns:
            Список операторов в очереди
        """
        operators: list[QueueOperator] = []
        if not self.queue:
            return operators

        # Извлекаем строки таблицы
        rows = re.findall(r"<tr[^>]*>.*?</tr>", self.queue, re.DOTALL)
        parser = _TableRowParser()

        for row in rows:
            # Пропускаем строки с colspan (это заголовки)
            if "colspan" in row:
                continue

            cells = parser.get_row_data(row)
            if len(cells) >= 8:
                try:
                    number = int(cells[0]) if cells[0].isdigit() else 0
                    if number > 0:  # Пропускаем заголовки и пустые строки
                        operators.append(
                            QueueOperator(
                                number=number,
                                fullname=cells[1],
                                delay=int(cells[2]) if cells[2].isdigit() else 0,
                                without_rest=cells[3],
                                spent=cells[4],
                                remaining=cells[5],
                                allowed=cells[6],
                                avg_discharge_time=cells[7],
                            )
                        )
                except (ValueError, IndexError):
                    continue

        return operators

    def get_all_break_users(self) -> dict[str, list[BreakUser]]:
        """Получить всех пользователей на перерыве по всем линиям.

        Returns:
            Словарь {номер_линии: список_пользователей_на_перерыве}
        """
        result = {}
        for line_name, line_data in self.lines.items():
            result[line_name] = line_data.get_break_users()
        return result

    def get_all_discharge_users(self) -> dict[str, list[DischargeUser]]:
        """Получить всех пользователей на разгрузке по всем линиям.

        Returns:
            Словарь {номер_линии: список_пользователей_на_разгрузке}
        """
        result = {}
        for line_name, line_data in self.lines.items():
            result[line_name] = line_data.get_discharge_users()
        return result


class SimpleBreakLineData(BaseModel):
    """Данные о перерывах для линии (простой формат для ntp_one и ntp_two).

    Содержит только HTML таблицу с перерывами и количество доступных слотов.
    Используется для пространств имен ntp_one и ntp_two.
    """

    table: str = Field(default="", description="HTML таблица перерывов")
    break_number: int = Field(
        alias="breakNumber", default=0, description="Количество доступных перерывов"
    )

    model_config = {"populate_by_name": True}

    def get_break_users(self) -> list[BreakUser]:
        """Парсит HTML таблицу перерывов и возвращает список пользователей.

        Returns:
            Список пользователей на перерыве
        """
        users: list[BreakUser] = []
        if not self.table:
            return users

        # Извлекаем строки таблицы
        rows = re.findall(r"<tr[^>]*>.*?</tr>", self.table, re.DOTALL)
        parser = _TableRowParser()

        for row in rows:
            # Пропускаем строки с colspan (это информационные строки)
            if "colspan" in row:
                continue

            cells = parser.get_row_data(row)
            if len(cells) >= 4:
                try:
                    number = int(cells[0]) if cells[0].isdigit() else 0
                    if number > 0:  # Пропускаем заголовки и пустые строки
                        users.append(
                            BreakUser(
                                number=number,
                                fullname=cells[1],
                                start_time=cells[2],
                                duration=cells[3],
                            )
                        )
                except (ValueError, IndexError):
                    continue

        return users


class SimplePageData(BaseModel):
    """Данные события pageData от WebSocket (простой формат для ntp_one и ntp_two).

    Содержит упрощенную информацию о перерывах по линиям и очереди операторов,
    а также информацию о finesse серверах.
    Используется для пространств имен ntp_one и ntp_two.
    """

    lines: dict[str, SimpleBreakLineData] = Field(
        default_factory=dict,
        description="Словарь с данными по линиям (line5, line10, line15)",
    )
    queue: str = Field(default="", description="HTML таблица очереди операторов")
    finesse_check: str = Field(
        alias="finesseCheck", default="", description="Статус смены статусов"
    )
    finesse_server: str = Field(
        alias="finesseServer", default="", description="Информация о серверах Finesse"
    )

    model_config = {"populate_by_name": True}

    def get_line(self, line_name: str) -> SimpleBreakLineData | None:
        """Получить данные для конкретной линии.

        Args:
            line_name: Имя линии (например, "line5", "line10", "line15")

        Returns:
            Данные линии или None, если линия не найдена
        """
        return self.lines.get(line_name)

    @property
    def line_names(self) -> list[str]:
        """Список названий доступных линий.

        Returns:
            Список имен линий
        """
        return list(self.lines.keys())

    def parse_queue_operators(self) -> list[QueueOperator]:
        """Парсит HTML таблицу очереди и возвращает список операторов.

        Returns:
            Список операторов в очереди
        """
        operators: list[QueueOperator] = []
        if not self.queue:
            return operators

        # Извлекаем строки таблицы
        rows = re.findall(r"<tr[^>]*>.*?</tr>", self.queue, re.DOTALL)
        parser = _TableRowParser()

        for row in rows:
            # Пропускаем строки с colspan (это заголовки)
            if "colspan" in row:
                continue

            cells = parser.get_row_data(row)
            # ntp_one/ntp_two have 7 columns (no avg_discharge_time)
            if len(cells) >= 7:
                try:
                    number = int(cells[0]) if cells[0].isdigit() else 0
                    if number > 0:  # Пропускаем заголовки и пустые строки
                        operators.append(
                            QueueOperator(
                                number=number,
                                fullname=cells[1],
                                delay=int(cells[2]) if cells[2].isdigit() else 0,
                                without_rest=cells[3],
                                spent=cells[4],
                                remaining=cells[5],
                                allowed=cells[6],
                                avg_discharge_time="",  # Not available for ntp_one/ntp_two
                            )
                        )
                except (ValueError, IndexError):
                    continue

        return operators

    def get_all_break_users(self) -> dict[str, list[BreakUser]]:
        """Получить всех пользователей на перерыве по всем линиям.

        Returns:
            Словарь {номер_линии: список_пользователей_на_перерыве}
        """
        result = {}
        for line_name, line_data in self.lines.items():
            result[line_name] = line_data.get_break_users()
        return result


class AuthMessage(BaseModel):
    """Данные события authMessage от WebSocket.

    Содержит информацию об авторизованном пользователе.
    """

    user_name: str = Field(alias="userName", default="", description="Имя пользователя")
    is_super_user: bool = Field(
        alias="isSuperUser",
        default=False,
        description="Является ли супер-пользователем",
    )

    model_config = {"populate_by_name": True}


class UserBreaks(BaseModel):
    """Данные события userBreaks от WebSocket.

    Содержит количество перерывов пользователя по линиям.
    """

    breaks_5: int = Field(alias="line5", default=0, description="5-минутных перерывов")
    breaks_10: int = Field(
        alias="line10", default=0, description="10-минутных перерывов"
    )
    breaks_15: int = Field(
        alias="line15", default=0, description="15-минутных перерывов"
    )

    model_config = {"populate_by_name": True}

    @property
    def total(self) -> int:
        """Общее количество перерывов.

        Returns:
            Сумма перерывов по всем линиям
        """
        return self.breaks_5 + self.breaks_10 + self.breaks_15
