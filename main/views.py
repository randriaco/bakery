from email.headerregistry import Group
import traceback
from django.core.mail import send_mail
from django.conf import settings

import stripe

from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Boulangerie, Contact, Categorie, Produit

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views import View
from .forms import CategorieForm, InscriptionForm, ProduitForm

# =================================================

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# =================================================

from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import (
    FrequenceCollecte, HoraireHebdomadaire, 
    FermetureSpecifique, FermetureMultiJours,
    Boulangerie
)
from .forms import (
    FrequenceForm, HoraireHebdomadaireForm,
    FermetureSpecifiqueForm, FermetureMultiJoursForm
)
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import CodeVerification

# réinitialisation mdp 

from .models import TokenReinitialisationMotDePasse
from django.contrib.auth.hashers import make_password
from django.urls import reverse

# système de paiement stripe

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Commande, LigneCommande, NotificationCommande
from django.db import transaction
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import io
from django.core.files.base import ContentFile
import os

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Import manquant pour models
from django.db import models as django_models
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Commande, NotificationCommande
from django.db.models import Sum

# statut - code de recuperation

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
import random

from django.contrib.auth import update_session_auth_hash
from .forms import BoulangerieInfoForm, CustomPasswordChangeForm

from django.core.mail import send_mail, EmailMultiAlternatives
from .forms import GerantInfoForm 

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import CreerPersonnelForm  # Ajoutez ceci à vos imports

from django.db.models import Q, Count
from datetime import datetime, timedelta

# pour proteger les pages gerant

def is_gerant(user):
    """
    True si l'utilisateur est staff, superuser, username 'randr'
    ou fait partie du groupe 'Gerants'.
    """
    return (
        user.is_active
        and (
            user.is_staff
            or user.is_superuser
            or user.username == 'randr'
            or user.groups.filter(name='Gerants').exists()
        )
    )

class GerantRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'connexion_pro'
    def test_func(self):
        return is_gerant(self.request.user)
    
# fin protection pages gerant

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

@login_required
def commander(request):
    """Affiche la page de commande avec tous les produits"""
    categories = Categorie.objects.all().order_by('ordre')
    boulangerie = get_boulangerie()
    
    context = {
        'categories': categories,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/client/commander.html', context)

@login_required
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

# ============ categorie ====================
class DashboardGerantView(GerantRequiredMixin, TemplateView):
    template_name = 'main/gerant/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les informations de la boulangerie
        context['boulangerie'] = Boulangerie.objects.first()
        return context
    
class DashboardClientView(GerantRequiredMixin, TemplateView):
    template_name = 'main/client/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les informations de la boulangerie
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class CategorieListView(GerantRequiredMixin, ListView):
    model = Categorie
    template_name = 'main/gerant/categorie_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class CategorieCreateView(GerantRequiredMixin, CreateView):
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

class CategorieUpdateView(GerantRequiredMixin, UpdateView):
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
class ProduitListView(GerantRequiredMixin, ListView):
    model = Produit
    template_name = 'main/gerant/produit_list.html'
    context_object_name = 'produits'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boulangerie'] = Boulangerie.objects.first()
        return context

class ProduitCreateView(GerantRequiredMixin, CreateView):
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

class ProduitUpdateView(GerantRequiredMixin, UpdateView):
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
    
# ===================== ajout horaires click and collect ==========

# Vue pour la fréquence
@login_required(login_url='connexion_pro')
def frequence_collecte(request):
    boulangerie = get_boulangerie()
    frequence, created = FrequenceCollecte.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = FrequenceForm(request.POST, instance=frequence)
        if form.is_valid():
            form.save()
            messages.success(request, 'La fréquence a été mise à jour avec succès.')
            return redirect('frequence_collecte')
    else:
        form = FrequenceForm(instance=frequence)
    
    context = {
        'form': form,
        'frequence': frequence,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/gerant/frequence_collecte.html', context)

# Vue pour les horaires hebdomadaires
@login_required(login_url='connexion_pro')
def horaires_hebdomadaires(request):
    boulangerie = get_boulangerie()
    
    # Créer les 7 jours s'ils n'existent pas
    for jour in range(7):
        HoraireHebdomadaire.objects.get_or_create(jour=jour)
    
    if request.method == 'POST':
        # Traiter chaque jour
        for jour in range(7):
            horaire = HoraireHebdomadaire.objects.get(jour=jour)
            form = HoraireHebdomadaireForm(
                request.POST, 
                instance=horaire, 
                prefix=str(jour)
            )
            if form.is_valid():
                form.save()
        
        messages.success(request, 'Les horaires ont été mis à jour avec succès.')
        return redirect('horaires_hebdomadaires')
    
    # Préparer les formulaires pour chaque jour
    jours_forms = []
    for jour in range(7):
        horaire = HoraireHebdomadaire.objects.get(jour=jour)
        form = HoraireHebdomadaireForm(instance=horaire, prefix=str(jour))
        jours_forms.append({
            'jour': horaire.get_jour_display(),
            'form': form,
            'horaire': horaire
        })
    
    context = {
        'jours_forms': jours_forms,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/gerant/horaires_hebdomadaires.html', context)

# Vue pour les fermetures spécifiques
@login_required(login_url='connexion_pro')
def fermetures_specifiques(request):
    boulangerie = get_boulangerie()
    
    if request.method == 'POST':
        form = FermetureSpecifiqueForm(request.POST)
        if form.is_valid():
            fermeture = form.save()
            messages.success(request, f'Fermeture ajoutée pour le {fermeture.date}')
            # TODO: Envoyer email si notifier_clients est True
            return redirect('fermetures_specifiques')
    else:
        form = FermetureSpecifiqueForm()
    
    # Récupérer les fermetures futures
    fermetures = FermetureSpecifique.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')
    
    context = {
        'form': form,
        'fermetures': fermetures,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/gerant/fermetures_specifiques.html', context)

# Vue pour supprimer une fermeture spécifique
@login_required(login_url='connexion_pro')
def supprimer_fermeture_specifique(request, pk):
    fermeture = get_object_or_404(FermetureSpecifique, pk=pk)
    fermeture.delete()
    messages.success(request, 'La fermeture a été supprimée.')
    return redirect('fermetures_specifiques')

# Vue pour les fermetures multi-jours
@login_required(login_url='connexion_pro')
def fermetures_multi_jours(request):
    boulangerie = get_boulangerie()
    
    if request.method == 'POST':
        form = FermetureMultiJoursForm(request.POST)
        if form.is_valid():
            fermeture = form.save()
            messages.success(request, f'Période de fermeture ajoutée du {fermeture.date_debut} au {fermeture.date_fin}')
            # TODO: Envoyer email si notifier_clients est True
            return redirect('fermetures_multi_jours')
    else:
        form = FermetureMultiJoursForm()
    
    # Récupérer les fermetures futures et en cours
    today = timezone.now().date()
    fermetures = FermetureMultiJours.objects.filter(
        date_fin__gte=today
    ).order_by('date_debut')
    
    context = {
        'form': form,
        'fermetures': fermetures,
        'boulangerie': boulangerie,
        'today': today,
    }
    return render(request, 'main/gerant/fermetures_multi_jours.html', context)

# Vue pour supprimer une fermeture multi-jours
@login_required(login_url='connexion_pro')
def supprimer_fermeture_multi_jours(request, pk):
    fermeture = get_object_or_404(FermetureMultiJours, pk=pk)
    fermeture.delete()
    messages.success(request, 'La période de fermeture a été supprimée.')
    return redirect('fermetures_multi_jours')

# API pour récupérer les créneaux disponibles
def api_creneaux_disponibles(request):
    """API pour récupérer les créneaux disponibles pour une date donnée"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date requise'}, status=400)
    
    try:
        date_collecte = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide'}, status=400)
    
    # Vérifier si c'est une date passée
    if date_collecte < timezone.now().date():
        return JsonResponse({'creneaux': []})
    
    # Récupérer le jour de la semaine (0 = Lundi, 6 = Dimanche)
    jour_semaine = date_collecte.weekday()
    
    # Vérifier les fermetures multi-jours
    fermeture_multi = FermetureMultiJours.objects.filter(
        date_debut__lte=date_collecte,
        date_fin__gte=date_collecte
    ).exists()
    
    if fermeture_multi:
        return JsonResponse({'creneaux': [], 'ferme': True, 'raison': 'Fermeture exceptionnelle'})
    
    # Vérifier les fermetures spécifiques
    fermeture_specifique = FermetureSpecifique.objects.filter(date=date_collecte).first()
    
    # Récupérer les horaires du jour
    horaire = HoraireHebdomadaire.objects.get(jour=jour_semaine)
    
    # Récupérer la fréquence
    frequence = FrequenceCollecte.objects.first()
    intervalle = frequence.intervalle if frequence else 30
    
    creneaux = []
    now = timezone.now()
    
    # Générer les créneaux du matin
    if horaire.est_ouvert_matin() and (not fermeture_specifique or fermeture_specifique.type_fermeture == 'soir'):
        heure_debut = datetime.combine(date_collecte, horaire.ouverture_matin)
        heure_fin = datetime.combine(date_collecte, horaire.fermeture_matin)
        
        while heure_debut < heure_fin:
            # Ne pas afficher les créneaux passés si c'est aujourd'hui
            if date_collecte == now.date():
                # heure_actuelle = timezone.localtime(now).time()
                heure_limite = (timezone.localtime(now) + timedelta(minutes=30)).time()               
                if heure_debut.time() <= heure_limite:
                    heure_debut += timedelta(minutes=intervalle)
                    continue
                
            creneaux.append({
                'heure': heure_debut.strftime('%H:%M'),
                'periode': 'matin'
            })
            heure_debut += timedelta(minutes=intervalle)
    
    # Générer les créneaux du soir
    if horaire.est_ouvert_soir() and (not fermeture_specifique or fermeture_specifique.type_fermeture == 'matin'):
        heure_debut = datetime.combine(date_collecte, horaire.ouverture_soir)
        heure_fin = datetime.combine(date_collecte, horaire.fermeture_soir)
        
        while heure_debut < heure_fin:
            if date_collecte == now.date():
                # heure_actuelle = timezone.localtime(now).time()
                heure_limite = (timezone.localtime(now) + timedelta(minutes=30)).time()               
                if heure_debut.time() <= heure_limite:
                    heure_debut += timedelta(minutes=intervalle)
                    continue
                
            creneaux.append({
                'heure': heure_debut.strftime('%H:%M'),
                'periode': 'soir'
            })
            heure_debut += timedelta(minutes=intervalle)
    
    return JsonResponse({
        'creneaux': creneaux,
        'ferme': len(creneaux) == 0,
        'raison': fermeture_specifique.motif if fermeture_specifique else None
    })

# Ajoutez cette vue à la fin du fichier
stripe.api_key = settings.STRIPE_SECRET_KEY

# =================== debut ajout =============

def creer_session_paiement(request):
    """Créer une session de paiement Stripe"""
    if request.method == 'POST':
        try:
            # Vérifier que l'utilisateur est connecté
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Vous devez être connecté pour commander'}, status=401)
            
            data = json.loads(request.body)
            panier = data.get('panier', [])
            info_collecte = data.get('infoCollecte', {})
            
            # Calculer les totaux
            sous_total = sum(Decimal(str(item['prix'])) * item['quantite'] for item in panier)
            frais_service = Decimal('0.00')
            total = sous_total + frais_service
            
            # Créer la commande en base de données avec statut en_attente
            with transaction.atomic():
                commande = Commande.objects.create(
                    client=request.user,
                    date_collecte=info_collecte.get('date'),
                    heure_collecte=info_collecte.get('heure'),
                    sous_total=sous_total,
                    frais_service=frais_service,
                    total=total,
                    statut='en_attente'
                )
                
                # Créer les lignes de commande
                for item in panier:
                    LigneCommande.objects.create(
                        commande=commande,
                        produit_id=item.get('id'),
                        nom_produit=item['nom'],
                        prix_unitaire=Decimal(str(item['prix'])),
                        categorie=item.get('categorie', ''),
                        quantite=item['quantite']
                    )
            
            # Créer les line items pour Stripe
            line_items = []
            for item in panier:
                line_items.append({
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': item['nom'],
                            'description': item.get('categorie', ''),
                        },
                        'unit_amount': int(float(item['prix']) * 100),
                    },
                    'quantity': item['quantite'],
                })
            
            # Créer la session Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                # success_url=request.build_absolute_uri(f'/paiement/succes/?session_id={{CHECKOUT_SESSION_ID}}&commande_id={commande.id}'),
                success_url=request.build_absolute_uri(f'/paiement/succes/?commande_id={commande.id}'),
                cancel_url=request.build_absolute_uri('/panier/'),
                metadata={
                    'commande_id': str(commande.id),
                    'date_collecte': info_collecte.get('date', ''),
                    'heure_collecte': info_collecte.get('heure', ''),
                }
            )
            
            # Sauvegarder l'ID de session Stripe
            commande.stripe_session_id = session.id
            commande.save()
            
            return JsonResponse({'sessionId': session.id})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Nouvelle vue paiement_succes améliorée

# debut ajout paiement_succes

@login_required
def paiement_succes(request):
    """
    Page de succès après paiement.
    On ne récupère plus session_id depuis l’URL, on utilise celui stocké
    en base via commande.stripe_session_id.
    """
    print("\n=== DEBUT paiement_succes ===")
    commande_id = request.GET.get('commande_id')
    print(f"commande_id: {commande_id}")
    print(f"user authenticated: {request.user.is_authenticated}")

    if not commande_id:
        print("ERREUR: Paramètre commande_id manquant")
        messages.error(request, 'Paramètre de paiement manquant.')
        return redirect('commander')

    # Charger la commande
    try:
        commande = Commande.objects.get(id=commande_id)
    except Commande.DoesNotExist:
        print("ERREUR: Commande introuvable")
        messages.error(request, 'Commande introuvable.')
        return redirect('panier')

    session_id = commande.stripe_session_id
    if not session_id:
        print("ERREUR: stripe_session_id manquant")
        messages.error(request, 'Impossible de retrouver la session de paiement.')
        return redirect('panier')

    try:
        print(f"Récupération session Stripe: {session_id}")
        session = stripe.checkout.Session.retrieve(session_id)
        print(f"payment_status: {session.payment_status}")

        if session.payment_status == 'paid':
            # Mettre à jour le statut si encore en attente
            if commande.statut == 'en_attente':
                commande.statut = 'payee'
                commande.date_paiement = timezone.now()
                commande.stripe_payment_intent = session.payment_intent
                commande.save()
                print("Commande mise à jour : payée")

                # Notification gérant
                NotificationCommande.objects.create(commande=commande)
                # Envoi d’email de confirmation
                try:
                    envoyer_email_confirmation_commande(commande)
                    print("Email de confirmation envoyé")
                except Exception as e:
                    print(f"Erreur email: {e}")

            messages.success(request, f'Commande n°{commande.numero_commande} confirmée !')
            return render(
                request,
                'main/client/commande_confirmee.html',
                {
                    'commande': commande,
                    'boulangerie': get_boulangerie()
                }
            )

        # Si le paiement n'est pas finalisé
        print(f"ERREUR: Paiement non complété, statut: {session.payment_status}")
        messages.error(request, 'Le paiement n\'a pas été complété.')
        return redirect('panier')

    except stripe.error.StripeError as e:
        print(f"ERREUR Stripe: {e}")
        messages.error(request, 'Erreur lors de la vérification du paiement.')
        return redirect('panier')

    except Exception as e:
        print(f"ERREUR générale: {e}")
        traceback.print_exc()
        messages.error(request, 'Une erreur est survenue.')
        return redirect('panier')

# fin ajout paiement_succes

# Fonction pour générer la facture PDF
def generer_facture_pdf(commande):
    """Génère une facture PDF pour une commande"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8B4513'),
        spaceAfter=30,
        alignment=1  # Centré
    )
    
    # En-tête
    boulangerie = get_boulangerie()
    elements.append(Paragraph(f"FACTURE - {boulangerie.nom}", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Infos boulangerie et client
    info_data = [
        ['', ''],
        [f'<b>{boulangerie.nom}</b>', f'<b>Client :</b>'],
        [f'{boulangerie.adresse}', f'{commande.client.get_full_name()}'],
        [f'{boulangerie.code} {boulangerie.ville}', f'{commande.client.email}'],
        [f'Tél: {boulangerie.telephone}', ''],
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Infos commande
    commande_info = [
        [f'<b>N° Commande :</b> {commande.numero_commande}'],
        [f'<b>Date :</b> {commande.date_commande.strftime("%d/%m/%Y %H:%M")}'],
        [f'<b>Retrait prévu :</b> {commande.date_collecte.strftime("%d/%m/%Y")} à {commande.heure_collecte.strftime("%H:%M")}'],
    ]
    
    for info in commande_info:
        elements.append(Paragraph(info[0], styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tableau des produits
    data = [['Produit', 'Prix unitaire', 'Quantité', 'Total']]
    
    for ligne in commande.lignes.all():
        data.append([
            ligne.nom_produit,
            f'{ligne.prix_unitaire:.2f} €',
            str(ligne.quantite),
            f'{ligne.sous_total:.2f} €'
        ])
    
    # Totaux
    data.append(['', '', '', ''])
    data.append(['', '', 'Sous-total :', f'{commande.sous_total:.2f} €'])
    data.append(['', '', 'Frais de service :', f'{commande.frais_service:.2f} €'])
    data.append(['', '', '<b>TOTAL :</b>', f'<b>{commande.total:.2f} €</b>'])
    
    # Créer le tableau
    table = Table(data, colWidths=[3*inch, 1.5*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d2691e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -5), 1, colors.grey),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        # Totaux
        ('FONTNAME', (-2, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2, -1), (-1, -1), 12),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer = Paragraph(
        f"<i>Merci pour votre commande chez {boulangerie.nom} !</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, fontSize=10)
    )
    elements.append(footer)
    
    # Générer le PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

# Fonction pour envoyer l'email de confirmation
def envoyer_email_confirmation_commande(commande):
    """Envoie un email de confirmation avec la facture en pièce jointe"""
    boulangerie = get_boulangerie()
    
    # Générer le contenu HTML de l'email
    context = {
        'commande': commande,
        'boulangerie': boulangerie,
        'lignes': commande.lignes.all(),
    }
    
    html_content = render_to_string('main/emails/confirmation_commande.html', context)
    text_content = f"""
    Bonjour {commande.client.get_full_name()},

    Votre commande n°{commande.numero_commande} a bien été confirmée !
    
    Montant total : {commande.total} €
    Date de retrait : {commande.date_collecte.strftime('%d/%m/%Y')} à {commande.heure_collecte.strftime('%H:%M')}
    
    Vous trouverez votre facture en pièce jointe.
    
    Merci pour votre confiance !
    L'équipe {boulangerie.nom}
    """
    
    # Créer l'email
    email = EmailMultiAlternatives(
        subject=f'Confirmation de commande n°{commande.numero_commande} - {boulangerie.nom}',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
        to=[commande.client.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    # Générer et attacher la facture PDF
    pdf = generer_facture_pdf(commande)
    email.attach(
        f'facture_{commande.numero_commande}.pdf',
        pdf,
        'application/pdf'
    )
    
    # Envoyer l'email
    try:
        email.send()
        commande.email_confirmation_envoye = True
        commande.facture_envoyee = True
        commande.save()
    except Exception as e:
        print(f"Erreur envoi email commande {commande.numero_commande}: {str(e)}")

# Vue pour voir les commandes du client
@login_required
def mes_commandes(request):
    """
    Affiche la liste des commandes du client connecté
    et compte combien sont au statut 'prete'.
    """
    # Récupère toutes les commandes du client, hors statut 'en_attente'
    commandes = (
        Commande.objects
        .filter(client=request.user)
        .exclude(statut='en_attente')
        .order_by('-date_commande')
    )

    # Pré-calcul du nombre de commandes déjà prêtes
    pretes_count = commandes.filter(statut='prete').count()

    context = {
        'commandes': commandes,
        'pretes_count': pretes_count,
        'boulangerie': get_boulangerie(),
    }
    return render(request, 'main/client/mes_commandes.html', context)

# Vue détail d'une commande
@login_required
def detail_commande(request, numero_commande):
    """Affiche le détail d'une commande"""
    commande = get_object_or_404(
        Commande,
        numero_commande=numero_commande,
        client=request.user
    )
    
    context = {
        'commande': commande,
        'boulangerie': get_boulangerie(),
    }
    
    return render(request, 'main/client/detail_commande.html', context)

# Vue pour télécharger la facture
@login_required
def telecharger_facture(request, numero_commande):
    """Télécharge la facture PDF d'une commande"""
    commande = get_object_or_404(
        Commande,
        numero_commande=numero_commande,
        client=request.user
    )
    
    pdf = generer_facture_pdf(commande)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{commande.numero_commande}.pdf"'
    
    return response

# API pour vider le panier après paiement
def vider_panier_api(request):
    """API pour vider le panier côté client"""
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Panier vidé'})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@login_required
@require_http_methods(["GET"])
def api_commande_details(request, commande_id):
    """API pour obtenir les détails d'une commande (modal gérant)"""
    try:
        commande = Commande.objects.get(id=commande_id)
        
        # Vérifier les permissions
        if not (request.user == commande.client or request.user.groups.filter(name='Gerants').exists()):
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        
        # Générer le HTML
        html = render_to_string('main/partials/commande_details_modal.html', {
            'commande': commande,
            'lignes': commande.lignes.all(),
        })
        
        return JsonResponse({'html': html})
        
    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)

@login_required
@require_http_methods(["GET"])
def api_stats_commandes(request):
    """API pour obtenir les statistiques des commandes (dashboard)"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    
    # Période sélectionnée
    periode = request.GET.get('periode', 'jour')
    today = timezone.now().date()
    
    if periode == 'jour':
        start_date = today
        end_date = today
    elif periode == 'semaine':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif periode == 'mois':
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    # Récupérer les commandes de la période
    commandes = Commande.objects.filter(
        date_commande__date__gte=start_date,
        date_commande__date__lte=end_date
    ).exclude(statut__in=['en_attente', 'annulee'])
    
    # Calculer les stats
    stats = {
        'total_commandes': commandes.count(),
        'ca_total': commandes.aggregate(total=Sum('total'))['total'] or 0,
        'ticket_moyen': 0,
        'commandes_par_statut': {},
        'evolution': [],
        'top_produits': []
    }
    
    # Ticket moyen
    if stats['total_commandes'] > 0:
        stats['ticket_moyen'] = stats['ca_total'] / stats['total_commandes']
    
    # Commandes par statut
    for statut, label in Commande.STATUT_CHOICES:
        count = commandes.filter(statut=statut).count()
        if count > 0:
            stats['commandes_par_statut'][label] = count
    
    # Évolution sur la période
    if periode == 'jour':
        # Par heure
        for hour in range(8, 20):  # 8h à 19h
            count = commandes.filter(
                date_commande__hour=hour
            ).count()
            stats['evolution'].append({
                'label': f'{hour}h',
                'value': count
            })
    elif periode == 'semaine':
        # Par jour
        for i in range(7):
            date = start_date + timedelta(days=i)
            count = commandes.filter(date_commande__date=date).count()
            stats['evolution'].append({
                'label': date.strftime('%a'),
                'value': count
            })
    
    # Top produits
    from django.db.models import Count
    top_produits = LigneCommande.objects.filter(
        commande__in=commandes
    ).values('nom_produit').annotate(
        total=Sum('quantite')
    ).order_by('-total')[:5]
    
    stats['top_produits'] = list(top_produits)
    
    return JsonResponse(stats)

@login_required
@require_http_methods(["POST"])
def api_marquer_notifications_vues(request):
    """Marque toutes les notifications comme vues"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    NotificationCommande.objects.filter(vue=False).update(vue=True)
    
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["GET"])
def api_export_commandes(request):
    """Export des commandes en CSV"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    import csv
    from django.http import HttpResponse
    
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Récupérer les commandes
    commandes = Commande.objects.all()
    
    if date_debut:
        commandes = commandes.filter(date_commande__date__gte=date_debut)
    if date_fin:
        commandes = commandes.filter(date_commande__date__lte=date_fin)
    
    # Créer la réponse CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="commandes.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'N° Commande',
        'Date',
        'Client',
        'Email',
        'Téléphone',
        'Date collecte',
        'Heure collecte',
        'Statut',
        'Total',
        'Produits'
    ])
    
    for commande in commandes:
        produits = ', '.join([
            f"{ligne.quantite}x {ligne.nom_produit}"
            for ligne in commande.lignes.all()
        ])
        
        writer.writerow([
            commande.numero_commande,
            commande.date_commande.strftime('%d/%m/%Y %H:%M'),
            commande.client.get_full_name(),
            commande.client.email,
            getattr(commande.client, 'telephone', ''),
            commande.date_collecte.strftime('%d/%m/%Y'),
            commande.heure_collecte.strftime('%H:%M'),
            commande.get_statut_display(),
            f"{commande.total}€",
            produits
        ])
    
    return response

@login_required
@require_http_methods(["GET"])
def api_commandes_en_cours(request):
    """API pour obtenir le nombre de commandes en cours (pour badge menu)"""
    if request.user.groups.filter(name='Gerants').exists():
        # Pour les gérants : commandes non récupérées du jour
        count = Commande.objects.filter(
            date_collecte=timezone.now().date(),
            statut__in=['payee', 'en_preparation', 'prete']
        ).count()
    else:
        # Pour les clients : leurs commandes prêtes
        count = Commande.objects.filter(
            client=request.user,
            statut='prete'
        ).count()
    
    return JsonResponse({'count': count})

@login_required
@require_http_methods(["POST"])
def api_imprimer_commande(request, commande_id):
    """Génère un bon de préparation pour impression"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        commande = Commande.objects.get(id=commande_id)
        
        # Générer le HTML pour impression
        html = render_to_string('main/print/bon_preparation.html', {
            'commande': commande,
            'lignes': commande.lignes.all(),
            'boulangerie': get_boulangerie(),
        })
        
        return JsonResponse({'html': html})
        
    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)
    
@login_required
def annuler_commande(request, numero_commande):
    """Annuler une commande (si elle n'est pas encore préparée)"""
    if request.method == 'POST':
        commande = get_object_or_404(
            Commande,
            numero_commande=numero_commande,
            client=request.user
        )
        
        # Vérifier que la commande peut être annulée
        if commande.statut in ['payee', 'en_preparation']:
            commande.statut = 'annulee'
            commande.save()
            
            # Envoyer un email de confirmation d'annulation
            envoyer_email_annulation_commande(commande)
            
            messages.success(request, 'Votre commande a été annulée avec succès.')
        else:
            messages.error(request, 'Cette commande ne peut plus être annulée.')
        
        return redirect('detail_commande', numero_commande=numero_commande)
    
    return redirect('mes_commandes')

def envoyer_email_annulation_commande(commande):
    """Envoie un email de confirmation d'annulation"""
    boulangerie = get_boulangerie()
    
    subject = f'Annulation de commande n°{commande.numero_commande} - {boulangerie.nom}'
    
    text_content = f"""
    Bonjour {commande.client.get_full_name()},

    Votre commande n°{commande.numero_commande} a été annulée à votre demande.
    
    Montant remboursé : {commande.total} €
    
    Le remboursement sera effectué sur votre moyen de paiement dans un délai de 5 à 10 jours ouvrés.
    
    Cordialement,
    L'équipe {boulangerie.nom}
    """
    
    html_content = render_to_string('main/emails/annulation_commande.html', {
        'commande': commande,
        'boulangerie': boulangerie,
    })
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
        to=[commande.client.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
    except Exception as e:
        print(f"Erreur envoi email annulation: {str(e)}")

@csrf_exempt
def stripe_webhook(request):
    """Webhook Stripe pour gérer les événements de paiement"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # À configurer dans settings.py
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Gérer les différents types d'événements
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Récupérer la commande
        commande_id = session['metadata'].get('commande_id')
        if commande_id:
            try:
                commande = Commande.objects.get(id=commande_id)
                
                # Confirmer le paiement
                if commande.statut == 'en_attente':
                    commande.statut = 'payee'
                    commande.date_paiement = timezone.now()
                    commande.stripe_payment_intent = session['payment_intent']
                    commande.save()
                    
                    # Créer une notification
                    NotificationCommande.objects.create(commande=commande)
                    
                    # Envoyer l'email de confirmation
                    envoyer_email_confirmation_commande(commande)
                    
            except Commande.DoesNotExist:
                pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        # Gérer l'échec du paiement
        payment_intent = event['data']['object']
        # Log l'erreur ou notifier l'administrateur
        
    return HttpResponse(status=200)

# Vue pour le tableau de bord gérant - voir les nouvelles commandes
@login_required(login_url='connexion_pro')
def dashboard_gerant_commandes(request):
    """
    Dashboard gérant : affiche les commandes du jour
    Accessible aux utilisateurs :
      - marqués staff, OU
      - dont le username est 'randr', OU
      - appartenant au groupe 'Gerants'
    """
    user = request.user
    # Test simple et large
    is_gerant = user.is_staff or user.username == 'randr' or user.groups.filter(name='Gerants').exists()
    if not is_gerant:
        return redirect('accueil')

    today = timezone.now().date()
    commandes_jour = (
        Commande.objects
        .filter(date_collecte=today)
        .exclude(statut__in=['annulee', 'en_attente'])
        .order_by('heure_collecte')
    )

    notifications = NotificationCommande.objects.filter(vue=False)

    stats = {
        'total_commandes': commandes_jour.count(),
        'commandes_payees':  commandes_jour.filter(statut='payee').count(),
        'commandes_preparation': commandes_jour.filter(statut='en_preparation').count(),
        'commandes_pretes': commandes_jour.filter(statut='prete').count(),
        'commandes_recuperees': commandes_jour.filter(statut='recuperee').count(),
        'ca_jour': commandes_jour.aggregate(total=Sum('total'))['total'] or 0
    }

    context = {
        'commandes_jour': commandes_jour,
        'notifications': notifications,
        'stats': stats,
        'boulangerie': get_boulangerie(),
    }
    return render(request, 'main/gerant/dashboard_commandes.html', context)

# API pour changer le statut d'une commande (gérant)
@login_required
def changer_statut_commande(request, commande_id):
    """Change le statut d'une commande (réservé aux gérants)"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nouveau_statut = data.get('statut')
            
            commande = Commande.objects.get(id=commande_id)
            ancien_statut = commande.statut
            
            # Mettre à jour le statut et les timestamps
            commande.statut = nouveau_statut
            
            if nouveau_statut == 'en_preparation':
                commande.date_preparation = timezone.now()
            elif nouveau_statut == 'prete':
                commande.date_prete = timezone.now()
                # Envoyer une notification au client
                envoyer_notification_commande_prete(commande)
            elif nouveau_statut == 'recuperee':
                commande.date_recuperation = timezone.now()
            
            commande.save()
            
            # Marquer les notifications comme vues
            NotificationCommande.objects.filter(commande=commande).update(vue=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Statut mis à jour : {commande.get_statut_display()}'
            })
            
        except Commande.DoesNotExist:
            return JsonResponse({'error': 'Commande introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def envoyer_notification_commande_prete(commande):
    """Envoie une notification quand la commande est prête"""
    boulangerie = get_boulangerie()
    
    subject = f'Votre commande est prête ! - {boulangerie.nom}'
    
    text_content = f"""
    Bonjour {commande.client.get_full_name()},

    Bonne nouvelle ! Votre commande n°{commande.numero_commande} est prête.
    
    Vous pouvez venir la récupérer à partir de maintenant.
    
    Rappel de votre créneau : {commande.heure_collecte.strftime('%H:%M')}
    
    À tout de suite !
    L'équipe {boulangerie.nom}
    """
    
    try:
        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
            [commande.client.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi notification commande prête: {str(e)}")

# ================== fin ajout ==========================

def connexion(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('commander')
    
    boulangerie = get_boulangerie()
    return render(request, 'main/auth/connexion.html', {'boulangerie': boulangerie})

def inscription(request):
    """Page d'inscription"""
    if request.user.is_authenticated:
        return redirect('commander')
    
    boulangerie = get_boulangerie()
    return render(request, 'main/auth/inscription.html', {'boulangerie': boulangerie})

# connexion_pro mis à jour

def connexion_pro(request):
    """Connexion pour gérants et personnel uniquement via email + code 6 chiffres"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Vérifier que le mot de passe est un code à 6 chiffres
        if not (password.isdigit() and len(password) == 6):
            return render(request, 'main/auth/connexion_pro.html', {
                'error': 'Le mot de passe doit contenir exactement 6 chiffres.'
            })

        # Récupérer l’utilisateur par email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            user_obj = None

        # Authentification avec le username interne
        if user_obj:
            user = authenticate(request,
                                username=user_obj.username,
                                password=password)
        else:
            user = None

        if user:
            # Vérifier que l’utilisateur est gérant, personnel ou super-user
            if (user.is_staff or
                user.username == 'randr' or
                user.groups.filter(name__in=['Gerants', 'Personnel']).exists() or
                user.is_superuser):
                
                login(request, user)

                # Redirection selon le rôle
                if user.is_superuser:
                    return redirect('admin:index')
                elif user.groups.filter(name='Gerants').exists():
                    return redirect('dashboard_gerant')
                elif user.groups.filter(name='Personnel').exists():
                    return redirect('dashboard_personnel')  # MODIFIÉ ICI
                else:
                    return redirect('dashboard_gerant')

            # Accès refusé si pas dans les bons groupes
            return render(request, 'main/auth/connexion_pro.html', {
                'error': 'Accès refusé. Cette page est réservée au personnel.'
            })
  
        # Identifiants invalides
        return render(request, 'main/auth/connexion_pro.html', {
            'error': 'Email ou code incorrect.'
        })

    # Méthode GET
    return render(request, 'main/auth/connexion_pro.html')

def ajax_connexion(request):
    """Traitement AJAX de la connexion avec redirection selon le groupe"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user:
                login(request, user)
                
                # Déterminer la redirection selon le groupe
                if user.is_superuser:
                    # Superuser - vers dashboard admin Django
                    redirect_url = '/admin/'
                elif user.groups.filter(name='Gerants').exists():
                    # Gérant - vers dashboard gérant
                    redirect_url = '/gerant/'
                elif user.groups.filter(name='Personnel').exists():
                    # Personnel - vers dashboard personnel (MODIFIÉ ICI)
                    redirect_url = '/personnel/'
                else:
                    # Client par défaut - vers page commander
                    redirect_url = '/commander/'
                
                return JsonResponse({
                    'success': True, 
                    'redirect': redirect_url,
                    'group': user.profile.get_user_group() if hasattr(user, 'profile') else 'Client'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Email ou mot de passe incorrect'})
                
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Email ou mot de passe incorrect'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def ajax_inscription(request):
    """Traitement AJAX de l'inscription avec téléphone et assignation au groupe Clients"""
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['prenom'],
                last_name=form.cleaned_data['nom']
            )
            
            # Ajouter le téléphone au profil
            if hasattr(user, 'profile'):
                user.profile.telephone = form.cleaned_data.get('telephone', '')
                user.profile.save()
            
            # Assigner au groupe Clients
            try:
                groupe_clients = Group.objects.get(name='Clients')
                user.groups.add(groupe_clients)
            except Group.DoesNotExist:
                print("Le groupe 'Clients' n'existe pas. Exécutez la commande init_groups.")
            
            # Générer et envoyer le code
            code = CodeVerification.objects.create(
                user=user,
                code=CodeVerification.generate_code()
            )
            
            # Envoyer l'email
            send_mail(
                'Code de vérification - Pain Doré',
                f'Votre code de vérification est : {code.code}',
                'noreply@paindore.com',
                [user.email],
                fail_silently=False,
            )
            
            # Stocker l'ID utilisateur en session
            request.session['user_to_verify'] = user.id
            
            return JsonResponse({'success': True, 'redirect': '/verification-code/'})
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            return JsonResponse({'success': False, 'errors': errors})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def verification_code(request):
    """Page de vérification du code"""
    user_id = request.session.get('user_to_verify')
    if not user_id:
        return redirect('connexion')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            user = User.objects.get(id=user_id)
            verification = CodeVerification.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if verification.is_valid():
                verification.is_used = True
                verification.save()
                login(request, user)
                del request.session['user_to_verify']
                return JsonResponse({'success': True, 'redirect': '/commander/'})
            else:
                return JsonResponse({'success': False, 'error': 'Code invalide ou expiré'})
        except (User.DoesNotExist, CodeVerification.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Code invalide'})
    
    boulangerie = get_boulangerie()
    return render(request, 'main/auth/verification_code.html', {'boulangerie': boulangerie})

def renvoyer_code(request):
    """Renvoyer un nouveau code"""
    user_id = request.session.get('user_to_verify')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            # Invalider les anciens codes
            CodeVerification.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Créer un nouveau code
            code = CodeVerification.objects.create(
                user=user,
                code=CodeVerification.generate_code()
            )
            
            # Envoyer l'email
            send_mail(
                'Nouveau code de vérification - Pain Doré',
                f'Votre nouveau code de vérification est : {code.code}',
                'noreply@paindore.com',
                [user.email],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True, 'message': 'Code renvoyé avec succès'})
        except User.DoesNotExist:
            pass
    
    return JsonResponse({'success': False, 'error': 'Erreur lors de l\'envoi'})

def deconnexion(request):
    """Déconnexion"""
    logout(request)
    return redirect('accueil')

# mot de passe oublié et réinitialisation mdp

def mot_de_passe_oublie(request):
    """Page et traitement du mot de passe oublié"""
    if request.user.is_authenticated:
        return redirect('accueil')
    
    boulangerie = get_boulangerie()
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Log pour déboguer
        print(f"Email reçu : {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"Utilisateur trouvé : {user.username}")
            
            # Invalider les anciens tokens
            TokenReinitialisationMotDePasse.objects.filter(
                user=user, 
                is_used=False
            ).update(is_used=True)
            
            # Créer un nouveau token
            token = TokenReinitialisationMotDePasse.objects.create(
                user=user,
                token=TokenReinitialisationMotDePasse.generate_token()
            )
            
            # Construire le lien de réinitialisation
            reset_link = request.build_absolute_uri(
                reverse('reinitialiser_mot_de_passe', kwargs={'token': token.token})
            )
            
            print(f"Lien de réinitialisation : {reset_link}")
            
            # Pour tester sans envoyer d'email, commentez le bloc send_mail
            # et décommentez cette ligne :
            # print(f"TEST MODE - Lien de réinitialisation : {reset_link}")
            
            try:
                # Envoyer l'email
                sujet = "Réinitialisation de votre mot de passe - Pain Doré"
                
                # Version texte simple
                message_text = f"""Bonjour {user.first_name or 'Client'},

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur ce lien pour créer un nouveau mot de passe :
{reset_link}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.

Cordialement,
L'équipe {boulangerie.nom}"""

                # Version HTML (si le template existe)
                try:
                    message_html = render_to_string('main/emails/reset_password_email.html', {
                        'user': user,
                        'reset_link': reset_link,
                        'boulangerie': boulangerie,
                    })
                except:
                    message_html = None
                    print("Template email HTML non trouvé")
                
                send_mail(
                    sujet,
                    message_text,
                    settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
                    [user.email],
                    html_message=message_html,
                    fail_silently=False,
                )
                
                print(f"Email envoyé à {user.email}")
                
            except Exception as e:
                print(f"Erreur envoi email : {str(e)}")
                # En cas d'erreur email, on retourne quand même success
                # mais on log l'erreur
            
            return JsonResponse({
                'success': True,
                'message': 'Email envoyé avec succès'
            })
            
        except User.DoesNotExist:
            print(f"Utilisateur non trouvé pour l'email : {email}")
            # Pour des raisons de sécurité, on retourne toujours success
            return JsonResponse({
                'success': True,
                'message': 'Email envoyé avec succès'
            })
        except Exception as e:
            print(f"Erreur générale : {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Une erreur est survenue : {str(e)}'
            })
    
    return render(request, 'main/auth/mot_de_passe_oublie.html', {
        'boulangerie': boulangerie
    })

def reinitialiser_mot_de_passe(request, token):
    """Page de réinitialisation du mot de passe"""
    boulangerie = get_boulangerie()
    
    # Vérifier si le token existe et est valide
    try:
        token_obj = TokenReinitialisationMotDePasse.objects.get(token=token)
        
        if not token_obj.is_valid():
            messages.error(request, 'Ce lien de réinitialisation a expiré ou a déjà été utilisé.')
            return redirect('mot_de_passe_oublie')
            
    except TokenReinitialisationMotDePasse.DoesNotExist:
        messages.error(request, 'Lien de réinitialisation invalide.')
        return redirect('mot_de_passe_oublie')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('password-confirm', '')
        
        # Validation - 6 chiffres exactement
        if len(password) != 6:
            return JsonResponse({
                'success': False,
                'error': 'Le mot de passe doit contenir exactement 6 chiffres'
            })
        
        if not password.isdigit():
            return JsonResponse({
                'success': False,
                'error': 'Le mot de passe doit contenir uniquement des chiffres'
            })
        
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'Les mots de passe ne correspondent pas'
            })
        
        try:
            # Mettre à jour le mot de passe
            user = token_obj.user
            user.password = make_password(password)
            user.save()
            
            # Marquer le token comme utilisé
            token_obj.is_used = True
            token_obj.save()
            
            # Envoyer un email de confirmation
            send_mail(
                'Mot de passe modifié - Pain Doré',
                f'Bonjour {user.first_name},\n\nVotre mot de passe a été modifié avec succès.',
                'noreply@paindore.com',
                [user.email],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Mot de passe réinitialisé avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Une erreur est survenue. Veuillez réessayer.'
            })
    
    return render(request, 'main/auth/reinitialiser_mot_de_passe.html', {
        'boulangerie': boulangerie,
        'token': token
    })

# statut - code de recuperation 

def generer_code_pin():
    """Génère un code PIN à 4 chiffres"""
    return str(random.randint(1000, 9999))

@csrf_exempt
@login_required
def changer_statut_commande(request, commande_id):
    """Change le statut d'une commande (réservé aux gérants)"""
    if not request.user.groups.filter(name='Gerants').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nouveau_statut = data.get('statut')
            
            commande = Commande.objects.get(id=commande_id)
            ancien_statut = commande.statut
            
            # Mettre à jour le statut et les timestamps
            commande.statut = nouveau_statut
            
            if nouveau_statut == 'en_preparation':
                commande.date_preparation = timezone.now()
                
            elif nouveau_statut == 'prete':
                commande.date_prete = timezone.now()
                
                # Générer et sauvegarder le code PIN
                code_pin = generer_code_pin()
                commande.code_recuperation = code_pin
                
                # Préparer le contexte pour l'email
                boulangerie = get_boulangerie()
                context = {
                    'commande': commande,
                    'boulangerie': boulangerie,
                }
                
                # Générer le contenu HTML
                html_content = render_to_string('main/emails/commande_prete_code.html', context)
                
                # Version texte simple
                text_content = f"""
Bonjour {commande.client.get_full_name()},

Bonne nouvelle ! Votre commande #{commande.numero_commande} est prête à être récupérée.

Votre code de récupération : {code_pin}

Présentez ce code à la boulangerie pour récupérer votre commande.

Heure de retrait prévue : {commande.heure_collecte.strftime('%H:%M')}

Merci de votre confiance !

{boulangerie.nom}
{boulangerie.adresse}
{boulangerie.telephone}
"""
                
                # Créer l'email multi-format
                email = EmailMultiAlternatives(
                    subject=f'Votre commande #{commande.numero_commande} est prête !',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
                    to=[commande.client.email]
                )
                email.attach_alternative(html_content, "text/html")
                
                try:
                    email.send()
                    print(f"Email avec code PIN envoyé pour commande {commande.numero_commande}")
                except Exception as e:
                    print(f"Erreur envoi email code PIN: {e}")
                    # On continue même si l'email échoue
                    
            elif nouveau_statut == 'recuperee':
                commande.date_recuperation = timezone.now()
            
            # Sauvegarder les modifications
            commande.save()
            
            # Marquer les notifications comme vues
            NotificationCommande.objects.filter(commande=commande).update(vue=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Statut mis à jour : {commande.get_statut_display()}'
            })
            
        except Commande.DoesNotExist:
            return JsonResponse({'error': 'Commande introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def valider_code_recuperation(request, commande_id):
    """Valide le code PIN et marque la commande comme récupérée"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_saisi = data.get('code')
            
            commande = get_object_or_404(Commande, id=commande_id, statut='prete')
            
            # Vérifier le code
            if commande.code_recuperation == code_saisi:
                # Mettre à jour le statut
                commande.statut = 'recuperee'
                commande.date_recuperation = timezone.now()
                commande.save()
                
                # Envoyer l'email de confirmation
                subject = f'Commande #{commande.numero_commande} récupérée'
                message = f"""
                Bonjour {commande.client.get_full_name()},
                
                Nous confirmons que vous avez récupéré votre commande #{commande.numero_commande}.
                
                Merci de votre visite et à bientôt !
                
                {settings.BAKERY_NAME}
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [commande.client.email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Commande récupérée avec succès'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Code incorrect'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

def api_commande_details(request, commande_id):
    """Retourne les détails d'une commande pour le modal"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    html = f"""
    <div class="row">
        <div class="col-md-6">
            <h6>Client</h6>
            <p>{commande.client.get_full_name()}<br>
            <small class="text-muted">{commande.client.email}</small></p>
        </div>
        <div class="col-md-6">
            <h6>Informations de retrait</h6>
            <p>Date : {commande.date_collecte.strftime('%d/%m/%Y')}<br>
            Heure : {commande.heure_collecte.strftime('%H:%M')}</p>
        </div>
    </div>
    
    <hr>
    
    <h6>Produits commandés</h6>
    <table class="table table-sm">
        <thead>
            <tr>
                <th>Produit</th>
                <th class="text-center">Qté</th>
                <th class="text-end">Prix unit.</th>
                <th class="text-end">Total</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for ligne in commande.lignes.all():
        html += f"""
            <tr>
                <td>{ligne.nom_produit}</td>
                <td class="text-center">{ligne.quantite}</td>
                <td class="text-end">{ligne.prix_unitaire}€</td>
                <td class="text-end">{ligne.sous_total}€</td>
            </tr>
        """
    
    html += f"""
        </tbody>
        <tfoot>
            <tr>
                <td colspan="3" class="text-end"><strong>Total :</strong></td>
                <td class="text-end"><strong>{commande.total}€</strong></td>
            </tr>
        </tfoot>
    </table>
    """
    
    return JsonResponse({'html': html})
    
# mise à jour en temps reel statut

def api_commande_statut(request, commande_id):
    """Retourne le statut actuel d'une commande pour la mise à jour en temps réel"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Formater les dates pour JavaScript
    def format_date(date):
        return date.strftime('%d/%m/%Y à %H:%M') if date else None
    
    data = {
        'statut': commande.statut,
        'statut_display': commande.get_statut_display(),
        'statut_class': commande.get_statut_display_class(),
        'date_commande': format_date(commande.date_commande),
        'date_paiement': format_date(commande.date_paiement),
        'date_preparation': format_date(commande.date_preparation),
        'date_prete': format_date(commande.date_prete),
        'date_recuperation': format_date(commande.date_recuperation),
    }
    
    return JsonResponse(data)

@login_required
def liste_commande_a_preparer(request):
    """
    Affiche la liste des commandes à préparer avec le détail des produits
    Accessible aux gérants et préparateurs
    """
    user = request.user
    
    # Vérification des permissions
    is_gerant = user.is_staff or user.username == 'randr' or user.groups.filter(name='Gerants').exists()
    
    if not is_gerant:
        return redirect('accueil')
    
    # Récupérer les commandes du jour qui sont payées ou en préparation
    today = timezone.now().date()
    commandes_a_preparer = (
        Commande.objects
        .filter(
            date_collecte=today,
            statut__in=['payee', 'en_preparation', 'prete']
        )
        .exclude(statut__in=['annulee', 'en_attente', 'recuperee'])
        .order_by('heure_collecte', 'statut')  # Tri par heure puis par statut
        .prefetch_related('lignes')  # Optimisation pour charger les lignes
    )
    
    context = {
        'commandes_a_preparer': commandes_a_preparer,
        'boulangerie': get_boulangerie(),
    }
    
    return render(request, 'main/gerant/liste_commande_a_preparer.html', context)

# Gerant - informations générales et mdp

@login_required
def parametres_boulangerie(request):
    """Vue combinée pour les informations générales et le changement de mot de passe"""
    # Vérifier que l'utilisateur est gérant
    user = request.user
    is_gerant = user.is_staff or user.username == 'randr' or user.groups.filter(name='Gerants').exists()
    
    if not is_gerant:
        return redirect('accueil')
    
    # Récupérer ou créer la boulangerie
    boulangerie = get_boulangerie()
    
    # Initialiser les deux formulaires
    info_form = BoulangerieInfoForm(instance=boulangerie)
    password_form = CustomPasswordChangeForm(request.user)
    
    if request.method == 'POST':
        # Déterminer quel formulaire a été soumis
        if 'save_info' in request.POST:
            # Traitement du formulaire d'informations
            info_form = BoulangerieInfoForm(request.POST, instance=boulangerie)
            if info_form.is_valid():
                info_form.save()
                messages.success(request, 'Les informations ont été mises à jour avec succès.')
                return redirect('parametres_boulangerie')
        
        elif 'change_password' in request.POST:
            # Traitement du formulaire de mot de passe
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                # Vérifier que le nouveau mot de passe est bien 6 chiffres
                new_password = password_form.cleaned_data['new_password1']
                if len(new_password) != 6 or not new_password.isdigit():
                    messages.error(request, 'Le mot de passe doit contenir exactement 6 chiffres.')
                else:
                    user = password_form.save()
                    # Garder l'utilisateur connecté après le changement
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Votre mot de passe a été modifié avec succès.')
                    return redirect('parametres_boulangerie')
    
    context = {
        'info_form': info_form,
        'password_form': password_form,
        'boulangerie': boulangerie,
    }
    return render(request, 'main/gerant/parametres_boulangerie.html', context)

# parametre gérant - informations générales et mdp

@login_required
def parametres_gerant(request):
    """Vue combinée pour les informations du gérant et le changement de mot de passe"""
    # Vérifier que l'utilisateur est gérant
    user = request.user
    is_gerant = user.is_staff or user.username == 'randr' or user.groups.filter(name='Gerants').exists()
    
    if not is_gerant:
        return redirect('accueil')
    
    # Initialiser les formulaires avec les données existantes
    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'telephone': user.profile.telephone if hasattr(user, 'profile') else ''
    }
    
    info_form = GerantInfoForm(initial=initial_data)
    password_form = CustomPasswordChangeForm(request.user)
    
    if request.method == 'POST':
        # Déterminer quel formulaire a été soumis
        if 'save_info' in request.POST:
            # Traitement du formulaire d'informations
            info_form = GerantInfoForm(request.POST)
            if info_form.is_valid():
                # Mettre à jour les informations de l'utilisateur
                user.first_name = info_form.cleaned_data['first_name']
                user.last_name = info_form.cleaned_data['last_name']
                user.save()
                
                # Mettre à jour le téléphone dans le profil
                if hasattr(user, 'profile'):
                    user.profile.telephone = info_form.cleaned_data.get('telephone', '')
                    user.profile.save()
                
                messages.success(request, 'Vos informations ont été mises à jour avec succès.')
                return redirect('parametres_gerant')
        
        elif 'change_password' in request.POST:
            # Traitement du formulaire de mot de passe
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                # Vérifier que le nouveau mot de passe est bien 6 chiffres
                new_password = password_form.cleaned_data['new_password1']
                if len(new_password) != 6 or not new_password.isdigit():
                    messages.error(request, 'Le mot de passe doit contenir exactement 6 chiffres.')
                else:
                    user = password_form.save()
                    # Garder l'utilisateur connecté après le changement
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Votre mot de passe a été modifié avec succès.')
                    return redirect('parametres_gerant')
    
    context = {
        'info_form': info_form,
        'password_form': password_form,
        'boulangerie': get_boulangerie(),
    }
    return render(request, 'main/gerant/parametres_gerant.html', context)

# creer personnel 

# Ajoutez cette vue dans votre views.py
# N'oubliez pas d'importer CreerPersonnelForm depuis forms.py et le décorateur gerant_required
# from .decorators import gerant_required  # Si vous avez créé le décorateur

@login_required
def creer_personnel(request):
    """Vue pour créer un nouveau compte personnel"""
    # Vérifier que l'utilisateur est gérant (si pas de décorateur)
    # user = request.user
    # is_gerant = user.is_staff or user.username == 'randr' or user.groups.filter(name='Gerants').exists()
    # if not is_gerant:
    #     return redirect('accueil')
    
    if request.method == 'POST':
        form = CreerPersonnelForm(request.POST)
        if form.is_valid():
            try:
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['prenom'],
                    last_name=form.cleaned_data['nom']
                )
                
                # Ajouter le téléphone au profil
                if hasattr(user, 'profile'):
                    user.profile.telephone = form.cleaned_data.get('telephone', '')
                    user.profile.save()
                
                # Assigner au groupe Personnel
                try:
                    groupe_personnel = Group.objects.get(name='Personnel')
                    user.groups.add(groupe_personnel)
                except Group.DoesNotExist:
                    messages.warning(request, "Le groupe 'Personnel' n'existe pas. Exécutez la commande init_groups.")
                
                # Envoyer l'email de confirmation
                try:
                    envoyer_email_creation_personnel(user, form.cleaned_data['password'])
                    messages.success(
                        request, 
                        f'Le compte personnel pour {user.get_full_name()} a été créé avec succès. '
                        f'Un email de confirmation a été envoyé à {user.email}.'
                    )
                except Exception as e:
                    messages.warning(
                        request,
                        f'Le compte a été créé mais l\'email n\'a pas pu être envoyé : {str(e)}'
                    )
                
                # Rediriger vers le formulaire vide pour créer un autre personnel
                return redirect('creer_personnel')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
    else:
        form = CreerPersonnelForm()
    
    # Récupérer la liste du personnel existant
    personnel_list = User.objects.filter(
        groups__name='Personnel'
    ).select_related('profile').order_by('last_name', 'first_name')
    
    context = {
        'form': form,
        'boulangerie': get_boulangerie(),
        'personnel_list': personnel_list,
    }
    return render(request, 'main/gerant/creer_personnel.html', context)

def envoyer_email_creation_personnel(user, password):
    """Envoie un email au nouveau personnel avec ses identifiants"""
    boulangerie = get_boulangerie()
    
    sujet = f'Votre compte personnel - {boulangerie.nom}'
    
    # Version texte
    message_text = f"""
Bonjour {user.first_name} {user.last_name},

Votre compte personnel pour {boulangerie.nom} a été créé avec succès.

Voici vos identifiants de connexion :
- Email : {user.email}
- Mot de passe : {password}

Pour vous connecter, rendez-vous sur la page de connexion professionnelle :
{settings.SITE_URL}/connexion-pro/

Important : Nous vous recommandons de changer votre mot de passe lors de votre première connexion.

Pour cela :
1. Connectez-vous avec les identifiants ci-dessus
2. Accédez à vos paramètres personnels
3. Changez votre mot de passe

Si vous avez des questions, n'hésitez pas à contacter votre gérant.

Cordialement,
L'équipe {boulangerie.nom}
{boulangerie.adresse}
{boulangerie.code} {boulangerie.ville}
{boulangerie.telephone}
"""    
    # Version HTML
    html_content = render_to_string('main/emails/creation_personnel_email.html', {
        'user': user,
        'password': password,
        'boulangerie': boulangerie,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    })
    
    # Créer l'email
    email = EmailMultiAlternatives(
        subject=sujet,
        body=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    # Envoyer
    email.send(fail_silently=False)

# Personnel - modifier supprimer

@login_required
def modifier_personnel(request, personnel_id):
    """Vue pour modifier un compte personnel"""
    personnel = get_object_or_404(User, id=personnel_id, groups__name='Personnel')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        personnel.first_name = request.POST.get('prenom', '')
        personnel.last_name = request.POST.get('nom', '')
        
        # Mettre à jour le téléphone dans le profil
        if hasattr(personnel, 'profile'):
            personnel.profile.telephone = request.POST.get('telephone', '')
            personnel.profile.save()
        
        # Si un nouveau mot de passe est fourni
        new_password = request.POST.get('password', '')
        if new_password and len(new_password) == 6 and new_password.isdigit():
            personnel.set_password(new_password)
            
            # Envoyer un email avec le nouveau mot de passe
            try:
                envoyer_email_modification_mot_de_passe(personnel, new_password)
                messages.info(request, 'Un email avec le nouveau mot de passe a été envoyé.')
            except Exception as e:
                messages.warning(request, f'Le mot de passe a été changé mais l\'email n\'a pas pu être envoyé : {str(e)}')
        
        personnel.save()
        messages.success(request, f'Les informations de {personnel.get_full_name()} ont été mises à jour.')
        return redirect('creer_personnel')
    
    # Préparer les données initiales
    initial_data = {
        'nom': personnel.last_name,
        'prenom': personnel.first_name,
        'email': personnel.email,
        'telephone': personnel.profile.telephone if hasattr(personnel, 'profile') else ''
    }
    
    context = {
        'personnel': personnel,
        'initial_data': initial_data,
        'boulangerie': get_boulangerie(),
    }
    return render(request, 'main/gerant/modifier_personnel.html', context)


@login_required
def supprimer_personnel(request, personnel_id):
    """Vue pour supprimer un compte personnel"""
    if request.method == 'POST':
        personnel = get_object_or_404(User, id=personnel_id, groups__name='Personnel')
        nom_complet = personnel.get_full_name()
        
        try:
            # Supprimer l'utilisateur (le profil sera supprimé automatiquement)
            personnel.delete()
            messages.success(request, f'Le compte de {nom_complet} a été supprimé avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    
    return redirect('creer_personnel')


def envoyer_email_modification_mot_de_passe(user, new_password):
    """Envoie un email au personnel avec son nouveau mot de passe"""
    boulangerie = get_boulangerie()
    
    sujet = f'Modification de votre mot de passe - {boulangerie.nom}'
    
    message_text = f"""
Bonjour {user.first_name} {user.last_name},

Votre mot de passe pour votre compte personnel chez {boulangerie.nom} a été modifié.

Votre nouveau mot de passe est : {new_password}

Pour vous connecter : {settings.SITE_URL}/connexion-pro/

Nous vous recommandons de changer ce mot de passe lors de votre prochaine connexion.

Cordialement,
L'équipe {boulangerie.nom}
"""
    
    send_mail(
        sujet,
        message_text,
        settings.DEFAULT_FROM_EMAIL or 'noreply@paindore.com',
        [user.email],
        fail_silently=False,
    )

# compte personnel

@login_required  # Ou @login_required si pas de décorateur
def dashboard_personnel(request):
    """Tableau de bord du personnel"""
    # Vérifier que l'utilisateur est bien du personnel (si pas de décorateur)
    # if not request.user.groups.filter(name='Personnel').exists():
    #     return redirect('accueil')
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Commandes du jour
    commandes_jour = Commande.objects.filter(
        date_collecte=today
    ).exclude(statut__in=['annulee', 'en_attente'])
    
    # Statistiques des commandes
    stats = {
        'total_jour': commandes_jour.count(),
        'a_preparer': commandes_jour.filter(statut='payee').count(),
        'en_preparation': commandes_jour.filter(statut='en_preparation').count(),
        'pretes': commandes_jour.filter(statut='prete').count(),
        'recuperees': commandes_jour.filter(statut='recuperee').count(),
    }
    
    # Commandes urgentes (dans l'heure qui suit)
    heure_limite = now + timedelta(hours=1)
    commandes_urgentes = commandes_jour.filter(
        statut__in=['payee', 'en_preparation'],
        date_collecte=today,
        heure_collecte__lte=heure_limite.time()
    ).order_by('heure_collecte')[:5]
    
    # Prochaines commandes à préparer
    prochaines_commandes = commandes_jour.filter(
        statut='payee'
    ).order_by('heure_collecte')[:10]
    
    # Notifications non lues (si vous avez un système de notifications)
    # notifications = NotificationPersonnel.objects.filter(
    #     destinataire=request.user,
    #     lue=False
    # ).count()
    
    # Performance personnelle du jour
    commandes_traitees = commandes_jour.filter(
        Q(statut='prete') | Q(statut='recuperee'),
        # Si vous trackez qui a préparé la commande :
        # preparee_par=request.user
    ).count()
    
    # Graphique des commandes par heure
    commandes_par_heure = []
    for hour in range(7, 21):  # De 7h à 20h
        count = commandes_jour.filter(
            heure_collecte__hour=hour
        ).count()
        commandes_par_heure.append({
            'heure': f"{hour}h",
            'nombre': count
        })
    
    context = {
        'boulangerie': get_boulangerie(),
        'stats': stats,
        'commandes_urgentes': commandes_urgentes,
        'prochaines_commandes': prochaines_commandes,
        'commandes_traitees': commandes_traitees,
        'commandes_par_heure': commandes_par_heure,
        'today': today,
        'commandes_en_attente_count': stats['a_preparer'],  # Pour la navbar
        'notifications_count': 0,  # À remplacer par le vrai compte
    }
    
    return render(request, 'main/personnel/dashboard_personnel.html', context)

@login_required  # Ou @login_required
def parametres_personnel(request):
    """Vue pour les paramètres du compte personnel"""
    # Vérifier que l'utilisateur est bien du personnel (si pas de décorateur)
    # if not request.user.groups.filter(name='Personnel').exists():
    #     return redirect('accueil')
    
    user = request.user
    
    # Initialiser les formulaires avec les données existantes
    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'telephone': user.profile.telephone if hasattr(user, 'profile') else ''
    }
    
    # Utiliser le même formulaire que pour le gérant
    info_form = GerantInfoForm(initial=initial_data)
    password_form = CustomPasswordChangeForm(request.user)
    
    if request.method == 'POST':
        # Déterminer quel formulaire a été soumis
        if 'save_info' in request.POST:
            # Le personnel peut seulement modifier son téléphone
            info_form = GerantInfoForm(request.POST)
            if info_form.is_valid():
                # Mettre à jour uniquement le téléphone
                if hasattr(user, 'profile'):
                    user.profile.telephone = info_form.cleaned_data.get('telephone', '')
                    user.profile.save()
                else:
                    # Créer le profil s'il n'existe pas
                    from main.models import Profile
                    Profile.objects.create(
                        user=user,
                        telephone=info_form.cleaned_data.get('telephone', '')
                    )
                
                messages.success(request, 'Votre numéro de téléphone a été mis à jour.')
                return redirect('parametres_personnel')
        
        elif 'change_password' in request.POST:
            # Changement de mot de passe
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                # Vérifier que le nouveau mot de passe est bien 6 chiffres
                new_password = password_form.cleaned_data['new_password1']
                if len(new_password) != 6 or not new_password.isdigit():
                    messages.error(request, 'Le mot de passe doit contenir exactement 6 chiffres.')
                else:
                    user = password_form.save()
                    # Garder l'utilisateur connecté après le changement
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Votre mot de passe a été modifié avec succès.')
                    return redirect('parametres_personnel')
    
    context = {
        'info_form': info_form,
        'password_form': password_form,
        'boulangerie': get_boulangerie(),
    }
    return render(request, 'main/personnel/parametres_personnel.html', context)

@login_required  # Ou @login_required si vous n'avez pas le décorateur
def notifications_personnel(request):
    """Vue pour les notifications du personnel"""
    # Vérifier que l'utilisateur est bien du personnel (si pas de décorateur)
    # if not request.user.groups.filter(name='Personnel').exists():
    #     return redirect('accueil')
    
    # Pour l'instant, page basique - à développer plus tard
    context = {
        'boulangerie': get_boulangerie(),
        'notifications': [],  # À remplacer par un vrai système de notifications
    }
    
    return render(request, 'main/personnel/notifications_personnel.html', context)


@login_required  # Ou @login_required si vous n'avez pas le décorateur
def historique_commandes_personnel(request):
    """Vue pour l'historique des commandes du personnel"""
    # Vérifier que l'utilisateur est bien du personnel (si pas de décorateur)
    # if not request.user.groups.filter(name='Personnel').exists():
    #     return redirect('accueil')
    
    today = timezone.now().date()
    
    # Récupérer toutes les commandes du jour qui ont été traitées
    commandes_historique = Commande.objects.filter(
        date_collecte=today,
        statut__in=['prete', 'recuperee']
    ).order_by('-date_prete', '-heure_collecte')
    
    # Statistiques du jour
    stats = {
        'total_preparees': commandes_historique.filter(statut='prete').count(),
        'total_recuperees': commandes_historique.filter(statut='recuperee').count(),
    }
    
    context = {
        'boulangerie': get_boulangerie(),
        'commandes': commandes_historique,
        'stats': stats,
        'today': today,
    }
    
    return render(request, 'main/personnel/historique_commandes_personnel.html', context)


