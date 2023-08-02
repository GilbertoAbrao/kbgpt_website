from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import User
from .models import BotModel, BotFileModel


class RegisterForm(UserCreationForm):
    cellphone = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'cellphone',)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)


class FileUploadForm(forms.Form):
    file = forms.FileField(label='Select a file', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'docx'])])

    # set class to file field
    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'class': 'form-control'})


class BotForm(forms.ModelForm):
    class Meta:
        model = BotModel
        fields = ('name', 'description', 'status')

    def __init__(self, *args, **kwargs):
        super(BotForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(FloatingField('name'), css_class='col-md-8'),
            Div(FloatingField('status'), css_class='col-md-4'),
            Div(FloatingField('description'), css_class='col-md-12'),
        )


class BotFileForm(forms.ModelForm):

    class Meta:
        model = BotFileModel
        fields = ('name', 'path',)
    
    def __init__(self, *args, **kwargs):
        super(BotFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(FloatingField('name'), css_class='col-md-6'),
            Div(FloatingField('path'), css_class='col-md-6'),
        )


class QAForm(forms.Form):
    # select the bot
    bot = forms.ModelChoiceField(queryset=BotModel.objects.all())
    question = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(QAForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(FloatingField('bot'), css_class='col-md-6'),
            Div(css_class='col-md-6'),
            Div(FloatingField('question'), css_class='col-md-12'),
        )