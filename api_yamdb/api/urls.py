from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, PersonalUserViewSet, signup, token_emission,
                    ReviewViewSet, CommentViewSet, TitleViewSet,
                    CategoryViewSet, GenreViewSet)


router = DefaultRouter()

router.register('users', UserViewSet)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename="reviews"
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename="comments"
)

personal_view_set = PersonalUserViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update'
})

urlpatterns = [
    path('v1/auth/token/', token_emission, name='token_emission'),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/users/me/', personal_view_set, name='users_me'),
    path('v1/', include(router.urls)),
]
