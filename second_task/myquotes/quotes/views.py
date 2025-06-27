from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import Author, Quote, Tag
from .forms import AuthorForm, QuoteForm
from django.core.paginator import Paginator
import requests
from bs4 import BeautifulSoup
from django.db.models import Count

class QuoteListView(ListView):
    model = Quote
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top_tags = Tag.objects.annotate(num_quotes=Count('quotes')).order_by('-num_quotes')[:10]
        context['top_tags'] = [(tag, tag.num_quotes) for tag in top_tags]
        return context
    
class AuthorDetailView(DetailView):
    model = Author
    template_name = 'quotes/author_detail.html'
    context_object_name = 'author'

class AddAuthorView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'quotes/add_author.html'
    success_url = reverse_lazy('quote-list')

class AddQuoteView(LoginRequiredMixin, CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'quotes/add_quote.html'
    success_url = reverse_lazy('quote-list')

class LoginView(LoginView):
    template_name = 'quotes/login.html'

class LogoutView(LogoutView):
    next_page = reverse_lazy('quote-list')

class TagQuotesView(ListView):
    model = Quote
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 5

    def get_queryset(self):
        tag_name = self.kwargs['tag_name']
        return Quote.objects.filter(tags__name=tag_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_tag'] = self.kwargs['tag_name']
        return context

def scrape_quotes(request):
    if not request.user.is_authenticated:
        return redirect('login')

    url = 'http://quotes.toscrape.com/page/1/'
    quotes_added = 0

    while url:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        for quote_div in soup.select('.quote'):
            text = quote_div.find(class_='text').get_text(strip=True)
            author_name = quote_div.find(class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_div.select('.tags .tag')]

            author, _ = Author.objects.get_or_create(name=author_name)

            quote, created = Quote.objects.get_or_create(text=text, author=author)
            if created:
                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    quote.tags.add(tag)
                quotes_added += 1

        next_link = soup.select_one('li.next > a')
        url = 'http://quotes.toscrape.com' + next_link['href'] if next_link else None

    return render(request, 'quotes/scrape_result.html', {'quotes_added': quotes_added})
