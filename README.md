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

## Ornatıw hám Iske túsiriw

### 1. Reppozitoriyanı kóshirip alıw:
```bash
git clone <repository_url>
cd OnlineDukan
```

### 2. Virtual ortalıqtı jaratıw hám iske túsiriw:
```bash
python -m venv venv
source venv/bin/activate  # Windows ushın: venv\Scripts\activate
```

### 3. Kerekli kitapxanalardı ornatıw:
```bash
pip install -r requirements.txt
```

### 4. Sazlaw (Environment Variables):
`.env.example` faylınan `.env` faylın jaratıń hám ózińizdiń maǵlıwmatlarıńızdı kiritiń (DB, Bot token):
```bash
cp .env.example .env
```

### 5. Maǵlıwmatlar bazasın sazlaw hám migraciyalar:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Telegram Bot-tı iske túsiriw (Májburiy):
Registraciya kodın alıw ushın bot islep turıwı kerek:
```bash
python users/telegram_bot.py
```

### 7. Serverdi iske túsiriw:
```bash
python manage.py runserver
```

### 8. Docker arqalı iske túsiriw (Alternativ):
Eger sizde Docker ornatılǵan bolsa, proektti tómendegi buyrıq arqalı iske túsire alasız:
```bash
docker-compose up --build
```
Bul buyrıq avtomatikalıq kerekli ortalıqtı jaratadı hám bazanı sazlaydı. (Eskertpe: `.env` faylı bolıwı shárt).

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
