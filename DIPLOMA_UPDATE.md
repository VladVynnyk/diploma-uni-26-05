# Звіт про поточний стан проєкту

## 1. Короткий висновок

Поточний проєкт уже не є просто marketplace консультантів. За фактичним кодом це гібридна web-орієнтована система: публічний каталог консультантів + dashboard для керування консультаційними заявками, ролями, тегами, відгуками та статистикою. Основна бізнес-сутність консультації реалізована через модель `Order` у [consulting-backend/core/database/models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:27), а адміністративне керування винесене у спільний dashboard без окремого `/admin` у [advicerr-frontend/src/app/dashboard/Dashboard.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1).

За темою диплома "Розробка web-орієнтованої системи менеджменту консультаційних послуг на базі платформи AWS" проєкт відповідає приблизно на `82%`. Найсильніша частина: ролі, workflow консультацій, admin/dashboard логіка, теги, відгуки, seed/demo дані та окрема AWS/S3 automation для avatar assets у [deployment/infra/s3_avatars](/D:/site/Consulting/bachelors/deployment/infra/s3_avatars/main.tf:1) і [deployment/scripts](/D:/site/Consulting/bachelors/deployment/scripts/setup_s3_avatars.py:1). Найслабша частина: AWS-частина ще вузька і зосереджена майже тільки на S3; немає реального коду для EC2/ECS/RDS/CloudFront, а також є технічні ризики та застарілі route-и, що не повністю узгоджені з новою консультаційною моделлю.

## 2. Таблиця оцінки по блоках

| Блок | Оцінка | Коментар |
| --- | --- | --- |
| A) Web-орієнтована система | `9/10` | Є Next.js frontend, FastAPI backend, auth, dashboard, user flows, RTK Query API та role-based UI. |
| B) Консультаційні послуги | `9/10` | Є консультанти, клієнти, заявки на консультації, поля `topic/message/scheduled_at/duration_minutes`, відгуки й теги. |
| C) Менеджмент | `8/10` | Є ролі client/consultant/admin, статусний workflow, admin stats, обмеження доступу, але є окремі старі route-и та спрощена доменна модель. |
| D) AWS | `7/10` | Реально є S3, Terraform, boto3 upload, master script, avatar mapping, DB sync script, seed fallback; але RDS/EC2/CloudFront тільки в документації. |

## 3. Детальний аналіз

### 3.1 Поточна природа системи

Система складається з:

- FastAPI application у [consulting-backend/core/main.py](/D:/site/Consulting/bachelors/consulting-backend/core/main.py:1), де підключені `auth`, `users`, `orders`, `reviews`, `tags`, `admin`, `payments`.
- Next.js dashboard і публічного UI у [advicerr-frontend/src/app](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1).
- PostgreSQL/SQLAlchemy моделей у [consulting-backend/core/database/models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:1).
- AWS/S3 automation у [deployment](/D:/site/Consulting/bachelors/deployment/infra/s3_avatars/main.tf:1).

Висновок: по факту це вже більше система менеджменту консультаційних послуг, ніж просто каталог консультантів, але каталогова marketplace-складова ще помітна через публічний список консультантів у [consulting-backend/core/routers/users/read.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/read.py:1).

### 3.2 Перевірка відповідності темі

#### A) Web-орієнтована система

Реалізовано:

- frontend на Next.js з dashboard, login/signup, каталогом, order form та admin sections;
- backend API на FastAPI;
- JWT auth у [consulting-backend/core/routers/users/auth.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/auth.py:1) і [consulting-backend/core/deps.py](/D:/site/Consulting/bachelors/consulting-backend/core/deps.py:1);
- dashboard у [advicerr-frontend/src/app/dashboard/Dashboard.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1);
- RTK Query для orders/users/reviews/tags/admin.

Оцінка: `9/10`.

#### B) Консультаційні послуги

Реалізовано:

- ролі консультантів і клієнтів через `users.is_consultant` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:145);
- консультаційні заявки через `Order` з полями `topic`, `message`, `scheduled_at`, `duration_minutes`, `status` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:27);
- відгуки через `Review` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:52);
- теги напрямів через `Tag` і `tags_users` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:73).

Оцінка: `9/10`.

#### C) Менеджмент

Реалізовано:

- ролі `client / consultant / admin`;
- admin endpoints у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:1);
- власні orders для consultant/client у [orders_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/orders_router.py:134);
- stats endpoint `/dashboard/admin/stats` у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:110);
- access control у [deps.py](/D:/site/Consulting/bachelors/consulting-backend/core/deps.py:1) і в route-ах.

Оцінка: `8/10`, бо є ще застарілі users/order update endpoints, а платіжний workflow не інтегрований у consultation status.

#### D) AWS

Реалізовано:

- Terraform bucket automation у [deployment/infra/s3_avatars/main.tf](/D:/site/Consulting/bachelors/deployment/infra/s3_avatars/main.tf:1);
- boto3 upload script у [deployment/scripts/upload_avatars_to_s3.py](/D:/site/Consulting/bachelors/deployment/scripts/upload_avatars_to_s3.py:1);
- master setup script у [deployment/scripts/setup_s3_avatars.py](/D:/site/Consulting/bachelors/deployment/scripts/setup_s3_avatars.py:1);
- avatar mapping у [deployment/generated/avatar_urls.json](/D:/site/Consulting/bachelors/deployment/generated/avatar_urls.json:1);
- DB sync script у [deployment/scripts/sync_avatar_urls_to_db.py](/D:/site/Consulting/bachelors/deployment/scripts/sync_avatar_urls_to_db.py:1);
- seed fallback та інтеграція з mapping у [consulting-backend/core/seed.py](/D:/site/Consulting/bachelors/consulting-backend/core/seed.py:1).

Не знайдено в коді:

- реального RDS deployment;
- реального EC2/ECS deployment;
- CloudFront integration;
- production IaC для всієї AWS архітектури.

Оцінка: `7/10`.

### 3.3 Поточний workflow системи

#### A) Client

- Реєстрація/логін: `реалізовано` через `/auth/signup`, `/auth/login`, `/auth/refresh-token` у [auth.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/auth.py:35).
- Заповнення профілю: `реалізовано` через `/users/update/{user_id}` у [update.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/update.py:29) і форму у [PersonalInformation.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/PersonalInformation/PersonalInformation.tsx:1).
- Перегляд консультантів: `реалізовано` через `/users/`, `/users/paginated`, `/users/sort_by_tag/{tag}` у [read.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/read.py:1).
- Бронювання/створення order: `реалізовано` через `POST /orders/` у [orders_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/orders_router.py:49).
- Перегляд статусу: `реалізовано` через `/orders/account/{user_id}` у [orders_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/orders_router.py:151).
- Відгук: `частково реалізовано`; створення review є у `POST /reviews/` в [reviews_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/reviews_router.py:19), але немає явної жорсткої перевірки "лише після completed order" на backend route.

#### B) Consultant

- Логін: `реалізовано`.
- Dashboard: `реалізовано` у [Dashboard.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1).
- Перегляд своїх orders: `реалізовано` через `/orders/account/consultant/{consultant_id}` і агрегований `/orders/account/{user_id}`.
- Перегляд контактів client: `реалізовано` через permission-aware serializer у [serializers.py](/D:/site/Consulting/bachelors/consulting-backend/core/serializers.py:55).
- Зміна статусу консультації: `реалізовано` через `PATCH /orders/{order_id}/status` у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:65) і frontend dropdown у [SingleOrder.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Orders/SingleOrder.tsx:1).
- Перегляд reviews: `реалізовано`.

#### C) Admin

- Логін: `реалізовано`.
- Dashboard: `реалізовано`.
- Перегляд users: `реалізовано` через `GET /users/admin/all`.
- Керування admin-role: `реалізовано` через `PATCH /users/{user_id}/admin-status`.
- Перегляд orders: `реалізовано` через `GET /orders/admin/all`.
- Зміна status: `реалізовано`.
- Перегляд/delete reviews: `реалізовано` через `GET /reviews/admin/all` і `DELETE /reviews/{id}`.
- CRUD tags: `реалізовано` через `tags_router`.
- Stats: `реалізовано`.

### 3.4 Аналіз моделей бази даних

#### User

Поля: `id`, `first_name`, `last_name`, `phone_number`, `email`, `password`, `photo`, `description`, `price`, `created_at`, `is_consultant`, `is_admin`, `rating`, `tags`, зв’язки з `Order` і `Review` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:96).

Ключові поля для теми диплома:

- `is_admin`: додано і використовується реально;
- `is_consultant`: використовується реально;
- `phone_number`: використовується реально, і в account update є обов’язковим через [pydantic_models.py](/D:/site/Consulting/bachelors/consulting-backend/core/pydantic_models.py:20).

Оцінка: для теми достатньо.

#### Order

Поля: `price`, `status`, `topic`, `message`, `scheduled_at`, `duration_minutes`, `consultant_id`, `client_id`, `created_at` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:27).

Це фактичний замінник ConsultationRequest. Для диплома цього достатньо, хоча окрема сутність `ConsultationRequest` не знайдена.

#### Review

Поля: `description`, `rating`, `created_at`, `consultant_id`, `client_id` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:52).

Для системи відгуків цього достатньо.

#### Tag

Поля: `id`, `name`, `description`, `created_at`, зв’язок many-to-many з `User` у [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:73).

Для напрямів консультацій достатньо.

#### CardPayment

`CardPayment` є в [models.py](/D:/site/Consulting/bachelors/consulting-backend/core/database/models.py:149), але ця модель виглядає окремою і не пов’язана напряму з consultation workflow/status logic.

Висновок: payment-частина існує, але слабко інтегрована з основною моделлю консультаційного менеджменту.

### 3.5 Аналіз backend API

#### A) Auth/users

Є:

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh-token`
- `GET /users/account/me`
- `PATCH /users/update/{user_id}`
- `GET /users/admin/all`
- `PATCH /users/{user_id}/admin-status`

Захист:

- current user витягується через JWT у [deps.py](/D:/site/Consulting/bachelors/consulting-backend/core/deps.py:1);
- admin endpoints захищені через `require_admin`.

Ризики:

- signup не вимагає `phone_number`, update profile вимагає;
- `change_photo` у [update.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/users/update.py:46) містить hardcoded bucket `avatar-bucket-main`;
- є старі допоміжні routes `change/name`, `change/surname`, `add/tags`, `remove/tags`, які виглядають менш узгодженими з новою логікою.

#### B) Orders

Є:

- `POST /orders/`
- `GET /orders/account/{user_id}`
- `GET /orders/account/client/{client_id}`
- `GET /orders/account/consultant/{consultant_id}`
- `GET /orders/admin/all`
- `PATCH /orders/{order_id}/status`

Strict workflow:

- backend transitions задані у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:20);
- frontend transitions задані у [OrderTypes.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/types/OrderTypes.tsx:46).

Contact visibility:

- client email/phone віддаються тільки consultant/admin у [serializers.py](/D:/site/Consulting/bachelors/consulting-backend/core/serializers.py:55).

Ризики:

- `GET /orders/{id}`, `PATCH /orders/{id}`, `DELETE /orders/{id}` виглядають застарілими і не відповідають поточній моделі `Order` у [orders_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/orders_router.py:110).

#### C) Reviews

Є:

- `POST /reviews/`
- `GET /reviews/`
- `GET /reviews/client/{client_id}`
- `GET /reviews/consultant/{consultant_id}`
- `GET /reviews/admin/all`
- `DELETE /reviews/{id}`

Захист:

- admin list і delete захищені.

Ризики:

- create review route не захищає доменне правило "review тільки після completed consultation".

#### D) Tags

Є:

- `GET /tags/`
- `POST /tags/`
- `PATCH /tags/{id}`
- `DELETE /tags/{id}`

Захист:

- write operations доступні тільки admin у [tags_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/tags_router.py:20).

#### E) Stats

Є:

- `GET /dashboard/admin/stats` у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:110).

Повертає:

- users, consultants, clients, orders by statuses, reviews, average rating, tags.

### 3.6 Аналіз frontend

#### Реалізовано

- Dashboard з role-based sections у [Dashboard.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1).
- Personal account form з phone validation і price validation у [PersonalInformation.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/PersonalInformation/PersonalInformation.tsx:1).
- Orders UI з topic/message/scheduledAt/duration/status у [SingleOrder.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Orders/SingleOrder.tsx:1).
- Status dropdown з allowed transitions у [OrderTypes.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/types/OrderTypes.tsx:46).
- Admin sections у dashboard, а не в окремому `/admin`, у [Dashboard.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/dashboard/Dashboard.tsx:1).

#### Важливі спостереження

- frontend не лише приховує блоки, backend теж реально захищає доступ через JWT/admin checks;
- це сильна сторона архітектури;
- admin UI існує, але виглядає утилітарно, без окремої складної UX-оболонки.

### 3.7 Аналіз статусного workflow

Підтверджено в коді:

- `new -> confirmed/cancelled`
- `confirmed -> in_progress/cancelled`
- `in_progress -> completed/cancelled`
- `completed` фінальний
- `cancelled` фінальний

Backend:

- реалізовано в `STATUS_TRANSITIONS` у [admin_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/admin_router.py:20).

Frontend:

- реалізовано в `ORDER_STATUS_TRANSITIONS` у [OrderTypes.tsx](/D:/site/Consulting/bachelors/advicerr-frontend/src/app/types/OrderTypes.tsx:46).

Ролі:

- admin не може ламати workflow, бо теж проходить через backend transitions;
- consultant може змінювати тільки власні orders;
- client не може змінювати status.

Оцінка: реалізовано добре.

### 3.8 Аналіз AWS/S3 частини

Реально знайдено:

- Terraform для bucket: [deployment/infra/s3_avatars/main.tf](/D:/site/Consulting/bachelors/deployment/infra/s3_avatars/main.tf:1)
- outputs: [outputs.tf](/D:/site/Consulting/bachelors/deployment/infra/s3_avatars/outputs.tf:1)
- CORS: є в `aws_s3_bucket_cors_configuration`
- public read: є через `aws_s3_bucket_policy`
- boto3 upload: [upload_avatars_to_s3.py](/D:/site/Consulting/bachelors/deployment/scripts/upload_avatars_to_s3.py:1)
- master script: [setup_s3_avatars.py](/D:/site/Consulting/bachelors/deployment/scripts/setup_s3_avatars.py:1)
- generated mapping: [deployment/generated/avatar_urls.json](/D:/site/Consulting/bachelors/deployment/generated/avatar_urls.json:1)
- DB update script: [sync_avatar_urls_to_db.py](/D:/site/Consulting/bachelors/deployment/scripts/sync_avatar_urls_to_db.py:1)
- seed fallback на placeholder: [seed.py](/D:/site/Consulting/bachelors/consulting-backend/core/seed.py:19)

Що тільки описано в документації:

- CloudFront
- EC2
- ECS
- RDS
- ElastiCache

Що можна чесно писати в дипломі:

- AWS S3 реально використовується для avatar/photo storage;
- для S3 є Terraform automation, boto3 upload, master setup script, mapping JSON і DB sync script;
- повна production AWS-архітектура поки що описана концептуально, а не реалізована кодом.

## 4. Що добре

- Рольова модель `client / consultant / admin` реально працює.
- Consultation workflow добре накладений на `Order`.
- Є admin dashboard без окремого `/admin`, що спрощує архітектуру.
- Є strict status workflow і на backend, і на frontend.
- Є contact visibility logic для client contacts.
- Є reviews, tags, stats.
- Є seed/demo data.
- Є реальна S3 automation, а не тільки опис у документації.
- Є окремий script для оновлення `users.photo` з `avatar_urls.json`.

## 5. Що слабко

- Окрема сутність `Service` не знайдена.
- `Order` нормально покриває consultation request, але це компромісна модель.
- Не знайдено календаря/slot booking.
- Не знайдено реального чату.
- Payment модель існує окремо і слабко інтегрована з консультаційним workflow.
- Є застарілі route-и в orders/users update частині.
- AWS-частина реальна, але вузька: по факту реалізовано S3, а не повну AWS-платформу.
- Admin dashboard функціональний, але досить простий.
- Є ризики безпеки й технічного боргу:
  - hardcoded S3 bucket в `change_photo`;
  - чутливі налаштування через `.env`;
  - частина коду все ще змішана зі старою marketplace-логікою.
- У Docker flow є ризик, що auto-seed перезаписує `photo`, якщо `avatar_urls.json` недоступний контейнеру.

## 6. Що доробити

### A) Обов’язково перед захистом

1. Узгодити seed + Docker + S3 mapping.
   Навіщо: щоб avatar URLs не зникали після restart.
   Файли: [seed.py](/D:/site/Consulting/bachelors/consulting-backend/core/seed.py:1), [docker-compose.dev.yml](/D:/site/Consulting/bachelors/docker-compose.dev.yml:1), [docker-entrypoint.sh](/D:/site/Consulting/bachelors/consulting-backend/docker-entrypoint.sh:1).
   Складність: `medium`.
   Вплив на диплом: `high`.

2. Прибрати або ізолювати застарілі order routes.
   Навіщо: вони не відповідають поточній моделі і псують технічну цілісність.
   Файли: [orders_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/orders_router.py:110).
   Складність: `medium`.
   Вплив: `high`.

3. Додати backend rule для review тільки після completed consultation.
   Навіщо: посилення доменної логіки.
   Файли: [reviews_router.py](/D:/site/Consulting/bachelors/consulting-backend/core/routers/reviews_router.py:19), [orders_dao.py](/D:/site/Consulting/bachelors/consulting-backend/core/daos/orders_dao.py:1).
   Складність: `medium`.
   Вплив: `high`.

### B) Бажано, якщо є час

1. Зробити чіткіший зв’язок payment -> order status.
   Складність: `medium`.
   Вплив: `medium`.

2. Підчистити старі S3 upload paths у backend profile photo endpoint.
   Складність: `low`.
   Вплив: `medium`.

3. Поліпшити admin dashboard UX.
   Складність: `medium`.
   Вплив: `medium`.

### C) Не варто робити зараз

1. Повний перехід на окрему складну microservice AWS-архітектуру.
   Складність: `high`.
   Вплив на захист: `low/medium`.

2. Додавання чату, календаря слотів, video-call subsystem.
   Складність: `high`.
   Вплив: `medium`, але занадто роздує проєкт.

3. Повна заміна `Order` на нову domain-сутність.
   Складність: `high`.
   Вплив: `medium`.

## 7. Як описати в дипломі

Об’єкт розробки:

- web-орієнтована інформаційна система менеджменту консультаційних послуг.

Предмет розробки:

- механізми керування консультаційними заявками, ролями користувачів, відгуками, тегами та пов’язаними цифровими ресурсами.

Мета системи:

- забезпечити пошук консультантів, створення й супровід консультаційних заявок, рольове керування процесом консультації та централізований адміністративний контроль.

Основні модулі:

- frontend-каталог консультантів;
- auth і account management;
- consultation orders/workflow;
- reviews and tags;
- admin dashboard;
- S3 avatar storage automation.

Ролі користувачів:

- client;
- consultant;
- admin.

Чому це система менеджменту консультаційних послуг, а не просто marketplace:

- є повноцінний workflow заявки;
- є статусна модель;
- є керування ролями;
- є admin statistics і moderation;
- є consultant/client/account-specific views;
- є доступ до контактів клієнта за правилами ролей.

AWS-архітектура:

- реально реалізовано S3 для avatar storage;
- Terraform/boto3/scripts підтримують bucket setup, upload і DB sync;
- інші AWS-компоненти поки описані як цільова архітектура, але не реалізовані у коді.

## 8. Фінальна оцінка у відсотках

- Загальна відповідність темі: `82%`
- Технічна готовність до захисту: `78%`
- AWS-частина: `68%`

### 5 найважливіших доробок

1. Виправити Docker + seed + avatar mapping інтеграцію.
2. Прибрати або відключити застарілі `orders/{id}` update/delete/get paths.
3. Додати review-policy тільки для completed consultations.
4. Прибрати hardcoded S3 bucket логіку зі старого profile photo route.
5. Узгодити payment flow із consultation lifecycle або чітко відокремити це в пояснювальній записці.

### Короткий фінальний висновок

Проєкт уже можна описувати й готувати до захисту як систему менеджменту консультаційних послуг на базі web-архітектури з реальною інтеграцією AWS S3. Але перед захистом бажано ще доробити кілька технічно помітних місць, насамперед seed/S3/Docker інтеграцію і прибрати застарілі endpoint-частини, щоб система виглядала цілісно і без суперечностей.
