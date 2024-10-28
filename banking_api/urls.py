from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AccountViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="Your API description",
      terms_of_service="https://www.yourapp.com/terms/",
      contact=openapi.Contact(email="contact@yourapp.com"),
      license=openapi.License(name="Your License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]