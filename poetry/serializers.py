from rest_framework import serializers
from poetry.models import Author, TangPoem, SongPoem, SongLyric, CaoCao, ChuLyric, \
    LunYu, Shijing, YuanQu, HuaJianji, NanTang, Strain, BaiJiaXing, XingOrigin, DiZiGui, \
    GuWenGuanZhi, QianJiaShi, QianZiWen, SanZiJing, ShiSanBai, ZhuZiJiaXun, SiShuWuJing, YouMengYing


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class TangPoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TangPoem
        fields = '__all__'


class SongPoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongPoem
        fields = '__all__'


class SongLyricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongLyric
        fields = '__all__'


class CaoCaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaoCao
        fields = '__all__'


class ChuLyricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChuLyric
        fields = '__all__'


class LunYuSerializer(serializers.ModelSerializer):
    class Meta:
        model = LunYu
        fields = '__all__'


class ShijingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shijing
        fields = '__all__'


class YuanQuSerializer(serializers.ModelSerializer):
    class Meta:
        model = YuanQu
        fields = '__all__'


class HuaJianjiSerializer(serializers.ModelSerializer):
    class Meta:
        model = HuaJianji
        fields = '__all__'


class NanTangSerializer(serializers.ModelSerializer):
    class Meta:
        model = NanTang
        fields = '__all__'


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = '__all__'


class BaiJiaXingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaiJiaXing
        fields = '__all__'


class XingOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = XingOrigin
        fields = '__all__'


class DiZiGuiSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiZiGui
        fields = '__all__'


class GuWenGuanZhiSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuWenGuanZhi
        fields = '__all__'


class QianJiaShiSerializer(serializers.ModelSerializer):
    class Meta:
        model = QianJiaShi
        fields = '__all__'


class QianZiWenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QianZiWen
        fields = '__all__'


class SanZiJingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanZiJing
        fields = '__all__'


class ShiSanBaiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiSanBai
        fields = '__all__'


class ZhuZiJiaXunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZhuZiJiaXun
        fields = '__all__'


class SiShuWuJingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiShuWuJing
        fields = '__all__'


class YouMengYingSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouMengYing
        fields = '__all__'
