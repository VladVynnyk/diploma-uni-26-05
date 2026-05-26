from __future__ import annotations

import logging
import os
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import joinedload, sessionmaker

from database.models import Order, Review, Tag, User
from settings import get_settings
from utils import get_hashed_password


logger = logging.getLogger(__name__)

DEFAULT_PHOTO = "https://via.placeholder.com/150"
DEFAULT_PASSWORD = "password123"
BACKEND_ROOT = Path(__file__).resolve().parents[1]
AVATAR_URLS_PATH = BACKEND_ROOT / "deployment" / "generated" / "avatar_urls.json"
AVATAR_MANIFEST_PATH = BACKEND_ROOT / "deployment" / "avatar_manifest.json"

TAG_DEFINITIONS = [
    {"name": "Бізнес", "description": "Консультації щодо запуску, розвитку та масштабування бізнесу."},
    {"name": "Право", "description": "Юридичні консультації, перевірка договорів та захист інтересів."},
    {"name": "Фінанси", "description": "Планування бюджету, фінансова стратегія та інвестиційні рішення."},
    {"name": "Психологія", "description": "Підтримка у складних життєвих ситуаціях та роботі зі стресом."},
    {"name": "Кар'єра", "description": "Кар'єрне консультування, резюме, співбесіди та розвиток навичок."},
    {"name": "IT", "description": "Технічні консультації, вибір стеку та розвиток цифрових продуктів."},
    {"name": "Маркетинг", "description": "Позиціонування, реклама, контент та маркетингові кампанії."},
    {"name": "Продажі", "description": "Побудова відділу продажів, скрипти та підвищення конверсії."},
    {"name": "Податки", "description": "Податкове планування, облік та перевірка податкових ризиків."},
    {"name": "Здоров'я", "description": "Консультації щодо балансу навантаження, профілактики вигорання та добробуту."},
]

CONSULTANT_DEFINITIONS = [
    {
        "email": "consultant.business@example.com",
        "first_name": "Олена",
        "last_name": "Коваль",
        "phone_number": "+380501000001",
        "description": "Допомагаю власникам малого бізнесу запускати послуги, рахувати unit-економіку та будувати процеси продажів.",
        "price": 2200,
        "tags": ["Бізнес", "Продажі"],
    },
    {
        "email": "consultant.law@example.com",
        "first_name": "Ігор",
        "last_name": "Мельник",
        "phone_number": "+380501000002",
        "description": "Працюю з договорами, ФОП-питаннями та юридичним супроводом сервісного бізнесу.",
        "price": 2400,
        "tags": ["Право", "Податки"],
    },
    {
        "email": "consultant.finance@example.com",
        "first_name": "Марина",
        "last_name": "Гнатюк",
        "phone_number": "+380501000003",
        "description": "Фінансове планування для підприємців, cash-flow, управлінський облік та сценарне моделювання.",
        "price": 2300,
        "tags": ["Фінанси", "Бізнес"],
    },
    {
        "email": "consultant.psychology@example.com",
        "first_name": "Світлана",
        "last_name": "Романюк",
        "phone_number": "+380501000004",
        "description": "Психологічна підтримка, робота зі стресом, вигоранням та особистими межами.",
        "price": 1800,
        "tags": ["Психологія", "Здоров'я"],
    },
    {
        "email": "consultant.career@example.com",
        "first_name": "Андрій",
        "last_name": "Шевчук",
        "phone_number": "+380501000005",
        "description": "Кар'єрні консультації для фахівців і менеджерів: розвиток, переговори про зарплату, зміна професії.",
        "price": 1700,
        "tags": ["Кар'єра", "Психологія"],
    },
    {
        "email": "consultant.it@example.com",
        "first_name": "Віктор",
        "last_name": "Дмитренко",
        "phone_number": "+380501000006",
        "description": "Консультую щодо архітектури веб-продуктів, вибору технологій, DevOps та технічних ризиків.",
        "price": 2600,
        "tags": ["IT", "Бізнес"],
    },
    {
        "email": "consultant.marketing@example.com",
        "first_name": "Наталія",
        "last_name": "Ткаченко",
        "phone_number": "+380501000007",
        "description": "Стратегії просування, воронки, performance-маркетинг та бренд-комунікації для сервісного бізнесу.",
        "price": 2100,
        "tags": ["Маркетинг", "Продажі"],
    },
    {
        "email": "consultant.sales@example.com",
        "first_name": "Руслан",
        "last_name": "Бондар",
        "phone_number": "+380501000008",
        "description": "Будую системні продажі, CRM-процеси та контроль якості роботи менеджерів.",
        "price": 2000,
        "tags": ["Продажі", "Бізнес"],
    },
    {
        "email": "consultant.taxes@example.com",
        "first_name": "Людмила",
        "last_name": "Савчук",
        "phone_number": "+380501000009",
        "description": "Консультую з податкового навантаження, первинки та підготовки до перевірок.",
        "price": 2250,
        "tags": ["Податки", "Фінанси"],
    },
    {
        "email": "consultant.health@example.com",
        "first_name": "Тетяна",
        "last_name": "Лисенко",
        "phone_number": "+380501000010",
        "description": "Працюю з профілактикою вигорання, балансом навантаження та відновленням ресурсу.",
        "price": 1600,
        "tags": ["Здоров'я", "Психологія"],
    },
    {
        "email": "consultant.startup@example.com",
        "first_name": "Максим",
        "last_name": "Яценко",
        "phone_number": "+380501000011",
        "description": "Допомагаю стартапам перевіряти ідеї, будувати MVP та готуватися до перших продажів.",
        "price": 2500,
        "tags": ["Бізнес", "IT"],
    },
    {
        "email": "consultant.hr@example.com",
        "first_name": "Юлія",
        "last_name": "Петренко",
        "phone_number": "+380501000012",
        "description": "HR та кар'єрні консультації: найм, адаптація, розвиток лідерів та утримання команди.",
        "price": 1750,
        "tags": ["Кар'єра", "Бізнес"],
    },
    {
        "email": "consultant.brand@example.com",
        "first_name": "Дарина",
        "last_name": "Федоренко",
        "phone_number": "+380501000013",
        "description": "Позиціонування, tone of voice, упаковка послуг та контентна стратегія для експертів.",
        "price": 1950,
        "tags": ["Маркетинг", "Бізнес"],
    },
    {
        "email": "consultant.contracts@example.com",
        "first_name": "Павло",
        "last_name": "Кравець",
        "phone_number": "+380501000014",
        "description": "Перевіряю договори, NDA, оферти та допомагаю знизити юридичні ризики співпраці.",
        "price": 2350,
        "tags": ["Право", "Бізнес"],
    },
    {
        "email": "consultant.analytics@example.com",
        "first_name": "Сергій",
        "last_name": "Назаренко",
        "phone_number": "+380501000015",
        "description": "Налаштовую аналітику, dashboards, метрики маркетингу та управлінські звіти.",
        "price": 2050,
        "tags": ["Фінанси", "Маркетинг"],
    },
    {
        "email": "consultant.product@example.com",
        "first_name": "Катерина",
        "last_name": "Мазур",
        "phone_number": "+380501000016",
        "description": "Product-консультації: customer discovery, roadmap, пріоритизація та дизайн сервісів.",
        "price": 2550,
        "tags": ["IT", "Маркетинг"],
    },
    {
        "email": "consultant.recruiting@example.com",
        "first_name": "Оксана",
        "last_name": "Василенко",
        "phone_number": "+380501000017",
        "description": "Підбираю стратегію пошуку роботи та кандидатів, розбір резюме та підготовка до співбесід.",
        "price": 1650,
        "tags": ["Кар'єра", "Продажі"],
    },
    {
        "email": "consultant.export@example.com",
        "first_name": "Денис",
        "last_name": "Панасюк",
        "phone_number": "+380501000018",
        "description": "Консультації з виходу на нові ринки, B2B-продажів та упаковки послуг для експорту.",
        "price": 2450,
        "tags": ["Бізнес", "Маркетинг"],
    },
    {
        "email": "consultant.taxlaw@example.com",
        "first_name": "Галина",
        "last_name": "Сорока",
        "phone_number": "+380501000019",
        "description": "Податково-правові консультації для ФОП, агентств та сервісних команд.",
        "price": 2300,
        "tags": ["Податки", "Право"],
    },
    {
        "email": "consultant.wellbeing@example.com",
        "first_name": "Ірина",
        "last_name": "Чумак",
        "phone_number": "+380501000020",
        "description": "Працюю з особистою ефективністю, режимом, емоційною стійкістю та поверненням до роботи після виснаження.",
        "price": 1550,
        "tags": ["Здоров'я", "Кар'єра"],
    },
]

CLIENT_DEFINITIONS = [
    {"email": "client1@example.com", "first_name": "Владислав", "last_name": "Винник", "phone_number": "+380671000001"},
    {"email": "client2@example.com", "first_name": "Анна", "last_name": "Сидоренко", "phone_number": "+380671000002"},
    {"email": "client3@example.com", "first_name": "Микола", "last_name": "Клименко", "phone_number": "+380671000003"},
    {"email": "client4@example.com", "first_name": "Ірина", "last_name": "Дяченко", "phone_number": "+380671000004"},
    {"email": "client5@example.com", "first_name": "Олег", "last_name": "Марченко", "phone_number": "+380671000005"},
    {"email": "client6@example.com", "first_name": "Софія", "last_name": "Литвин", "phone_number": "+380671000006"},
    {"email": "client7@example.com", "first_name": "Богдан", "last_name": "Кулик", "phone_number": "+380671000007"},
    {"email": "client8@example.com", "first_name": "Марія", "last_name": "Тимошенко", "phone_number": "+380671000008"},
    {"email": "client9@example.com", "first_name": "Роман", "last_name": "Білик", "phone_number": "+380671000009"},
    {"email": "client10@example.com", "first_name": "Вікторія", "last_name": "Міщенко", "phone_number": "+380671000010"},
    {"email": "client11@example.com", "first_name": "Артем", "last_name": "Олійник", "phone_number": "+380671000011"},
    {"email": "client12@example.com", "first_name": "Юлія", "last_name": "Кравчук", "phone_number": "+380671000012"},
    {"email": "client13@example.com", "first_name": "Ілля", "last_name": "Бойко", "phone_number": "+380671000013"},
    {"email": "client14@example.com", "first_name": "Христина", "last_name": "Мельничук", "phone_number": "+380671000014"},
    {"email": "client15@example.com", "first_name": "Дмитро", "last_name": "Козак", "phone_number": "+380671000015"},
    {"email": "client16@example.com", "first_name": "Алла", "last_name": "Баранова", "phone_number": "+380671000016"},
    {"email": "client17@example.com", "first_name": "Єгор", "last_name": "Руденко", "phone_number": "+380671000017"},
    {"email": "client18@example.com", "first_name": "Леся", "last_name": "Степаненко", "phone_number": "+380671000018"},
    {"email": "client19@example.com", "first_name": "Петро", "last_name": "Захарчук", "phone_number": "+380671000019"},
    {"email": "client20@example.com", "first_name": "Назар", "last_name": "Іванчук", "phone_number": "+380671000020"},
    {"email": "client21@example.com", "first_name": "Олена", "last_name": "Поліщук", "phone_number": "+380671000021"},
    {"email": "client22@example.com", "first_name": "Максим", "last_name": "Черненко", "phone_number": "+380671000022"},
    {"email": "client23@example.com", "first_name": "Тетяна", "last_name": "Герасименко", "phone_number": "+380671000023"},
    {"email": "client24@example.com", "first_name": "Сергій", "last_name": "Паламарчук", "phone_number": "+380671000024"},
    {"email": "client25@example.com", "first_name": "Лілія", "last_name": "Приходько", "phone_number": "+380671000025"},
]

ORDER_DEFINITIONS = [
    {"client_email": "client1@example.com", "consultant_email": "consultant.business@example.com", "price": 2200, "topic": "Консультація щодо запуску бізнесу", "message": "Потрібен план старту сервісної компанії та перші кроки по продажах.", "scheduled_at": "2026-05-28T10:00:00", "duration_minutes": 60, "status": "new"},
    {"client_email": "client2@example.com", "consultant_email": "consultant.law@example.com", "price": 2400, "topic": "Юридична перевірка договору", "message": "Хочу перевірити договір з підрядником та ризики по оплаті.", "scheduled_at": "2026-05-29T12:00:00", "duration_minutes": 60, "status": "confirmed"},
    {"client_email": "client3@example.com", "consultant_email": "consultant.finance@example.com", "price": 2300, "topic": "Фінансове планування на 6 місяців", "message": "Потрібна допомога з бюджетом, cash-flow та резервним фондом.", "scheduled_at": "2026-05-30T15:30:00", "duration_minutes": 90, "status": "in_progress"},
    {"client_email": "client4@example.com", "consultant_email": "consultant.career@example.com", "price": 1700, "topic": "Кар'єрна консультація", "message": "Планую зміну роботи і хочу підготуватися до співбесіди.", "scheduled_at": "2026-05-20T11:00:00", "duration_minutes": 60, "status": "completed"},
    {"client_email": "client5@example.com", "consultant_email": "consultant.marketing@example.com", "price": 2100, "topic": "Маркетингова стратегія для експерта", "message": "Потрібно визначити позиціонування та контент-план на запуск послуги.", "scheduled_at": "2026-05-21T16:00:00", "duration_minutes": 60, "status": "completed"},
    {"client_email": "client6@example.com", "consultant_email": "consultant.it@example.com", "price": 2600, "topic": "Технічний аудит MVP", "message": "Потрібно оцінити архітектуру, ризики та пріоритети до релізу.", "scheduled_at": "2026-05-31T13:00:00", "duration_minutes": 90, "status": "confirmed"},
    {"client_email": "client7@example.com", "consultant_email": "consultant.psychology@example.com", "price": 1800, "topic": "Робота зі стресом та вигоранням", "message": "Є перевантаження на роботі, хочу розібратись із симптомами і режимом.", "scheduled_at": "2026-06-01T09:30:00", "duration_minutes": 60, "status": "new"},
    {"client_email": "client8@example.com", "consultant_email": "consultant.sales@example.com", "price": 2000, "topic": "Оптимізація продажів", "message": "Потрібно розібрати воронку та зрозуміти, де втрачаються ліди.", "scheduled_at": "2026-05-24T14:00:00", "duration_minutes": 60, "status": "cancelled"},
    {"client_email": "client9@example.com", "consultant_email": "consultant.taxes@example.com", "price": 2250, "topic": "Підготовка до податкової перевірки", "message": "Потрібно перевірити документи та основні ризики.", "scheduled_at": "2026-05-19T10:30:00", "duration_minutes": 75, "status": "completed"},
    {"client_email": "client10@example.com", "consultant_email": "consultant.brand@example.com", "price": 1950, "topic": "Упаковка особистого бренду", "message": "Хочу краще сформулювати свою експертність і оновити опис послуг.", "scheduled_at": "2026-06-02T17:00:00", "duration_minutes": 60, "status": "confirmed"},
    {"client_email": "client11@example.com", "consultant_email": "consultant.contracts@example.com", "price": 2350, "topic": "Аналіз оферти для клієнтів", "message": "Потрібно перевірити публічну оферту та умови повернення коштів.", "scheduled_at": "2026-06-03T11:30:00", "duration_minutes": 60, "status": "new"},
    {"client_email": "client12@example.com", "consultant_email": "consultant.product@example.com", "price": 2550, "topic": "Product roadmap для нового сервісу", "message": "Потрібна допомога з пріоритизацією функцій та першим roadmap.", "scheduled_at": "2026-05-18T15:00:00", "duration_minutes": 90, "status": "completed"},
    {"client_email": "client13@example.com", "consultant_email": "consultant.hr@example.com", "price": 1750, "topic": "Побудова HR-процесів", "message": "Потрібно налаштувати адаптацію нових співробітників та зворотний зв'язок.", "scheduled_at": "2026-05-27T10:00:00", "duration_minutes": 60, "status": "in_progress"},
    {"client_email": "client14@example.com", "consultant_email": "consultant.export@example.com", "price": 2450, "topic": "Вихід на новий ринок", "message": "Планую продавати послуги за кордон і хочу оцінити канали продажів.", "scheduled_at": "2026-06-04T12:00:00", "duration_minutes": 90, "status": "confirmed"},
    {"client_email": "client15@example.com", "consultant_email": "consultant.wellbeing@example.com", "price": 1550, "topic": "Баланс роботи та відновлення", "message": "Потрібно відновити режим та знизити втому після інтенсивного періоду.", "scheduled_at": "2026-05-17T09:00:00", "duration_minutes": 60, "status": "completed"},
]

REVIEW_DEFINITIONS = [
    {"client_email": "client4@example.com", "consultant_email": "consultant.career@example.com", "rating": 5, "description": "Дуже практична консультація. Отримала чіткий план підготовки до співбесіди.", "created_at": "2026-05-21T13:00:00"},
    {"client_email": "client5@example.com", "consultant_email": "consultant.marketing@example.com", "rating": 5, "description": "Сподобався системний підхід і конкретні ідеї для запуску маркетингу.", "created_at": "2026-05-22T10:00:00"},
    {"client_email": "client9@example.com", "consultant_email": "consultant.taxes@example.com", "rating": 4, "description": "Корисно розклали всі податкові ризики та список документів.", "created_at": "2026-05-20T16:30:00"},
    {"client_email": "client12@example.com", "consultant_email": "consultant.product@example.com", "rating": 5, "description": "Після консультації roadmap став набагато зрозумілішим.", "created_at": "2026-05-19T17:30:00"},
    {"client_email": "client15@example.com", "consultant_email": "consultant.wellbeing@example.com", "rating": 5, "description": "Отримала реалістичні рекомендації без зайвої теорії.", "created_at": "2026-05-18T12:00:00"},
    {"client_email": "client4@example.com", "consultant_email": "consultant.career@example.com", "rating": 4, "description": "Було багато прикладів і конкретних фраз для розмови з рекрутером.", "created_at": "2026-05-21T15:00:00"},
    {"client_email": "client5@example.com", "consultant_email": "consultant.marketing@example.com", "rating": 5, "description": "Після зустрічі стало зрозуміло, як упакувати послугу і які канали тестувати першими.", "created_at": "2026-05-22T12:00:00"},
    {"client_email": "client12@example.com", "consultant_email": "consultant.product@example.com", "rating": 4, "description": "Корисно розклали пріоритети для MVP і допомогли не розпорошуватись.", "created_at": "2026-05-19T18:30:00"},
]


def _load_avatar_manifest() -> dict[str, str]:
    if not AVATAR_MANIFEST_PATH.exists():
        return {}

    try:
        with AVATAR_MANIFEST_PATH.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to read avatar manifest from %s: %s", AVATAR_MANIFEST_PATH, exc)
        return {}

    if not isinstance(payload, dict):
        return {}

    return {
        str(email): str(filename)
        for email, filename in payload.items()
        if email and filename
    }


def _load_avatar_urls() -> dict[str, str]:
    settings = get_settings()

    if settings.use_s3_avatars and settings.avatars_base_url:
        manifest = _load_avatar_manifest()
        base_url = settings.avatars_base_url.rstrip("/")
        return {
            email: f"{base_url}/avatars/{filename}"
            for email, filename in manifest.items()
        }

    if not AVATAR_URLS_PATH.exists():
        return {}

    try:
        with AVATAR_URLS_PATH.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to read avatar URL mapping from %s: %s", AVATAR_URLS_PATH, exc)
        return {}

    if isinstance(payload, dict):
        consultant_email_urls = payload.get("consultant_email_urls")
        if isinstance(consultant_email_urls, dict):
            return {
                str(email): str(url)
                for email, url in consultant_email_urls.items()
                if url
            }
    return {}


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _normalize_flag(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _upsert_tag(session, payload: dict[str, str]) -> tuple[Tag, bool]:
    tag = session.execute(select(Tag).where(Tag.name == payload["name"])).scalar_one_or_none()
    created = False
    if tag is None:
        tag = Tag(name=payload["name"], description=payload["description"])
        session.add(tag)
        session.flush()
        created = True
    else:
        tag.description = payload["description"]
    return tag, created


def _upsert_user(session, payload: dict[str, object], *, password: str, tags_by_name: dict[str, Tag] | None = None) -> tuple[User, bool]:
    user = (
        session.execute(
            select(User)
            .options(joinedload(User.tags))
            .where(User.email == payload["email"])
        )
        .unique()
        .scalar_one_or_none()
    )
    created = False
    if user is None:
        user = User(email=str(payload["email"]))
        session.add(user)
        created = True

    user.first_name = str(payload["first_name"])
    user.last_name = str(payload["last_name"])
    user.phone_number = str(payload["phone_number"])
    user.password = get_hashed_password(password)
    user.photo = str(payload.get("photo") or DEFAULT_PHOTO)
    user.description = str(payload.get("description") or "")
    user.price = payload.get("price")
    user.is_consultant = bool(payload.get("is_consultant", False))
    user.is_admin = bool(payload.get("is_admin", False))

    if tags_by_name is not None:
        tag_names = payload.get("tags", [])
        user.tags = [tags_by_name[tag_name] for tag_name in tag_names]

    session.flush()
    return user, created


def _upsert_order(session, payload: dict[str, object], users_by_email: dict[str, User]) -> tuple[Order, bool]:
    client = users_by_email[str(payload["client_email"])]
    consultant = users_by_email[str(payload["consultant_email"])]
    order = session.execute(
        select(Order).where(
            Order.client_id == client.id,
            Order.consultant_id == consultant.id,
            Order.topic == payload["topic"],
        )
    ).scalar_one_or_none()
    created = False
    if order is None:
        order = Order(
            client_id=client.id,
            consultant_id=consultant.id,
            topic=str(payload["topic"]),
        )
        session.add(order)
        created = True

    order.price = int(payload["price"])
    order.message = str(payload["message"])
    order.scheduled_at = _parse_datetime(str(payload["scheduled_at"]))
    order.duration_minutes = int(payload["duration_minutes"])
    order.status = str(payload["status"])

    session.flush()
    return order, created


def _upsert_review(session, payload: dict[str, object], users_by_email: dict[str, User]) -> tuple[Review | None, bool]:
    client = users_by_email[str(payload["client_email"])]
    consultant = users_by_email[str(payload["consultant_email"])]
    completed_order = session.execute(
        select(Order).where(
            Order.client_id == client.id,
            Order.consultant_id == consultant.id,
            Order.status == "completed",
        )
    ).scalar_one_or_none()
    if completed_order is None:
        logger.warning(
            "Skipping review seed because no completed order exists for client=%s consultant=%s",
            client.email,
            consultant.email,
        )
        return None, False

    review = session.execute(
        select(Review).where(
            Review.client_id == client.id,
            Review.consultant_id == consultant.id,
            Review.description == payload["description"],
        )
    ).scalar_one_or_none()
    created = False
    if review is None:
        review = Review(
            client_id=client.id,
            consultant_id=consultant.id,
        )
        session.add(review)
        created = True

    review.rating = int(payload["rating"])
    review.description = str(payload["description"])
    review.created_at = _parse_datetime(str(payload["created_at"]))

    session.flush()
    return review, created


def seed_demo_data(force: bool = False) -> dict[str, int]:
    settings = get_settings()
    engine = create_engine(settings.db_uri)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    consultant_avatar_urls = _load_avatar_urls()

    summary = {
        "tags_created": 0,
        "users_created": 0,
        "orders_created": 0,
        "reviews_created": 0,
    }

    with SessionLocal() as session:
        admin_exists = session.execute(
            select(User.id).where(User.email == "admin@example.com")
        ).scalar_one_or_none() is not None
    if admin_exists and not force:
        logger.info("Demo data already exists. Seed will reconcile records without creating duplicates.")

    with SessionLocal() as session:
        with session.begin():
            tags_by_name: dict[str, Tag] = {}
            for tag_definition in TAG_DEFINITIONS:
                tag, created = _upsert_tag(session, tag_definition)
                tags_by_name[tag.name] = tag
                summary["tags_created"] += int(created)

            users_by_email: dict[str, User] = {}

            admin_user, admin_created = _upsert_user(
                session,
                {
                    "email": "admin@example.com",
                    "first_name": "Admin",
                    "last_name": "User",
                    "phone_number": "+380501111111",
                    "photo": DEFAULT_PHOTO,
                    "description": "Системний адміністратор демонстраційного середовища.",
                    "price": None,
                    "is_consultant": False,
                    "is_admin": True,
                },
                password="admin12345",
            )
            users_by_email[admin_user.email] = admin_user
            summary["users_created"] += int(admin_created)

            for consultant_definition in CONSULTANT_DEFINITIONS:
                consultant_payload = {
                    **consultant_definition,
                    "photo": consultant_avatar_urls.get(
                        consultant_definition["email"],
                        DEFAULT_PHOTO,
                    ),
                    "is_consultant": True,
                    "is_admin": False,
                }
                consultant, created = _upsert_user(
                    session,
                    consultant_payload,
                    password=DEFAULT_PASSWORD,
                    tags_by_name=tags_by_name,
                )
                users_by_email[consultant.email] = consultant
                summary["users_created"] += int(created)

            for client_definition in CLIENT_DEFINITIONS:
                client_payload = {
                    **client_definition,
                    "photo": DEFAULT_PHOTO,
                    "description": "",
                    "price": None,
                    "is_consultant": False,
                    "is_admin": False,
                }
                client, created = _upsert_user(
                    session,
                    client_payload,
                    password=DEFAULT_PASSWORD,
                )
                users_by_email[client.email] = client
                summary["users_created"] += int(created)

            for order_definition in ORDER_DEFINITIONS:
                _, created = _upsert_order(session, order_definition, users_by_email)
                summary["orders_created"] += int(created)

            for review_definition in REVIEW_DEFINITIONS:
                _, created = _upsert_review(session, review_definition, users_by_email)
                summary["reviews_created"] += int(created)

    logger.info("Seed complete: %s", summary)
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    force = _normalize_flag(os.getenv("SEED_DEMO_DATA_FORCE"))
    summary = seed_demo_data(force=force)
    print(summary)


if __name__ == "__main__":
    main()
