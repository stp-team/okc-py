"""Pydantic models for Lines API."""

from pydantic import BaseModel, Field


class LineMessage(BaseModel):
    """Represents a line message from the day log.

    Attributes:
        message_text: The message content (may contain HTML)
        active_from: When the message was active from (format: DD.MM.YYYY HH:MM)
        fullname: Full name of the person who sent the message
    """

    message_text: str = Field(alias="MESSAGE_TEXT", description="Текст сообщения")
    active_from: str = Field(alias="ACTIVE_FROM", description="Дата сообщения")
    fullname: str = Field(alias="FIO", description="ФИО дежурного")


class Shift(BaseModel):
    """Represents a work shift.

    Attributes:
        employee_id: Employee ID
        shift_start: Shift start time (format: DD.MM.YYYY HH:MM)
        shift_end: Shift end time (format: DD.MM.YYYY HH:MM)
    """

    employee_id: str = Field(alias="EMPLOYEE_ID", description="ID сотрудника")
    shift_start: str = Field(alias="SHIFT_S", description="Начало смены")
    shift_end: str = Field(alias="SHIFT_E", description="Конец смены")


class Lunch(BaseModel):
    """Represents a lunch break.

    Attributes:
        lunch_start: Lunch start time (format: DD.MM.YYYY HH:MM)
        lunch_end: Lunch end time (format: DD.MM.YYYY HH:MM)
    """

    lunch_start: str = Field(alias="LUNCH_S", description="Начало обеда")
    lunch_end: str = Field(alias="LUNCH_E", description="Конец обеда")


class UserInfo(BaseModel):
    """Represents detailed user information.

    Attributes:
        birthday: User's birthday
        photo: Photo filename
        phone: Phone number
        social: Social network link
        person_id: Person ID
        employee_id: Employee ID
        fullname: Full name
        city_id: City ID
        city_name: City name
        post_id: Post/position ID
        post_name: Post/position name
        subdivision_id: Subdivision ID
        subdivision_name: Subdivision name
        email: Email address
        head_id: Head/manager ID
        head_fullname: Head/manager name
        finesse_id: Finesse ID
        unit_id: Unit ID
        unit_name: Unit name
        division_id: Division ID
    """

    #birthday: str = Field(alias="BIRTHDAY", description="Дата рождения")
    photo: str = Field(alias="PHOTO", description="Фотография")
    phone: str = Field(alias="PHONE", description="Телефон")
    social: str = Field(alias="SOCIAL", description="Социальная сеть")
    person_id: str = Field(alias="PERSON_ID", description="ID персоны")
    employee_id: str = Field(alias="EMPLOYEE_ID", description="ID сотрудника")
    fullname: str = Field(alias="USER_NAME", description="ФИО пользователя")
    city_id: str = Field(alias="CITY_ID", description="ID города")
    city_name: str = Field(alias="CITY_NAME", description="Название города")
    post_id: str = Field(alias="POST_ID", description="ID должности")
    post_name: str = Field(alias="POST_NAME", description="Название должности")
    subdivision_id: str = Field(alias="SUBDIVISION_ID", description="ID подразделения")
    subdivision_name: str = Field(
        alias="SUBDIVISION_NAME", description="Название подразделения"
    )
    email: str = Field(alias="EMAIL", description="Email")
    head_id: str = Field(alias="HEAD_ID", description="ID руководителя")
    head_fullname: str = Field(alias="HEAD_NAME", description="ФИО руководителя")
    finesse_id: str = Field(alias="FINESSE_ID", description="Finesse ID")
    unit_id: str = Field(alias="UNIT_ID", description="ID юнита")
    unit_name: str = Field(alias="UNIT_NAME", description="Название юнита")
    division_id: str = Field(alias="DIVISION_ID", description="ID дивизиона")


class UserData(BaseModel):
    """Represents complete user data including shifts and lunches.

    Attributes:
        data: Detailed user information
        shift: List of work shifts
        lunch: List of lunch breaks
    """

    data: UserInfo = Field(alias="userInfo", description="Информация о пользователе")
    shift: list[Shift] = Field(default_factory=list, description="Список смен")
    lunch: list[Lunch] = Field(default_factory=list, description="Список обедов")
