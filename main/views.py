from django.core.mail import send_mail
from django.conf import settings

from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Boulangerie, Contact, Categorie, Produit

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views import View
from .forms import CategorieForm, ProduitForm

# =================================================

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# =================================================

def accueil(request):
    # Récupérer la première boulangerie dans la base de données
    boulangerie = Boulangerie.objects.first()

    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Enregistrer les données dans la base de données
        Contact.objects.create(nom=nom, email=email, message=message)

        # Générer le contenu HTML de l'e-mail
        sujet = "Confirmation de réception de votre message"
        message_html = render_to_string('main/emails/confirmation_email.html', {
            'nom': nom,
            'message': message,
            'boulangerie': boulangerie,
        })

        # Envoyer l'e-mail
        send_mail( 
            sujet,
            None,  # Le message en texte brut (None car on utilise HTML)
            'noreply@votredomaine.com',  # Adresse e-mail de l'expéditeur
            [email],  # Adresse e-mail du destinataire
            html_message=message_html,  # Contenu HTML de l'e-mail
            fail_silently=False,
        )

        # Afficher un message de confirmation
        messages.success(request, 'Votre message a bien été envoyé ! Un e-mail de confirmation vous a été envoyé.')

        # Rediriger vers la page d'accueil pour éviter la soumission multiple du formulaire
        return redirect('accueil')

    # Afficher la page d'accueil avec le formulaire vide
    return render(request, 'main/home/accueil.html', {'boulangerie': boulangerie})

# ===================================================

def get_boulangerie():
    """Récupère les infos de la boulangerie"""
    return Boulangerie.objects.first() or Boulangerie.objects.create(
        nom="La Boulangerie Dorée",
        adresse="123 Rue du Pain",
        code="75001",
        ville="Paris",
        telephone="0123456789"
    )

def commander(request):
    """Affiche la page de commande avec tous les produits"""
    categories = Categorie.objects.all().order_by('ordre')
    boulangerie = get_boulangerie()
    
    context = {
        'categories': categories,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/client/commander.html', context)

def panier(request):
    """Affiche la page du panier"""
    boulangerie = get_boulangerie()
    
    context = {
        'boulangerie': boulangerie,
    }
    return render(request, 'main/client/panier.html', context)

@require_http_methods(["GET"])
def api_produits(request):
    """API pour récupérer tous les produits en JSON"""
    produits_data = []
    
    for produit in Produit.objects.select_related('categorie').all():
        produits_data.append({
            'id': produit.id,
            'nom': produit.nom,
            'description': produit.description,
            'prix': str(produit.prix),
            'categorie': {
                'id': produit.categorie.id,
                'nom': produit.categorie.nom
            },
            'image': produit.image.url if produit.image else None
        })
    
    return JsonResponse({'produits': produits_data})

# =================================================


# ============ categorie ====================

class DashboardGerantView(TemplateView):
    template_name = 'main/gerant/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les informations de la boulangerie
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class CategorieListView(ListView):
    model = Categorie
    template_name = 'main/gerant/categorie_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class CategorieCreateView(CreateView):
    model = Categorie
    form_class = CategorieForm
    template_name = 'main/gerant/categorie_form.html'
    success_url = reverse_lazy('liste_categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie créée avec succès!')
        return super().form_valid(form)

class CategorieUpdateView(UpdateView):
    model = Categorie
    form_class = CategorieForm
    template_name = 'main/gerant/categorie_form.html'
    success_url = reverse_lazy('liste_categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie modifiée avec succès!')
        return super().form_valid(form)

class CategorieDeleteView(View):
    def post(self, request, pk):
        categorie = get_object_or_404(Categorie, pk=pk)
        categorie.delete()
        messages.success(request, 'Catégorie supprimée avec succès!')
        return redirect('liste_categories')

#  ============ produit =================

class ProduitListView(ListView):
    model = Produit
    template_name = 'main/gerant/produit_list.html'
    context_object_name = 'produits'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class ProduitCreateView(CreateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'main/gerant/produit_form.html'
    success_url = reverse_lazy('liste_produits')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Produit créé avec succès!')
        return super().form_valid(form)

class ProduitUpdateView(UpdateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'main/gerant/produit_form.html'
    success_url = reverse_lazy('liste_produits')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Produit modifié avec succès!')
        return super().form_valid(form)

class ProduitDeleteView(View):
    def post(self, request, pk):
        produit = get_object_or_404(Produit, pk=pk)
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès!')
        return redirect('liste_produits')