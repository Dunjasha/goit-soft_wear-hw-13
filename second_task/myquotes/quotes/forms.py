from django import forms
from .models import Author, Quote, Tag

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'born_date', 'bio']

class QuoteForm(forms.ModelForm):
    tags = forms.CharField(help_text='Введіть теги через кому')

    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']

    def clean_tags(self):
        tags_str = self.cleaned_data['tags']
        tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]
        return tags_list

    def save(self, commit=True):
        quote = super().save(commit=False)
        tags_list = self.cleaned_data['tags']
        if commit:
            quote.save()
            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                quote.tags.add(tag)
        return quote
