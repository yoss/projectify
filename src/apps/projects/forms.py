from django import forms
from .models import Project
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, MultiWidgetField
from crispy_forms.bootstrap import FormActions
from django.utils.html import format_html

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'is_active', 'is_public', 'is_chargable', 'client', 'managers', 'members']
        widgets = {
            'managers': forms.CheckboxSelectMultiple(),
            'members': forms.CheckboxSelectMultiple(),
        }
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_url = Project.get_list_url()

    @property
    def helper(self):    
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-4'
        helper.layout = Layout(
            'name',
            'client',
            'managers',
            'members',
            'is_active',
            'is_public',
            'is_chargable',
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary btn-sm'),
                HTML(format_html('<a class="btn btn-outline-primary btn-sm" href="{}">Cancel</a>', self.cancel_url)),
            ),
        )
        return helper
