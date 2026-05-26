# Production Deploy на AWS

## Що створює Terraform

Terraform у `deployment/infra/prod/` створює:
- EC2 instance з Ubuntu
- Elastic IP
- Security Group з доступом лише на 80, 443 і 22
- S3 bucket для avatar-фото
- IAM role та instance profile для доступу EC2 до S3
- Route53 A-record, якщо `enable_route53=true`

## Підготовка домену

Якщо домен керується через Route53:
- вкажіть `enable_route53=true`
- заповніть `root_domain` і `app_domain`
- Terraform сам створить A-record на Elastic IP

Якщо домен лишається в GoDaddy або іншому реєстраторі:
- вкажіть `enable_route53=false`
- після `terraform apply` візьміть `ec2_public_ip`
- створіть A-record вручну на цей Elastic IP

## Як запустити

1. Скопіюйте `deployment/infra/prod/terraform.tfvars.example` у `deployment/infra/prod/terraform.tfvars`
2. Заповніть змінні
3. Переконайтесь, що налаштовані AWS credentials
4. Запустіть:

```bash
python deployment/scripts/deploy_prod.py
```

## Як перевірити

- відкрийте `https://<domain>`
- відкрийте `https://<domain>/api/docs`
- підключіться по SSH і перевірте:

```bash
docker ps
docker logs $(docker ps --format '{{.Names}}' | grep traefik)
```

- перевірте avatar URL з `deployment/generated/avatar_urls.json`

## SSH

```bash
ssh -i /path/to/key.pem ubuntu@<ec2_public_ip>
```

## Як оновити deploy

1. Підключіться по SSH
2. Перейдіть у `/opt/consulting`
3. Виконайте:

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Важливі застереження

- не комітьте реальні secrets у `terraform.tfvars`
- не відкривайте Postgres або Redis назовні
- не запускайте `terraform destroy`, не перевіривши, що саме буде видалено
- Elastic IP може коштувати гроші, якщо не використовується
- Let’s Encrypt потребує правильного DNS і відкритих 80/443
- seed використовує `AVATARS_BASE_URL` для S3 URL у `users.photo`, якщо `USE_S3_AVATARS=true`
