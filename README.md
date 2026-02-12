# Online Dúkan API

RESTful API ushın on-line dúkan platforması. Django hám Django REST Framework (DRF) járdeminde islep shıǵılǵan.

## Proekt imkaniyatları

- **Autentifikaciya:** JWT (Access/Refresh tokens) arqalı dizimnen ótiwi hám kirisiw.
- **Ónimler:** Kategoriyalar boyınsha gruppalanıw, izlew, filterlew (bahası boyınsha: `min_price`, `max_price`) hám sortirovka.
- **Sebet:** Ónimlerdi sebetke qosıw, sanın ózgertiw hám óshiriw. Skladtaǵı qaldıqtı (cumulatively) tekseriw.
- **Buyırtpalar:** Sebetdegi zatlardan buyırtpa jaratıw, skladtı (stock) avtomatikalıq kemeytiw.
- **Pikirler:** Ónimlerge reyting hám kommentariy qaldırıw.
- **Signals:** Jańa paydalanıwshı dizimnen ótkende "Xosh keldińiz" degen email jiberiw.
- **Admin Panel:** Ónimler hám buyırtpalardı basqarıw ushın qolaylı panel.
- **API Documentation:** Swagger arqalı barlıq endpoitlerdi kóriw hám testlew.
- **Qáwipsizlik (Security):** 
    - Rate Limiting (Throttling) — spam hám DDOS-tan qorǵaw.
    - Race Condition Protection — bir waqıtta kóp buyırtpa berilgende skladtı qáte esaplawdan saqlaw.
    - Environment Variables — barlıq jasırın maǵlıwmatlar `.env` faylında.

## Ornatıw hám Iske túsiriw (Docker arqalı — Eń ańsat jolı)

### 1. Reppozitoriyanı kóshirip alıw:
```bash
git clone https://github.com/Sanjar-swe/Edukan.git
cd OnlineDukan
```

### 2. Sazlaw (Environment Variables):
`.env.example` faylınan `.env` faylın jaratıń hám ózińizdiń maǵlıwmatlarıńızdı kiritiń (Telegram Bot token hám t.b.):
```bash
cp .env.example .env
```

### 3. Proektti jıynaw hám iske túsiriw:
Docker ornatılǵan bolsa, tómendegi buyrıqlardı izbe-iz orınlań:
```bash
# 1. Konteynerlerdi jıynaw (Build)
docker-compose build

# 2. Iske túsiriw (Up)
docker-compose up
```
*Bul buyrıq avtomatikalıq túsirip aladı: PostgreSQL bazasın, Django serverin hám Telegram-bottı.*

### 4. Sırırtqı testlew (Ngrok):
Eger proektti internetke shıǵarıp testlemekshi bolsańız:
1. `ngrok http 8000` buyrıǵın jıberip URL-dı alıń.
2. Sol URL-dı `.env`-dag'i `CSRF_TRUSTED_ORIGINS`-ge kiritiń.
3. [NGROK_GUIDE.md](file:///home/swe/Desktop/OnlineDukan/Documentation/NGROK_GUIDE.md) boyınsha tolıq instrukciyanı kóriń.

---

## Ornatıw (Lokal — Docker-siz)

Eger Docker-den paydalanbaqshı bolmasańız:

### 1. Virtual ortalıqtı jaratıw hám iske túsiriw:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Kitapxanalardı ornatıw hám migraciyalar:
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 3. Telegram Bot-tı iske túsiriw (Májburiy):
```bash
python users/telegram_bot.py
```

### 4. Serverdi iske túsiriw:
```bash
python manage.py runserver
```

## API Endpointler Dizimi

### 1. Autentifikaciya (`/api/users/`)
Barlıq login hám dizimnen ótiwi boyınsha endpointler `users/views.py` faylında jaylasqan.

- **Login:** `POST /api/users/login/` (0. Steps)
- **Token Refresh:** `POST /api/users/token/refresh/`
- **Registraciya:** `POST /api/users/register/`
- **Telegram Login:** `POST /api/users/telegram-login/`
- **Profil:** `GET/PUT/PATCH /api/users/profile/`

### 2. Dúkan xızmetleri (`/api/shop/`)
Dúkanǵa baylanıslı endpointler `shop/views/` paketinde gruppalanǵan:

- **1. Ónimler (Catalog):** `GET /categories/`, `GET /products/`
  - *Module:* `shop/views/catalog.py`
- **2. Sebet (Cart):** `GET /cart/`, `POST /cart/add/`, `DELETE /cart/{product_id}/`
  - *Module:* `shop/views/cart.py`
- **3. Buyırtpalar (Checkout):** `GET /orders/`, `POST /orders/checkout/`
  - *Module:* `shop/views/orders.py`
- **4. Pikirler (Reviews):** `GET /reviews/`, `POST /reviews/`
  - *Module:* `shop/views/reviews.py`

## API Hújjetleri (Documentation)

Barlıq endpointler boyınsha tolıq maǵlıwmat hám testlew ushın:
- **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **Testing Guide:** [swagger_testing_guide.md](file:///home/swe/Desktop/OnlineDukan/Documentation/swagger_testing_guide.md) (Step-by-step manual)

## Texnologiyalar
- Python 3.10+
- Django 4.x
- Django REST Framework
- PostgreSQL
- Simple JWT
- drf-spectacular (Swagger)
