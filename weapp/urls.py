from django.conf import settings

from django.urls import path, include
from rest_framework import routers

from likes import views as likes_views
from follows import views as follows_views
from comments import views as comments_views
from collects import views as collects_views
from oauth import views as oauth_views
from poetry import views as poetry_views
from polls import views as polls_views
from taggit import views as taggit_views
from weblog import views as weblog_views
from wechat import views as wechat_views


router = routers.DefaultRouter()

# 账户
router.register('users', oauth_views.UserViewSet, 'user')
router.register('profiles', oauth_views.ProfileViewSet, 'profile')
router.register('groups', oauth_views.GroupViewSet, 'group')

# 博客
router.register('posts', weblog_views.PostViewSet, 'post')
router.register('articles', weblog_views.ArticleViewSet, 'article')
router.register('categories', weblog_views.CategoryViewSet, 'category')
router.register('topics', weblog_views.TopicViewSet, 'topic')

# 动作
router.register('tags', taggit_views.TagViewSet, 'tag')
router.register('collections', collects_views.CollectionViewSet, 'collection')
router.register('collected-items', collects_views.CollectViewSet, 'collected_items')
router.register('commented-items', comments_views.CommentViewSet, 'commented_items')
router.register('followed-items', follows_views.FollowViewSet, 'followed_items')
router.register('liked-items', likes_views.LikeViewSet, 'liked_items')
router.register('tagged-items', taggit_views.TaggedItemViewSet, 'tagged_items')

# 投票
router.register('questions', polls_views.QuestionViewSet, 'question')
router.register('choices', polls_views.ChoiceViewSet, 'choice')
router.register('votes', polls_views.VoteViewSet, 'vote')

# 诗歌
router.register('authors', poetry_views.AuthorViewSet, 'author')
router.register('tangpoem', poetry_views.TangPoemViewSet, 'tangpoem')
router.register('songpoem', poetry_views.SongPoemViewSet, 'songpoem')
router.register('songlyric', poetry_views.SongLyricViewSet, 'songlyric')
router.register('caocao', poetry_views.CaoCaoViewSet, 'caocao')
router.register('chulyric', poetry_views.ChuLyricViewSet, 'chulyric')
router.register('lunyu', poetry_views.LunYuViewSet, 'lunyu')
router.register('shijing', poetry_views.ShijingViewSet, 'shijing')
router.register('yuanqu', poetry_views.YuanQuViewSet, 'yuanqu')
router.register('huajianji', poetry_views.HuaJianjiViewSet, 'huajianji')
router.register('nantang', poetry_views.NanTangViewSet, 'nantang')
router.register('strains', poetry_views.StrainViewSet, 'strain')
router.register('baijiaxing', poetry_views.BaiJiaXingViewSet, 'baijiaxing')
router.register('xingorigin', poetry_views.XingOriginViewSet, 'xingorigin')
router.register('dizigui', poetry_views.DiZiGuiViewSet, 'dizigui')
router.register('guwenguanzhi', poetry_views.GuWenGuanZhiViewSet, 'guwenguanzhi')
router.register('qianjiashi', poetry_views.QianJiaShiViewSet, 'qianjiashi')
router.register('qianziwen', poetry_views.QianZiWenViewSet, 'qianziwen')
router.register('sanzijing', poetry_views.SanZiJingViewSet, 'sanzijing')
router.register('shisanbai', poetry_views.ShiSanBaiViewSet, 'shisanbai')
router.register('zhuzijiaxun', poetry_views.ZhuZiJiaXunViewSet, 'zhuzijiaxun')
router.register('sishuwujing', poetry_views.SiShuWuJingViewSet, 'sishuwujing')
router.register('youmengying', poetry_views.YouMengYingViewSet, 'youmengying')

# 聊天
router.register('messages', wechat_views.MessageViewSet, 'message')

urlpatterns = router.urls
urlpatterns += [
    path('token/', oauth_views.TokenView.as_view(), name='token'),
    path('captcha/', oauth_views.CaptchaView.as_view(), name='captcha')
]


if settings.DEBUG:
    import debug_toolbar
    from django.contrib import admin
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += [
        path('admin/', admin.site.urls),

        # Django Debug Tools
        path('__debug__/', include(debug_toolbar.urls)),

        # Browsable API Login
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

        # Your Patterns
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

        # Optional UI:
        path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
