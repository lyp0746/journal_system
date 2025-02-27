# testing/forms.py
from django import forms
from .models import TestUser

class TestUserForm(forms.Form):
    """创建测试用户表单"""
    test_role = forms.ChoiceField(
        choices=TestUser.TEST_ROLES,
        label='测试角色',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    test_scenario = forms.CharField(
        max_length=50,
        required=False,
        label='测试场景',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    expiry_days = forms.IntegerField(
        min_value=1,
        max_value=30,
        initial=7,
        label='有效期(天)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


# testing/forms.py (继续添加)
from .models import TestFeedback


class TestFeedbackForm(forms.ModelForm):
    """测试反馈表单"""

    class Meta:
        model = TestFeedback
        exclude = ['test_session', 'created_at']
        widgets = {
            'satisfaction_rating': forms.RadioSelect(),
            'ui_rating': forms.RadioSelect(),
            'usability_rating': forms.RadioSelect(),
            'performance_rating': forms.RadioSelect(),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'encountered_issues': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'suggestions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }