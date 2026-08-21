# پلن ساخت کتابخانه‌ی پایتون

این پلن اکنون پیاده‌سازی شده است: SDK async و type-safe در `src/funstat` با
`httpx.AsyncClient` و مدل‌های Pydantic v2 قرار دارد. موارد باقی‌مانده در این
سند، توسعه‌های اختیاری هستند.

## تصمیم‌های پیشنهادی

- Python 3.10+، کلاینت async بر پایه‌ی `httpx.AsyncClient`.
- مدل‌ها با `pydantic v2` و نام‌گذاری Pythonic؛ alias برای نام‌های فعلی API مثل
  `pageSize` و `onlyMsg`.
- لایه‌ی انتقال مستقل از مدل‌ها تا امکان تعویض HTTP client و تست با mock فراهم
  باشد.
- base URL اجباری در سازنده؛ چون در Swagger تعریف نشده است.
- توابع آرایه‌ای (`id` و `name`) با serialization قابل تنظیم، پیش‌فرض تکرار
  پارامتر (`id=1&id=2`)؛ این رفتار باید با یک تست contract تأیید شود.

## ساختار بسته

```text
src/funstat/
  __init__.py
  client.py          # FunstatClient، lifecycle و auth
  transport.py       # request، timeout، status mapping، retry
  errors.py          # FunstatError و Unauthorized/Forbidden/ApiProblem
  models/
    common.py        # ApiResponse، TechInfo، Paging
    groups.py
    users.py
    search.py
  resources/
    groups.py        # متدهای Groups
    users.py         # متدهای Users
    text.py
```

`FunstatClient` منابع `groups`, `users` و `text` را expose می‌کند و همه‌ی متدها
type hint و docstring شامل هزینه و محدودیت عملیاتی دارند.

## API عمومی پیشنهادی

- `FunstatClient(base_url, token, timeout=...)`
- context managerهای `async with FunstatClient(...)`
- `client.groups.common_groups(ids)`
- `client.groups.get(id)`, `members(id)`
- `client.users.stats(id, full=True)`, `basic_info_by_id(ids)`,
  `resolve_username(names)`
- `client.users.messages(id, page, page_size, ...)` و متدهای شمارش/گروه/تاریخچه
- `client.users.gifts_relation(id, page, page_size)`
- `client.text.search(input, page, page_size)`

برای endpointهای صفحه‌بندی‌شده یک `Page[T]` عمومی و متد کمکی async iterator
(`iter_messages`, `iter_text_search`, ...) اضافه شود؛ دریافت خودکار همه‌ی صفحات
باید opt-in باشد چون هزینه‌ی سرویس ممکن است زیاد شود.

## مدیریت خطا و هزینه

1. قبل از ارسال، اعتبارسنجی شناسه‌ها و `page/pageSize` مثبت.
2. timeout پیش‌فرض، connection pooling و retry فقط برای خطاهای موقت شبکه/`5xx`
   با backoff؛ retry روی درخواست‌های هزینه‌دار باید قابل خاموش‌کردن باشد.
3. نگاشت `401`، `403` و `500` به exceptionهای مشخص و parse کردن `AppProblem`.
4. پس از هر پاسخ، `TechInfo` در شیء پاسخ باقی بماند؛ یک hook اختیاری برای
   ثبت هزینه و موجودی ارائه شود.
5. عدم log کردن JWT و داده‌های حساس؛ امکان redaction در debug logging.

## مراحل اجرا

1. تثبیت قرارداد: تعیین base URL، serialization آرایه‌ها، نمونه‌ی واقعی پاسخ
   endpointهای فاقد schema و قواعد rate limit با مالک API.
2. تولید مدل‌های Pydantic و envelopeهای مشترک از Swagger؛ تست parse برای فیلدهای
   nullable و تاریخ/بازه‌ی زمانی.
3. پیاده‌سازی transport و exception mapping، سپس یک resource کامل به‌عنوان
   الگو.
4. پیاده‌سازی بقیه‌ی resources و pagination/iterators، با پوشش همه‌ی ۲۰ مسیر.
5. تست unit با `respx` یا mock transport، تست contract در برابر نمونه‌های واقعی،
   و تست عدم افشای token در log.
6. مستندسازی README، نمونه‌ی quickstart و جدول هزینه‌ها؛ انتشار type stubs
   (خود کد typed است) و changelog.
7. CI: lint (`ruff`)، type check (`mypy`/`pyright`)، تست و build wheel؛ انتشار
   با `pyproject.toml` و نسخه‌گذاری معنایی.

## معیار پذیرش

- هر ۲۰ endpoint یک متد typed و تست‌شده دارد.
- پاسخ موفق، `tech` و داده‌ی nullable بدون از دست رفتن اطلاعات parse می‌شود.
- خطاهای 401/403/500 به exception قابل تشخیص تبدیل می‌شوند.
- pagination و هزینه‌ی درخواست در API عمومی واضح است و SDK هیچ retry پنهانی
  برای عملیات پرهزینه انجام نمی‌دهد.
- تست‌ها بدون شبکه قابل اجرا هستند و حداقل یک تست contract اختیاری برای سرور
  واقعی وجود دارد.
