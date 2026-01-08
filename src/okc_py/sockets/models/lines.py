"""Модели для ответов сокета линии."""

from pydantic import BaseModel, Field


class LineStatus(BaseModel):
    """Текущий статус линии."""

    line_id: str = Field(description="Идентификатор линии")
    status: str = Field(description="Статус линии (online/offline/queued)")
    agents_online: int = Field(description="Количество агентов онлайн")
    calls_waiting: int = Field(description="Количество звонков в ожидании")
    timestamp: str | None = Field(
        default=None, description="Временная метка последнего обновления"
    )


class LineStats(BaseModel):
    """Статистика линии за период."""

    line_id: str = Field(description="Идентификатор линии")
    total_calls: int = Field(description="Общее количество звонков")
    answered_calls: int = Field(description="Количество ответивших звонков")
    abandoned_calls: int = Field(description="Количество пропущенных звонков")
    avg_wait_time: float = Field(description="Среднее время ожидания")
    avg_talk_time: float = Field(description="Среднее время разговора")


class QueueInfo(BaseModel):
    """Информация об очереди в rawData."""

    current_waiting_calls: int = Field(
        default=0, description="Текущее количество ожидающих звонков"
    )
    total_entered_calls: int = Field(
        default=0, description="Общее количество поступивших звонков"
    )
    max_wait_time: int = Field(default=0, description="Максимальное время ожидания")
    dep_name: str = Field(default="", description="Название отдела")
    table_order: int = Field(default=0, description="Порядковый номер в таблице")
    sort_order: int = Field(default=0, description="Порядок сортировки")
    duration_str: str = Field(default="", description="Длительность в формате ЧЧ:ММ:СС")

    model_config = {"populate_by_name": True}


class ChatCapacityInfo(BaseModel):
    """Информация о вместимости чатов."""

    available: int = Field(default=0, description="Доступно слотов")
    max: int = Field(default=0, description="Максимум слотов")

    model_config = {"populate_by_name": True}


class WaitingChats(BaseModel):
    """Информация о ожидающих чатах."""

    lvl1: int = Field(default=0, description="Чаты LVL1 в ожидании")
    lvl2: int = Field(default=0, description="Чаты LVL2 в ожидании")
    lvl3: int = Field(default=0, description="Чаты LVL3 в ожидании")


class ChatCapacity(BaseModel):
    """Вместимость чатов по уровням."""

    lvl1: ChatCapacityInfo = Field(
        default_factory=ChatCapacityInfo, description="Вместимость LVL1"
    )
    lvl2: ChatCapacityInfo = Field(
        default_factory=ChatCapacityInfo, description="Вместимость LVL2"
    )
    lvl3: ChatCapacityInfo = Field(
        default_factory=ChatCapacityInfo, description="Вместимость LVL3"
    )


class Agent(BaseModel):
    """Базовая модель агента."""

    USER_ID: int = Field(default=0, description="ID пользователя")
    USER_NAME: str = Field(default="", description="Полное имя пользователя")
    SHORT_USER_NAME: str = Field(default="", description="Краткое имя пользователя")
    SUBDIVISION_ID: int = Field(default=0, description="ID подразделения")
    EMPLOYEE_ID: str = Field(default="", description="Табельный номер")
    HEAD_ID: int = Field(default=0, description="ID руководителя")
    HEAD_NAME: str = Field(default="", description="Имя руководителя")
    LINE: int = Field(default=1, description="Линия (1-3)")
    IS_EXPERT: int = Field(default=0, description="Является экспертом (0/1)")
    TRAINEE_TYPE: int | None = Field(default=None, description="Тип стажера")
    SKILL_ID: int = Field(default=0, description="ID навыка")
    HAS_DUTY_SKILL: int | None = Field(default=None, description="Есть дежурный навык")
    hasEmailStatus: bool = Field(default=False, description="Есть email статус")

    model_config = {"populate_by_name": True}


class ReadyAgent(Agent):
    """Готовый к работе агент."""

    SHIFT_RECORD_ID: int | None = Field(default=None, description="ID записи смены")
    SHIFT_START: str | None = Field(default=None, description="Начало смены")
    SHIFT_END: str | None = Field(default=None, description="Конец смены")
    SHIFT_START_SPEC: str | None = Field(default=None, description="Начало смены (ISO)")
    SHIFT_END_SPEC: str | None = Field(default=None, description="Конец смены (ISO)")
    SHIFT_TYPE: int | None = Field(default=None, description="Тип смены")
    statusStart: int = Field(
        default=0, description="Время начала статуса (unix timestamp)"
    )
    chatStatusId: int = Field(default=0, description="ID статуса чата")
    emailStatusId: int = Field(default=0, description="ID статуса email")
    currentChat: int = Field(default=0, description="Текущее количество чатов")
    maxChat: int = Field(default=0, description="Максимум чатов")
    marginChat: int = Field(default=0, description="Запас чатов")
    chat: str = Field(default="", description="Статус чата")
    agentBlock: str = Field(default="", description="Блок агента")
    onDischarge: bool = Field(default=False, description="На разгрузке")
    durationStr: str = Field(default="", description="Длительность статуса")
    onShift: bool = Field(default=False, description="На смене")
    sortOrder: int = Field(default=0, description="Порядок сортировки")
    currentEmail: int | None = Field(
        default=None, description="Текущее количество email"
    )


class NotReadyAgent(Agent):
    """Агент не готов к работе."""

    statusStart: int = Field(
        default=0, description="Время начала статуса (unix timestamp)"
    )
    chatStatusId: int = Field(default=0, description="ID статуса чата")
    emailStatusId: int = Field(default=0, description="ID статуса email")
    notReadyReason: str = Field(default="", description="Причина неготовности")
    currentChat: int = Field(default=0, description="Текущее количество чатов")
    maxChat: int = Field(default=0, description="Максимум чатов")
    marginChat: int = Field(default=0, description="Запас чатов")
    currentEmail: int | None = Field(
        default=None, description="Текущее количество email"
    )
    chat: str = Field(default="", description="Статус чата")
    email: str | None = Field(default=None, description="Статус email")
    agentBlock: str = Field(default="", description="Блок агента")
    onDischarge: bool = Field(default=False, description="На разгрузке")
    durationStr: str = Field(default="", description="Длительность статуса")
    onShift: bool = Field(default=False, description="На смене")


class AssignAgent(Agent):
    """Агент на назначении."""

    SHIFT_RECORD_ID: int = Field(default=0, description="ID записи смены")
    SHIFT_START: str = Field(default="", description="Начало смены")
    SHIFT_END: str = Field(default="", description="Конец смены")
    SHIFT_START_SPEC: str = Field(default="", description="Начало смены (ISO)")
    SHIFT_END_SPEC: str = Field(default="", description="Конец смены (ISO)")
    SHIFT_TYPE: int = Field(default=0, description="Тип смены")
    ASSIGNMENT_START_SPEC: str = Field(
        default="", description="Начало назначения (ISO)"
    )
    ASSIGNMENT_END_SPEC: str = Field(default="", description="Конец назначения (ISO)")
    ASSIGNMENT_START: str = Field(default="", description="Начало назначения")
    ASSIGNMENT_END: str = Field(default="", description="Конец назначения")
    ASSIGN_RECORD_ID: int = Field(default=0, description="ID записи назначения")
    ASSIGN_TYPE_ID: int = Field(default=0, description="Тип назначения")
    ASSIGN_SUBTYPE_ID: int = Field(default=0, description="Подтип назначения")
    REASON: str = Field(default="", description="Причина")
    INFO: str | None = Field(default=None, description="Дополнительная информация")
    statusStart: int = Field(
        default=0, description="Время начала статуса (unix timestamp)"
    )
    chatStatusId: int = Field(default=0, description="ID статуса чата")
    emailStatusId: int = Field(default=0, description="ID статуса email")
    agentBlock: str = Field(default="", description="Блок агента")
    onDischarge: bool = Field(default=False, description="На разгрузке")
    durationStr: str = Field(default="", description="Длительность статуса")
    onShift: bool = Field(default=False, description="На смене")
    currentChat: int | None = Field(
        default=None, description="Текущее количество чатов"
    )
    maxChat: int | None = Field(default=None, description="Максимум чатов")
    marginChat: int | None = Field(default=None, description="Запас чатов")
    chat: str | None = Field(default=None, description="Статус чата")
    currentEmail: int | None = Field(
        default=None, description="Текущее количество email"
    )
    hasEmailStatus: bool | None = Field(default=None, description="Есть email статус")


class BreakAgent(Agent):
    """Агент на перерыве."""

    statusStart: int = Field(
        default=0, description="Время начала статуса (unix timestamp)"
    )
    chatStatusId: int = Field(default=0, description="ID статуса чата")
    emailStatusId: int = Field(default=0, description="ID статуса email")
    notReadyReason: str = Field(default="", description="Причина неготовности")
    currentChat: int = Field(default=0, description="Текущее количество чатов")
    maxChat: int = Field(default=0, description="Максимум чатов")
    marginChat: int = Field(default=0, description="Запас чатов")
    breakStart: str = Field(default="", description="Начало перерыва")
    breakEnd: str = Field(default="", description="Конец перерыва")
    chat: str = Field(default="", description="Статус чата")
    agentBlock: str = Field(default="", description="Блок агента")
    onDischarge: bool = Field(default=False, description="На разгрузке")
    durationStr: str = Field(default="", description="Длительность статуса")
    onShift: bool = Field(default=False, description="На смене")


class Agents(BaseModel):
    """Все агенты по статусам."""

    readyAgents: list[ReadyAgent] = Field(
        default_factory=list, description="Готовые агенты"
    )
    notReadyAgents: list[NotReadyAgent] = Field(
        default_factory=list, description="Не готовые агенты"
    )
    discreteAgents: list[dict] = Field(
        default_factory=list, description="Дискретные агенты"
    )
    assignAgents: list[AssignAgent] = Field(
        default_factory=list, description="Агенты на назначении"
    )
    breakAgents: list[BreakAgent] = Field(
        default_factory=list, description="Агенты на перерыве"
    )

    model_config = {"populate_by_name": True}


class LineDuty(BaseModel):
    """Дежурный по линии."""

    EMPLOYEE_ID: int = Field(default=0, description="Табельный номер")
    FIO: str = Field(default="", description="ФИО")
    EMAIL: str = Field(default="", description="Email")
    DUTY_TYPE_ID: int = Field(default=0, description="Тип дежурства")
    DUTY_TYPE_NAME: str = Field(default="", description="Название типа дежурства")
    IN_CHARGE: int = Field(default=0, description="Ответственный (0/1)")

    model_config = {"populate_by_name": True}


class LastMessage(BaseModel):
    """Последнее сообщение."""

    author: str = Field(default="", description="Автор сообщения")
    date: str = Field(default="", description="Дата сообщения")
    message: str = Field(default="", description="Текст сообщения")

    model_config = {"populate_by_name": True}


class CityInQueue(BaseModel):
    """Город в очереди."""

    cities: list = Field(default_factory=list, description="Список городов")
    total: int = Field(default=0, description="Общее количество")

    model_config = {"populate_by_name": True}


class CityWithChats(BaseModel):
    """Город с количеством чатов."""

    chatsInProcessing: int = Field(default=0, description="Чатов в обработке")
    city: str = Field(default="", description="Название города")

    model_config = {"populate_by_name": True}


class CitiesInProcess(BaseModel):
    """Города в обработке."""

    cities: list[CityWithChats] = Field(
        default_factory=list, description="Список городов"
    )
    total: int = Field(default=0, description="Общее количество")

    model_config = {"populate_by_name": True}


class CityStatus(BaseModel):
    """Статус города."""

    DHCP_chat: str = Field(default="", description="Статус DHCP чата")
    Mobile_chat: str = Field(default="", description="Статус Mobile чата")
    SmartDom_chat: str = Field(default="", description="Статус SmartDom чата")
    Web_chat: str = Field(default="", description="Статус Web чата")
    all: str = Field(default="", description="Общий статус")
    ruName: str | None = Field(default=None, description="Русское название города")

    model_config = {"populate_by_name": True}


class CitiesStatuses(BaseModel):
    """Статусы городов."""

    all: CityStatus = Field(
        default_factory=CityStatus, description="Статус всех городов"
    )
    angarsk: CityStatus = Field(default_factory=CityStatus, description="Ангарск")
    barnaul: CityStatus = Field(default_factory=CityStatus, description="Барнаул")
    bryansk: CityStatus = Field(default_factory=CityStatus, description="Брянск")
    cheb: CityStatus = Field(default_factory=CityStatus, description="Чебоксары")
    chel: CityStatus = Field(default_factory=CityStatus, description="Челябинск")
    chelny: CityStatus = Field(
        default_factory=CityStatus, description="Набережные Челны"
    )
    dzr: CityStatus = Field(default_factory=CityStatus, description="Дзержинск")
    ekat: CityStatus = Field(default_factory=CityStatus, description="Екатеринбург")
    hq: CityStatus = Field(default_factory=CityStatus, description="HQ")
    interzet: CityStatus = Field(default_factory=CityStatus, description="СПБ-Izet")
    irkutsk: CityStatus = Field(default_factory=CityStatus, description="Иркутск")
    izhevsk: CityStatus = Field(default_factory=CityStatus, description="Ижевск")
    kazan: CityStatus = Field(default_factory=CityStatus, description="Казань")
    kirov: CityStatus = Field(default_factory=CityStatus, description="Киров")
    krd: CityStatus = Field(default_factory=CityStatus, description="Краснодар")
    krsk: CityStatus = Field(default_factory=CityStatus, description="Красноярск")
    kurgan: CityStatus = Field(default_factory=CityStatus, description="Курган")
    kursk: CityStatus = Field(default_factory=CityStatus, description="Курск")
    lipetsk: CityStatus = Field(default_factory=CityStatus, description="Липецк")
    mgn: CityStatus = Field(default_factory=CityStatus, description="Магнитогорск")
    mich: CityStatus = Field(default_factory=CityStatus, description="Мичуринск")
    moscow: CityStatus = Field(default_factory=CityStatus, description="Москва")
    msk: CityStatus = Field(default_factory=CityStatus, description="Москва")
    nn: CityStatus = Field(default_factory=CityStatus, description="Нижний Новгород")
    nsk: CityStatus = Field(default_factory=CityStatus, description="Новосибирск")
    omsk: CityStatus = Field(default_factory=CityStatus, description="Омск")
    oren: CityStatus = Field(default_factory=CityStatus, description="Оренбург")
    penza: CityStatus = Field(default_factory=CityStatus, description="Пенза")
    perm: CityStatus = Field(default_factory=CityStatus, description="Пермь")
    rinet: CityStatus = Field(default_factory=CityStatus, description="Москва-Ринет")
    rostov: CityStatus = Field(default_factory=CityStatus, description="Ростов")
    ryazan: CityStatus = Field(default_factory=CityStatus, description="Рязань")
    samara: CityStatus = Field(default_factory=CityStatus, description="Самара")
    saratov: CityStatus = Field(default_factory=CityStatus, description="Саратов")
    spb: CityStatus = Field(default_factory=CityStatus, description="СПБ")
    syzran: CityStatus = Field(default_factory=CityStatus, description="Сызрань")
    taishet: CityStatus = Field(default_factory=CityStatus, description="Тайшет")
    testcity: CityStatus = Field(default_factory=CityStatus, description="Тест")
    tmn: CityStatus = Field(default_factory=CityStatus, description="Тюмень")
    tomsk: CityStatus = Field(default_factory=CityStatus, description="Томск")
    tula: CityStatus = Field(default_factory=CityStatus, description="Тула")
    tver: CityStatus = Field(default_factory=CityStatus, description="Тверь")
    ufa: CityStatus = Field(default_factory=CityStatus, description="Уфа")
    ulsk: CityStatus = Field(default_factory=CityStatus, description="Ульяновск")
    ulu: CityStatus = Field(default_factory=CityStatus, description="Улан-Удэ")
    usol: CityStatus = Field(default_factory=CityStatus, description="Усолье-Сибирское")
    vlz: CityStatus = Field(default_factory=CityStatus, description="Волжский")
    volgograd: CityStatus = Field(default_factory=CityStatus, description="Волгоград")
    voronezh: CityStatus = Field(default_factory=CityStatus, description="Воронеж")
    yar: CityStatus = Field(default_factory=CityStatus, description="Ярославль")
    yola: CityStatus = Field(default_factory=CityStatus, description="Йошкар-Ола")

    model_config = {"populate_by_name": True}


class RawData(BaseModel):
    """Данные события rawData от WebSocket.

    Содержит полную информацию о очередях, агентах, городах и статусах.
    Обновляется каждую секунду.
    """

    availQueues: list[list[QueueInfo]] = Field(
        default_factory=list,
        description="Доступные очереди (вложенный список по уровням)",
    )
    agents: Agents = Field(default_factory=Agents, description="Агенты по статусам")
    exampleGatherMessage: str = Field(default="", description="Пример сообщения")
    lineDuty: list[LineDuty] = Field(
        default_factory=list, description="Дежурные по линии"
    )
    lastMessage: LastMessage = Field(
        default_factory=LastMessage, description="Последнее сообщение"
    )
    serviceScheme: int = Field(default=0, description="Схема сервиса")
    citiesInQueue: CityInQueue = Field(
        default_factory=CityInQueue, description="Города в очереди"
    )
    citiesInProcess: CitiesInProcess = Field(
        default_factory=CitiesInProcess, description="Города в обработке"
    )
    discreteMaxTime: int = Field(
        default=0, description="Максимальное время дискретного режима"
    )
    waitingChats: WaitingChats = Field(
        default_factory=WaitingChats, description="Ожидающие чаты по уровням"
    )
    chatCapacity: ChatCapacity = Field(
        default_factory=ChatCapacity, description="Вместимость чатов"
    )
    daySl: float = Field(default=0.0, description="SL за день")
    citiesStatuses: CitiesStatuses = Field(
        default_factory=CitiesStatuses, description="Статусы городов"
    )

    model_config = {"populate_by_name": True}


class Incident(BaseModel):
    """Базовая модель инцидента (для priority incidents)."""

    incId: int = Field(default=0, description="ID инцидента")
    description: str | None = Field(default=None, description="Описание инцидента")
    priority: int | None = Field(default=None, description="Приоритет")
    status: str | None = Field(default=None, description="Статус")
    created_at: str | None = Field(default=None, description="Время создания")
    updated_at: str | None = Field(default=None, description="Время обновления")

    @property
    def id(self) -> int:
        """ID инцидента (alias for incId)."""
        return self.incId

    model_config = {"populate_by_name": True}


class IncidentStat(BaseModel):
    """Статистика инцидентов (для new/old)."""

    minutesSinceChange: int = Field(default=0, description="Минут с момента изменения")
    mobile: int = Field(default=0, description="Мобильные")
    office: int = Field(default=0, description="Офис")
    other: int = Field(default=0, description="Другие")

    model_config = {"populate_by_name": True}


class RawIncidents(BaseModel):
    """Данные события rawIncidents от WebSocket.

    Содержит инциденты разделенные на priority, new и old.
    Priority - полные данные инцидентов, new/old - статистика.
    """

    priority: list[Incident] = Field(
        default_factory=list, description="Приоритетные инциденты"
    )
    new: list[IncidentStat] = Field(
        default_factory=list, description="Новые (статистика)"
    )
    old: list[IncidentStat] = Field(
        default_factory=list, description="Старые (статистика)"
    )

    model_config = {"populate_by_name": True}


class CiscoAgent(BaseModel):
    """Агент Cisco (ntp1/ntp2 lines)."""

    userId: int = Field(default=0, description="ID пользователя")
    headId: int = Field(default=0, description="ID руководителя")
    userName: str = Field(default="", description="Имя пользователя")
    finesseId: str = Field(default="", description="Finesse ID")
    shiftPresence: int = Field(
        default=0, description="Присутствие на смене (0/1)"
    )
    state: str = Field(default="", description="Состояние")
    stateGroup: str = Field(
        default="",
        description="Группа состояния (ring/ready/talk/unknown)",
    )
    time: int = Field(default=0, description="Время в состоянии")
    statusTime: int = Field(default=0, description="Время статуса")
    shiftId: int = Field(default=0, description="ID смены")
    shiftType: int = Field(default=0, description="Тип смены")
    traineeTypeId: int | None = Field(default=None, description="Тип стажера")

    model_config = {"populate_by_name": True}


class CiscoAgents(BaseModel):
    """Агенты Cisco по группам."""

    ring: list[CiscoAgent] = Field(
        default_factory=list, description="Агенты в состоянии звонка"
    )
    ready: list[CiscoAgent] = Field(
        default_factory=list, description="Готовые агенты"
    )
    talk: list[CiscoAgent] = Field(
        default_factory=list, description="Агенты на разговоре"
    )
    unknown: list[CiscoAgent] = Field(
        default_factory=list, description="Агенты в неизвестном состоянии"
    )

    model_config = {"populate_by_name": True}


class CiscoQueueInfo(BaseModel):
    """Информация об очереди Cisco."""

    name: str = Field(default="", description="Название очереди")
    total: int = Field(default=0, description="Количество")

    model_config = {"populate_by_name": True}


class CiscoAssignment(BaseModel):
    """Назначение агента."""

    userId: int = Field(default=0, description="ID пользователя")
    headId: int = Field(default=0, description="ID руководителя")
    userName: str = Field(default="", description="Имя")
    shiftPresence: int = Field(default=0, description="Присутствие")
    assignmentId: int = Field(default=0, description="ID назначения")
    state: str = Field(default="", description="Состояние")
    comment: str | None = Field(default="", description="Комментарий")
    startTime: str = Field(default="", description="Начало")
    stopTime: str = Field(default="", description="Конец")
    sortOrder: int = Field(default=0, description="Порядок")
    shiftId: int = Field(default=0, description="ID смены")
    source: str = Field(default="", description="Источник")

    model_config = {"populate_by_name": True}


class BossInfo(BaseModel):
    """Информация о боссе."""

    EMPLOYEE_ID: int = Field(default=0, description="Табельный номер")
    FIO: str = Field(default="", description="ФИО")
    EMAIL: str = Field(default="", description="Email")


class CiscoRawData(BaseModel):
    """Данные события rawData от WebSocket для ntp1/ntp2 линий.

    Использует Cisco Finesse формат с другой структурой данных.
    """

    cisco: CiscoAgents = Field(
        default_factory=CiscoAgents, description="Агенты Cisco"
    )
    talkingQueue: list[CiscoQueueInfo] = Field(
        default_factory=list, description="Очереди разговоров"
    )
    waitingQueue: list[CiscoQueueInfo] = Field(
        default_factory=list, description="Очереди ожидания"
    )
    assignments: list[CiscoAssignment] = Field(
        default_factory=list, description="Назначения"
    )
    exampleGatherMessage: str = Field(default="", description="Пример сообщения")
    lastMessage: LastMessage = Field(
        default_factory=LastMessage, description="Последнее сообщение"
    )
    boss: BossInfo = Field(default_factory=BossInfo, description="Босс")
    assistant: list = Field(default_factory=list, description="Ассистенты")
    lineDuty: list[LineDuty] = Field(
        default_factory=list, description="Дежурные"
    )
    serviceScheme: int = Field(default=0, description="Схема сервиса")

    model_config = {"populate_by_name": True}


class AuthRoles(BaseModel):
    """Данные события authRoles от WebSocket.

    Содержит информацию о ролях пользователя.
    """

    roles: list[str] = Field(default_factory=list, description="Список ролей")
    permissions: list[str] = Field(
        default_factory=list, description="Список разрешений"
    )
    user_id: int | None = Field(default=None, description="ID пользователя")
    user_name: str | None = Field(default=None, description="Имя пользователя")

    model_config = {"populate_by_name": True}
