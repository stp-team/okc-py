from pydantic import BaseModel, Field


class TestCategory(BaseModel):
    """Модель категории тестов."""

    id: str = Field(description="Идентификатор категории")
    name: str = Field(description="Название категории")


class TestTheme(BaseModel):
    """Модель темы теста."""

    id: str = Field(description="Идентификатор темы")
    name: str = Field(description="Название темы")
    question_count: int = Field(description="Количество вопросов в теме")


class TestDetailedTheme(BaseModel):
    """Детальная модель темы с категориями."""

    id: str = Field(description="Идентификатор темы")
    name: str = Field(description="Название темы")
    description: str | None = Field(description="Описание темы")
    question_count: int = Field(description="Количество вопросов в теме")
    categories: list[str] = Field(description="Список идентификаторов категорий")


class Test(BaseModel):
    """Модель теста."""

    id: str = Field(description="Идентификатор теста")
    name: str = Field(description="Название теста")
    description: str | None = Field(description="Описание теста")
    success_percent: int = Field(description="Процент успешного прохождения")
    lifetime_days: int = Field(description="Время жизни теста в днях")
    time_limit_type_id: int = Field(
        description="Идентификатор типа ограничения времени"
    )
    time_limit_value: int = Field(description="Значение ограничения времени")
    time_limit_description: str = Field(description="Описание ограничения времени")
    themes: list[TestTheme] = Field(description="Список тем теста")


class AssignedTest(BaseModel):
    """Модель для назначенного теста."""

    id: str = Field(description="Идентификатор теста")
    test_name: str = Field(description="Название теста")
    user_name: str = Field(description="ФИО пользователя")
    head_name: str | None = Field(description="ФИО руководителя")
    creator_name: str | None = Field(description="ФИО создателя теста")
    status_name: str = Field(description="Статус теста")
    active_from: str = Field(description="Дата назначения теста")
    start_date: str | None = Field(description="Дата начала теста")


class TestsSubdivision(BaseModel):
    """Модель подразделения."""

    id: str = Field(description="Идентификатор подразделения")
    name: str = Field(description="Название подразделения")
    units: list[str | None] = Field(description="Список идентификаторов подразделений")


class TestsUser(BaseModel):
    """Модель пользователя."""

    id: str = Field(description="Идентификатор пользователя")
    name: str = Field(description="ФИО пользователя")
    head: str | None = Field(description="Идентификатор руководителя")
    subdivision: str = Field(description="Идентификатор подразделения")
    unit: str | None = Field(description="Идентификатор подразделения")


class TestsSupervisor(BaseModel):
    """Модель руководителя."""

    id: str = Field(description="Идентификатор руководителя")
    name: str = Field(description="ФИО руководителя")
    head: str | None = Field(description="Идентификатор вышестоящего руководителя")
    subdivision: str = Field(description="Идентификатор подразделения")
    unit: str | None = Field(description="Идентификатор подразделения")
