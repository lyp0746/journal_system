# submission/forms.py
from django import forms
from .models import Paper, Revision, Category


class PaperSubmissionForm(forms.ModelForm):
    """论文投稿表单"""

    class Meta:
        model = Paper
        fields = ('title', 'abstract', 'keywords', 'category', 'co_authors',
                  'corresponding_author', 'corresponding_email', 'manuscript_file',
                  'cover_letter', 'supplementary_file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

            # 文本域字段
        self.fields['abstract'].widget.attrs['rows'] = 5
        self.fields['co_authors'].widget.attrs['rows'] = 3
        self.fields['co_authors'].widget.attrs['placeholder'] = '请按格式填写: 姓名, 单位, 邮箱'

        # 帮助文本
        self.fields['keywords'].help_text = '请用分号(;)分隔关键词'
        self.fields['co_authors'].help_text = '每行一位共同作者，格式：姓名, 单位, 邮箱'
        self.fields['manuscript_file'].help_text = '请上传Word格式(.docx)或PDF格式(.pdf)的论文文件'
        self.fields['cover_letter'].help_text = '投稿信(可选)'
        self.fields['supplementary_file'].help_text = '补充材料(可选)'


class RevisionForm(forms.ModelForm):
    """论文修改表单"""

    class Meta:
        model = Revision
        fields = ('manuscript_file', 'cover_letter', 'response_to_reviewers')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['response_to_reviewers'].widget.attrs['rows'] = 10
        self.fields['response_to_reviewers'].widget.attrs['placeholder'] = '请详细回应审稿人的每一条意见，并说明修改内容...'
        self.fields['manuscript_file'].help_text = '请上传修改后的论文文件'
        self.fields['cover_letter'].help_text = '修改说明(可选)'