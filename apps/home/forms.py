from django import forms
from .models import Keyword, Domain


class RegisterDomainForm(forms.ModelForm):
    class Meta():
        model = Domain
        fields = ("name", )
        labels = {
            "name":"ドメイン名",
        }

class RegisterKeywordForm(forms.ModelForm):
    class Meta():
        model = Keyword
        fields = (
            "domain",
            "name", )
        labels = {
            "domain":"ドメイン名",
            "name":"キーワード名",
        }

class AnalysisForm(forms.Form):
    keyword = forms.CharField(label='キーワード')
    url = forms.CharField(label='分析対象のURL')
