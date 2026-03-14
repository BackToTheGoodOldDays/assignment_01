import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'api-gateway-secret-key-2024')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'proxy',
    'web',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gateway.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
WSGI_APPLICATION = 'gateway.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True

# Service URLs
STAFF_SERVICE_URL = os.getenv('STAFF_SERVICE_URL', 'http://localhost:8001')
MANAGER_SERVICE_URL = os.getenv('MANAGER_SERVICE_URL', 'http://localhost:8002')
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:8003')
CATALOG_SERVICE_URL = os.getenv('CATALOG_SERVICE_URL', 'http://localhost:8004')
BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8005')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://localhost:8006')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://localhost:8007')
SHIP_SERVICE_URL = os.getenv('SHIP_SERVICE_URL', 'http://localhost:8008')
PAY_SERVICE_URL = os.getenv('PAY_SERVICE_URL', 'http://localhost:8009')
COMMENT_SERVICE_URL = os.getenv('COMMENT_SERVICE_URL', 'http://localhost:8010')
RECOMMENDER_SERVICE_URL = os.getenv('RECOMMENDER_SERVICE_URL', 'http://localhost:8011')

SERVICE_MAP = {
    # staff-service
    'staff': STAFF_SERVICE_URL,
    'inventory-logs': STAFF_SERVICE_URL,
    # manager-service
    'managers': MANAGER_SERVICE_URL,
    # customer-service
    'customers': CUSTOMER_SERVICE_URL,
    # catalog-service
    'categories': CATALOG_SERVICE_URL,
    'authors': CATALOG_SERVICE_URL,
    'publishers': CATALOG_SERVICE_URL,
    # book-service
    'books': BOOK_SERVICE_URL,
    'statuses': BOOK_SERVICE_URL,
    # cart-service
    'carts': CART_SERVICE_URL,
    'cart-items': CART_SERVICE_URL,
    # order-service
    'orders': ORDER_SERVICE_URL,
    # ship-service
    'shipping-methods': SHIP_SERVICE_URL,
    'shipments': SHIP_SERVICE_URL,
    # pay-service
    'payment-methods': PAY_SERVICE_URL,
    'payments': PAY_SERVICE_URL,
    # comment-rate-service
    'reviews': COMMENT_SERVICE_URL,
    # recommender-ai-service
    'interactions': RECOMMENDER_SERVICE_URL,
    'recommendations': RECOMMENDER_SERVICE_URL,
    'trending': RECOMMENDER_SERVICE_URL,
    'best-rated': RECOMMENDER_SERVICE_URL,
    'similar': RECOMMENDER_SERVICE_URL,
}
