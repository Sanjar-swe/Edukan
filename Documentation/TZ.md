# Online Dúkan API

## 1. Proekt Maqseti

Paydalanıwshılar ónimlerdi kóriwi, sebetke (karzina) salıwı hám buyırtpa (zakaz) beriwi múmkin bolǵan, al administratorlar ónimlerdi basqara alatuǵın **RESTful API** jaratıw.

## 2. Texnologiyalar Stack-i

- **Til:** Python 3.10+
- **Framework:** Django 4.x, Django REST Framework (DRF)
- **Maǵlıwmatlar bazası:** PostgreSQL
- **Autentifikaciya:** JWT (Simple JWT)
- **Hújjetlestiriw:** Swagger (drf-yasg yamasa drf-spectacular)
- **Media:** Súwretlerdi saqlaw (Media files)

---

## 3. Maǵlıwmatlar Bazası Modelleri (Models)

Tómendegi modeller hám olardıń maydanları (fields) bolıwı kerek:

### A. Paydalanıwshılar (Users)

Django-nıń `AbstractUser` modelinen paydalanıw yamasa onı keńeytiw kerek.

- **Role:** Admin, Klient.
- **Qosımsha maydanlar:** Telefon nomer, Mánzil (Address).

### B. Kategoriyalar (Categories)

Ónimlerdi toparlaw ushın.

- `name`: Kategoriya atı (Máselen: "Smartfonlar", "Kiyimler").
- `slug`: URL ushın unikal atama.
- `parent`: (Optional) Ishki kategoriyalar ushın (Máselen: Elektronika -> Noutbuklar).

### C. Ónimler (Products)

- `category`: Kategoriyaǵa baylanıs (ForeignKey).
- `name`: Ónim atı.
- `slug`: URL ushın.
- `description`: Toliq maǵlıwmat.
- `price`: Bahası (DecimalField).
- `discount_price`: Shegirmeli baha (eger bolsa).
- `image`: Ónim súwreti.
- `stock`: Qoymadaǵı sanı (Integer).
- `is_active`: Ónim satılıwda bar/joqlıǵı.
- `created_at`, `updated_at`.

### D. Sebet (Cart & CartItems)

Paydalanıwshı satıp almaqshı bolǵan zatların waqtınsha saqlaw ushın.

- **Cart:** `user` (paydalanıwshı).
- **CartItem:** `cart`, `product`, `quantity` (sanı).

### E. Buyırtpalar (Order & OrderItems)

Rásmiylestirilgen satıp alıwlar.

**Order:**

- `user`: Kim buyırtpa berdi?
- `total_price`: Ulıwma summa.
- `status`: Jaǵdayı (Kútilmekte, Tólendi, Jiberildi, Biykar etildi).
- `address`: Jetkerip beriw mánzili.
- `created_at`: Waqıt.

**OrderItems:**

- `order`, `product`, `price`, `quantity`

![image.png](attachment:9e8573b7-0dd4-4881-87ed-d18058c43c5e:image.png)

---

## 4. Funksional Talaplar (API Endpoints)

### 1. Autentifikaciya & Avtorizaciya

- **Registraciya:** Jańa paydalanıwshı dizimnen ótiwi kerek.
- **Login:** JWT token alıw (Access & Refresh token).
- **Logout:** Tokendi biykarlaw (optional).
- **Permissions:**
    - Ónimlerdi kóriw (GET) — Hámmege ruxsat (AllowAny).
    - Ónim qosıw/ózgertiw/óshiriw — Tek ǵana Adminlerge (IsAdminUser).
    - Sebet hám Buyırtpalar — Tek dizimnen ótken paydalanıwshılarǵa (IsAuthenticated).

### 2. Ónimler (Products API)

- `GET /products/`: Barlıq ónimlerdi shıǵarıw (Pagination bolıwı shárt).
- `GET /products/{id}/`: Anıq bir ónimdi kóriw.
- **Filtering & Searching:**
    - Atı boyınsha izlew (SearchFilter).
    - Bahası boyınsha filter (min_price, max_price).
    - Kategoriya boyınsha filter.
    - Sortirovka (arzanınan qımbatqa hám kerisinshe).

### 3. Sebet (Cart API)

- `GET /cart/`: Paydalanıwshınıń sebetin kóriw.
- `POST /cart/add/`: Sebetke ónim qosıw (ónim ID hám sanı).
- `DELETE /cart/remove/{id}/`: Sebetten ónimdi óshiriw.

### 4. Buyırtpa (Order API)

- `POST /orders/checkout/`: Sebetdegi zatlardan buyırtpa jaratıw. Bul jerde:
    - Ónimniń `stock` (sanı) kemeyiwi kerek.
    - Sebet tazalanıwı kerek.
- `GET /orders/`: Paydalanıwshı óziniń buyırtpalar tariyxın kóriwi kerek.

---

## 5. Texnikalıq Tapsırmalar hám Validaciya

1. **Pagination:** Hár bette 10 yamasa 20 ónim shıǵarıw kerek (`PageNumberPagination`).
2. **Validaciya:**
    - Eger ónim qoymada (stock) qalmasa, onı sebetke qosıwǵa ruxsat bermew kerek.
    - Buyırtpa berilgende ónim sanı teris (minus) bolıp qalmawı kerek.
3. **Serializer:** `ModelSerializer`dan paydalanıw hám kerek jerde Nested Serializers (mısalı, Kategoriya atın ónim ishinde kórsetiw) isletiw.

---

## 6. Bonus Tapsırmalar (Baha alıw ushın qosımsha)

Eger student tiykarǵı tapsırmanı orınlap bolsa, tómendegilerdi qossa boladı:

1. **Reviews (Pikirler):** Paydalanıwshı satıp alǵan ónimine kommentariy hám reyting (1-5 juldız) qaldıra alıwı.
2. **Signals:** Jańa paydalanıwshı dizimnen ótkende oǵan "Xosh keldińiz" degen email jiberiw (Django Signals).
3. **Docker:** Proektti Docker-compose arqalı júrgiziw.
4. **Admin Panel:** Django Admin panelin ónimlerdi qolaylı basqarıw ushın sazlaw (Search, List filter qosıw).

---

## 7. Tapsırıw Formatı

1. Proekt kodları **GitHub** repozitoriyasına júkleniwi kerek.
2. `README.md` faylı bolıwı shárt. Onda:
    - Proektti iske túsiriw boyınsha instrukciya.
    -