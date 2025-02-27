# submission/models.py  
from django.db import models


class Category(models.Model):
    """期刊栏目分类"""
    name = models.CharField(max_length=100, verbose_name='栏目名称')
    description = models.TextField(blank=True, verbose_name='栏目描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '期刊栏目'
        verbose_name_plural = '期刊栏目管理'

    def __str__(self):
        return self.name

    # submission/models.py 继续添加


from django.conf import settings


class Paper(models.Model):
    """论文投稿模型"""
    STATUS_CHOICES = (
        ('DRAFT', '草稿'),
        ('SUBMITTED', '已投稿'),
        ('INITIAL_CHECK', '初审中'),
        ('UNDER_REVIEW', '审稿中'),
        ('REVISION_REQUIRED', '需要修改'),
        ('REJECTED', '已拒绝'),
        ('ACCEPTED', '已接受'),
        ('PUBLISHED', '已发表'),
    )

    title = models.CharField(max_length=200, verbose_name='论文标题')
    abstract = models.TextField(verbose_name='摘要')
    keywords = models.CharField(max_length=200, verbose_name='关键词')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='所属栏目')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_papers',
                               verbose_name='投稿作者')

    # 作者信息
    co_authors = models.TextField(blank=True, verbose_name='共同作者信息')
    corresponding_author = models.CharField(max_length=100, blank=True, verbose_name='通讯作者')
    corresponding_email = models.EmailField(blank=True, verbose_name='通讯作者邮箱')

    # 文件
    manuscript_file = models.FileField(upload_to='manuscripts/%Y/%m/', verbose_name='论文文件')
    cover_letter = models.FileField(upload_to='cover_letters/%Y/%m/', blank=True, null=True, verbose_name='投稿信')
    supplementary_file = models.FileField(upload_to='supplementary/%Y/%m/', blank=True, null=True,
                                          verbose_name='补充材料')

    # 状态跟踪
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name='论文状态')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='投稿时间')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    # 编辑处理
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='edited_papers', verbose_name='负责编辑')
    editor_comments = models.TextField(blank=True, verbose_name='编辑备注')

    # 审稿管理
    is_anonymous = models.BooleanField(default=True, verbose_name='匿名评审')

    class Meta:
        verbose_name = '论文'
        verbose_name_plural = '论文管理'

    def __str__(self):
        return self.title


# submission/models.py 继续添加

class Revision(models.Model):
    """论文修改记录模型"""
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='revisions', verbose_name='论文')
    version = models.IntegerField(verbose_name='修改版本')
    manuscript_file = models.FileField(upload_to='revisions/%Y/%m/', verbose_name='修改后论文')
    cover_letter = models.FileField(upload_to='revision_letters/%Y/%m/', blank=True, null=True, verbose_name='修改说明')

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    response_to_reviewers = models.TextField(blank=True, verbose_name='对审稿意见的回应')

    class Meta:
        verbose_name = '论文修改记录'
        verbose_name_plural = '论文修改记录管理'

    def __str__(self):
        return f"{self.paper.title} - 修改版本 {self.version}"


# submission/models.py 继续添加

class Issue(models.Model):
    """期刊期次模型"""
    volume = models.IntegerField(verbose_name='卷号')
    number = models.IntegerField(verbose_name='期号')
    year = models.IntegerField(verbose_name='年份')
    publication_date = models.DateField(verbose_name='出版日期')
    is_current = models.BooleanField(default=False, verbose_name='是否当前期')
    cover_image = models.ImageField(upload_to='issue_covers/%Y/%m/', blank=True, null=True, verbose_name='封面图片')
    description = models.TextField(blank=True, verbose_name='期刊描述')

    papers = models.ManyToManyField(Paper, related_name='issues', blank=True, verbose_name='收录论文')

    class Meta:
        verbose_name = '期刊期次'
        verbose_name_plural = '期刊期次管理'

    def __str__(self):
        return f"第{self.volume}卷 第{self.number}期 ({self.year}年)"

