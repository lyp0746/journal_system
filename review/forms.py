# review/forms.py
from django import forms
from .models import Review, EditorDecision


class ReviewForm(forms.ModelForm):
    """审稿表单"""

    class Meta:
        model = Review
        fields = ('recommendation', 'comments_to_author', 'comments_to_editor',
                  'score_originality', 'score_methodology', 'score_literature',
                  'score_writing', 'review_file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

            # 文本域字段
        self.fields['comments_to_author'].widget.attrs['rows'] = 8
        self.fields['comments_to_editor'].widget.attrs['rows'] = 5

        # 评分字段限制
        for field_name in ['score_originality', 'score_methodology', 'score_literature', 'score_writing']:
            self.fields[field_name].widget.attrs['min'] = 1
            self.fields[field_name].widget.attrs['max'] = 5
            self.fields[field_name].widget.attrs['type'] = 'number'

            # 帮助文本
        self.fields['recommendation'].help_text = '请选择您对此稿件的评审建议'
        self.fields['comments_to_author'].help_text = '此评语将直接发送给作者'
        self.fields['comments_to_editor'].help_text = '此评语仅编辑可见，不会发送给作者'
        self.fields['review_file'].help_text = '可选上传审稿附件'


class ReviewInvitationResponseForm(forms.Form):
    """审稿邀请回复表单"""
    RESPONSE_CHOICES = (
        ('ACCEPT', '接受审稿邀请'),
        ('DECLINE', '婉拒审稿邀请'),
    )

    response = forms.ChoiceField(choices=RESPONSE_CHOICES, widget=forms.RadioSelect)
    reason = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['reason'].help_text = '如果婉拒，请简要说明原因'


class AssignReviewersForm(forms.Form):
    """分配审稿人表单"""
    reviewers = forms.ModelMultipleChoiceField(
        queryset=None,  # 将在视图中设置
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        reviewers_queryset = kwargs.pop('reviewers_queryset', None)
        super().__init__(*args, **kwargs)
        if reviewers_queryset is not None:
            self.fields['reviewers'].queryset = reviewers_queryset


class EditorDecisionForm(forms.ModelForm):
    """编辑决定表单"""

    class Meta:
        model = EditorDecision
        fields = ('decision', 'comments')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['comments'].widget.attrs['rows'] = 5
        self.fields['comments'].help_text = '请提供决定的详细理由，这将发送给作者'


# review/forms.py (添加以下代码)
class DateRangeForm(forms.Form):
    """日期范围选择表单"""
    start_date = forms.DateField(
        label='开始日期',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    end_date = forms.DateField(
        label='结束日期',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("开始日期不能晚于结束日期")

        return cleaned_data