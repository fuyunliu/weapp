from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from poetry.models import Author, TangPoem, SongPoem, SongLyric, CaoCao, ChuLyric, LunYu, Shijing, YuanQu, HuaJianji, \
    NanTang, Strain, BaiJiaXing, XingOrigin, DiZiGui, GuWenGuanZhi, QianJiaShi, QianZiWen, SanZiJing, ShiSanBai, \
    ZhuZiJiaXun, SiShuWuJing, YouMengYing
from poetry.serializers import AuthorSerializer, TangPoemSerializer, SongPoemSerializer, SongLyricSerializer, \
    CaoCaoSerializer, ChuLyricSerializer, LunYuSerializer, ShijingSerializer, YuanQuSerializer, HuaJianjiSerializer, \
    NanTangSerializer, StrainSerializer, BaiJiaXingSerializer, XingOriginSerializer, DiZiGuiSerializer, \
    GuWenGuanZhiSerializer, QianJiaShiSerializer, QianZiWenSerializer, SanZiJingSerializer, ShiSanBaiSerializer, \
    ZhuZiJiaXunSerializer, SiShuWuJingSerializer, YouMengYingSerializer


class AuthorViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset


class TangPoemViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = TangPoem.objects.all()
    serializer_class = TangPoemSerializer
    permission_classes = [IsAuthenticated]


class SongPoemViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = SongPoem.objects.all()
    serializer_class = SongPoemSerializer
    permission_classes = [IsAuthenticated]


class SongLyricViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = SongLyric.objects.all()
    serializer_class = SongLyricSerializer
    permission_classes = [IsAuthenticated]


class CaoCaoViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = CaoCao.objects.all()
    serializer_class = CaoCaoSerializer
    permission_classes = [IsAuthenticated]


class ChuLyricViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = ChuLyric.objects.all()
    serializer_class = ChuLyricSerializer
    permission_classes = [IsAuthenticated]


class LunYuViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = LunYu.objects.all()
    serializer_class = LunYuSerializer
    permission_classes = [IsAuthenticated]


class ShijingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Shijing.objects.all()
    serializer_class = ShijingSerializer
    permission_classes = [IsAuthenticated]


class YuanQuViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = YuanQu.objects.all()
    serializer_class = YuanQuSerializer
    permission_classes = [IsAuthenticated]


class HuaJianjiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = HuaJianji.objects.all()
    serializer_class = HuaJianjiSerializer
    permission_classes = [IsAuthenticated]


class NanTangViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = NanTang.objects.all()
    serializer_class = NanTangSerializer
    permission_classes = [IsAuthenticated]


class StrainViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Strain.objects.all()
    serializer_class = StrainSerializer
    permission_classes = [IsAuthenticated]


class BaiJiaXingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = BaiJiaXing.objects.all()
    serializer_class = BaiJiaXingSerializer
    permission_classes = [IsAuthenticated]


class XingOriginViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = XingOrigin.objects.all()
    serializer_class = XingOriginSerializer
    permission_classes = [IsAuthenticated]


class DiZiGuiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = DiZiGui.objects.all()
    serializer_class = DiZiGuiSerializer
    permission_classes = [IsAuthenticated]


class GuWenGuanZhiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = GuWenGuanZhi.objects.all()
    serializer_class = GuWenGuanZhiSerializer
    permission_classes = [IsAuthenticated]


class QianJiaShiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = QianJiaShi.objects.all()
    serializer_class = QianJiaShiSerializer
    permission_classes = [IsAuthenticated]


class QianZiWenViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = QianZiWen.objects.all()
    serializer_class = QianZiWenSerializer
    permission_classes = [IsAuthenticated]


class SanZiJingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = SanZiJing.objects.all()
    serializer_class = SanZiJingSerializer
    permission_classes = [IsAuthenticated]


class ShiSanBaiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShiSanBai.objects.all()
    serializer_class = ShiSanBaiSerializer
    permission_classes = [IsAuthenticated]


class ZhuZiJiaXunViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = ZhuZiJiaXun.objects.all()
    serializer_class = ZhuZiJiaXunSerializer
    permission_classes = [IsAuthenticated]


class SiShuWuJingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = SiShuWuJing.objects.all()
    serializer_class = SiShuWuJingSerializer
    permission_classes = [IsAuthenticated]


class YouMengYingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = YouMengYing.objects.all()
    serializer_class = YouMengYingSerializer
    permission_classes = [IsAuthenticated]
