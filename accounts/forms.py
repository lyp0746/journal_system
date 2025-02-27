# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True, help_text='必填。请输入有效的电子邮件地址。')
    phone = forms.CharField(max_length=20, required=False, help_text='选填。请输入您的联系电话。')
    institution = forms.CharField(max_length=100, required=True, help_text='必填。请输入您所在的机构或单位。')
    title = forms.CharField(max_length=50, required=False, help_text='选填。请输入您的职称或职位。')
    address = forms.CharField(max_length=200, required=False, help_text='选填。请输入您的通讯地址。')
    research_field = forms.CharField(max_length=100, required=False, help_text='选填。请输入您的研究领域。')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                  'phone', 'institution', 'title', 'address', 'research_field', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # 默认角色为作者
        self.fields['role'].initial = 'AUTHOR'
        self.fields['role'].widget = forms.Select(choices=[
            ('AUTHOR', '作者'),
            ('REVIEWER', '审稿人')
        ])


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].label = '用户名'
        self.fields['password'].label = '密码'


class UserProfileForm(forms.ModelForm):
    """用户资料表单"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'institution',
                  'title', 'address', 'bio', 'research_field')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加Bootstrap类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'