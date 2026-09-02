from django import forms
from .models import (
    EducationDetail,
    FamilyDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
)


class BaseStyledModelForm(forms.ModelForm):
    """Applies unified styling classes and error states to form widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'form-checkbox'})
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.update({'class': 'form-input form-select'})
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({'class': 'form-input form-textarea', 'rows': 4})
            else:
                widget.attrs.update({'class': 'form-input'})


class ProfileBasicForm(BaseStyledModelForm):
    """Form for basic biographical and matrimonial information."""

    date_of_birth = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
        }),
        help_text='Used to calculate your age. Age is shown on your profile.',
    )

    class Meta:
        model = Profile
        fields = (
            'display_name',
            'gender',
            'date_of_birth',
            'height_cm',
            'marital_status',
            'profile_created_for',
            'religion',
            'caste',
            'sub_caste',
            'mother_tongue',
            'country',
            'state',
            'city',
            'citizenship',
            'about_me',
            'visibility',
        )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
            if age > 100:
                raise forms.ValidationError('Please provide a valid date of birth.')
        return dob


class EducationForm(BaseStyledModelForm):
    class Meta:
        model = EducationDetail
        fields = (
            'highest_education',
            'ug_degree',
            'pg_degree',
            'institution',
            'field_of_study',
        )


class ProfessionForm(BaseStyledModelForm):
    class Meta:
        model = ProfessionDetail
        fields = (
            'occupation',
            'industry',
            'employer',
            'annual_income',
            'working_city',
            'working_country',
            'income_visible',
        )


class FamilyForm(BaseStyledModelForm):
    class Meta:
        model = FamilyDetail
        fields = (
            'family_type',
            'family_values',
            'family_status',
            'father_occupation',
            'mother_occupation',
            'brothers_count',
            'sisters_count',
            'living_with_parents',
            'family_location',
            'about_family',
        )


class LifestyleForm(BaseStyledModelForm):
    class Meta:
        model = LifestyleDetail
        fields = (
            'diet',
            'smoking',
            'drinking',
            'hobbies',
            'spoken_languages',
        )


class PartnerPreferenceForm(BaseStyledModelForm):
    class Meta:
        model = PartnerPreference
        fields = (
            'min_age',
            'max_age',
            'min_height_cm',
            'max_height_cm',
            'preferred_marital_status',
            'preferred_religion',
            'preferred_mother_tongue',
            'preferred_education',
            'preferred_occupation',
            'preferred_country',
            'preferred_diet',
            'notes',
        )

    def clean(self):
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')
        min_height = cleaned_data.get('min_height_cm')
        max_height = cleaned_data.get('max_height_cm')

        if min_age and max_age and min_age > max_age:
            self.add_error('max_age', 'Maximum age cannot be less than minimum age.')

        if min_height and max_height and min_height > max_height:
            self.add_error('max_height_cm', 'Maximum height cannot be less than minimum height.')

        return cleaned_data


class ProfilePhotoUploadForm(BaseStyledModelForm):
    """Form to handle photo uploading."""

    class Meta:
        model = ProfilePhoto
        fields = (
            'image',
            'caption',
            'is_primary',
            'visibility',
        )
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
        }
