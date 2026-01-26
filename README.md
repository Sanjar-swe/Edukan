# Online Dúkan API

RESTful API ushın on-line dúkan platforması. Django hám Django REST Framework (DRF) járdeminde islep shıǵılǵan.

## Proekt imkaniyatları

- **Autentifikaciya:** JWT (Access/Refresh tokens) arqalı dizimnen ótiwi hám kirisiw.
- **Ónimler:** Kategoriyalar boyınsha gruppalanıw, izlew, filterlew hám sortirovka.
- **Sebet:** Ónimlerdi sebetke qosıw, sanın ózgertiw hám óshiriw.
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
Barlıq login hám dizimnen ótiwi boyınsha endpointler `users/views.py` hám `users/urls.py` fayllarında jaylasqan.

- **Login:** `POST /login/`
  - *Class:* `TokenObtainPairView` (SimpleJWT)
  - *Filename:* `users/urls.py`
- **Token Refresh:** `POST /token/refresh/`
  - *Class:* `TokenRefreshView` (SimpleJWT)
  - *Filename:* `users/urls.py`
- **Registraciya:** `POST /register/`
  - *Note:* `telegram_code` (6 sanlı) kiritiliwi shárt.
- **Telegram Login:** `POST /telegram-login/`
  - *Note:* Tek bot-tan alınǵan kod arqalı tez kirisiw.
- **Profil:** `GET/PUT/PATCH /profile/`
  - *Class:* `ProfileView` (generics.RetrieveUpdateAPIView)
  - *Filename:* `users/views.py`

### 2. Dúkan xızmetleri (`/api/shop/`)
Dúkanǵa baylanıslı barlıq endpointler `shop/views.py` degi ViewSet-ler járdeminde iske túsirilgen, marshrutlar `shop/urls.py`da belgilengen.

- **Kategoriyalar:** `GET /categories/`
  - *Class:* `CategoryViewSet` (viewsets.ReadOnlyModelViewSet)
  - *Filename:* `shop/views.py`
- **Ónimler:** `GET /products/`
  - *Class:* `ProductViewSet` (viewsets.ModelViewSet)
  - *Filename:* `shop/views.py`
- **Sebet (Cart):** `GET /cart/`, `POST /cart/add/`, `DELETE /cart/{product_id}/`
  - *Class:* `CartViewSet` (viewsets.ViewSet)
  - *Filename:* `shop/views.py`
- **Buyırtpalar (Orders):** `GET /orders/`, `POST /orders/checkout/`
  - *Class:* `OrderViewSet` (viewsets.ModelViewSet)
  - *Filename:* `shop/views.py`
  - *Note:* `checkout` requires `cart_item_ids` (list) and `address` (string).
- **Pikirler (Reviews):** `GET /reviews/`, `POST /reviews/`
  - *Class:* `ReviewViewSet` (viewsets.ModelViewSet)
  - *Filename:* `shop/views.py`

## API Hújjetleri (Documentation)

Barlıq endpointler boyınsha tolıq maǵlıwmat hám testlew ushın:
- **Swagger UI:** `http://127.0.0.1:8000/swagger/`

## Texnologiyalar
- Python 3.10+
- Django 4.x
- Django REST Framework
- PostgreSQL
- Simple JWT
- drf-yasg (Swagger)
