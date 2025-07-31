from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from django.contrib.auth.models import User
import random
import string

import secrets
from datetime import timedelta

import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver

class Boulangerie(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    telephone = models.CharField(max_length=10, default="0123456789")

    def __str__(self):
        return self.nom
    
class Contact(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message de {self.nom}"
    
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.nom
    
# ================= ajout : horaires click and collect ===========

class FrequenceCollecte(models.Model):
    """Fréquence des créneaux de collecte"""
    intervalle = models.IntegerField(
        default=30,
        choices=[
            (15, '15 minutes'),
            (30, '30 minutes'),
            (45, '45 minutes'),
            (60, '60 minutes'),
        ],
        verbose_name="Intervalle entre les créneaux"
    )

    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )

    class Meta:
        verbose_name = "Fréquence de collecte"
        verbose_name_plural = "Fréquence de collecte"

    def __str__(self):
        return f"Intervalle: {self.intervalle} minutes"

class HoraireHebdomadaire(models.Model):
    """Horaires d'ouverture hebdomadaires"""
    JOURS_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('ferme', 'Fermé'),
        ('ferme_matin', 'Fermé le matin'),
        ('ferme_soir', 'Fermé le soir'),
    ]
    
    jour = models.IntegerField(choices=JOURS_CHOICES, unique=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    
    # Horaires matin
    ouverture_matin = models.TimeField(default='07:00')
    fermeture_matin = models.TimeField(default='15:00')
    
    # Horaires soir
    ouverture_soir = models.TimeField(default='15:00')
    fermeture_soir = models.TimeField(default='20:00')
    
    class Meta:
        ordering = ['jour']
        verbose_name = "Horaire hebdomadaire"
        verbose_name_plural = "Horaires hebdomadaires"
    
    def __str__(self):
        return f"{self.get_jour_display()}"
    
    def est_ouvert_matin(self):
        return self.statut in ['ouvert', 'ferme_soir']
    
    def est_ouvert_soir(self):
        return self.statut in ['ouvert', 'ferme_matin']

class FermetureSpecifique(models.Model):
    """Fermetures exceptionnelles pour une journée"""
    TYPE_CHOICES = [
        ('journee', 'Journée complète'),
        ('matin', 'Fermé le matin'),
        ('soir', 'Fermé le soir'),
    ]
    
    date = models.DateField(unique=True)
    type_fermeture = models.CharField(max_length=10, choices=TYPE_CHOICES, default='journee')
    motif = models.CharField(max_length=200)
    notifier_clients = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = "Fermeture spécifique"
        verbose_name_plural = "Fermetures spécifiques"
    
    def __str__(self):
        return f"{self.date} - {self.get_type_fermeture_display()}"
    
    def est_passe(self):
        return self.date < timezone.now().date()

class FermetureMultiJours(models.Model):
    """Fermetures sur plusieurs jours (congés, etc.)"""
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.CharField(max_length=200)
    notifier_clients = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date_debut']
        verbose_name = "Fermeture multi-jours"
        verbose_name_plural = "Fermetures multi-jours"
    
    def __str__(self):
        return f"Du {self.date_debut} au {self.date_fin} - {self.motif}"
    
    def nombre_jours(self):
        return (self.date_fin - self.date_debut).days + 1
    
    def est_en_cours(self):
        today = timezone.now().date()
        return self.date_debut <= today <= self.date_fin
    
    def est_a_venir(self):
        return self.date_debut > timezone.now().date()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_debut and self.date_fin:
            if self.date_debut > self.date_fin:
                raise ValidationError('La date de début doit être avant la date de fin.')
            
# Ajoutez ce modèle
class CodeVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        # Code valide pendant 60 secondes
        return (timezone.now() - self.created_at).seconds < 60 and not self.is_used
    
    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))
    
# réinitialisation de mot de passe
class TokenReinitialisationMotDePasse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de réinitialisation"
        verbose_name_plural = "Tokens de réinitialisation"
        ordering = ['-created_at']
    
    @classmethod
    def generate_token(cls):
        """Génère un token unique"""
        return secrets.token_urlsafe(48)
    
    def is_valid(self):
        """Vérifie si le token est encore valide (24 heures)"""
        if self.is_used:
            return False
        return timezone.now() < self.created_at + timedelta(hours=24)
    
    def __str__(self):
        return f"Token pour {self.user.email} - {'Utilisé' if self.is_used else 'Valide'}"

# système de paiement stripe

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('payee', 'Payée'),
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête'),
        ('recuperee', 'Récupérée'),
        ('annulee', 'Annulée'),
    ]
    
    numero_commande = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commandes')
    date_commande = models.DateTimeField(default=timezone.now)
    date_collecte = models.DateField()
    heure_collecte = models.TimeField()
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    # Montants
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    frais_service = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stripe
    stripe_session_id = models.CharField(max_length=200, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, null=True)
    
    # Notifications
    email_confirmation_envoye = models.BooleanField(default=False)
    facture_envoyee = models.BooleanField(default=False)
    
    # Timestamps
    date_paiement = models.DateTimeField(blank=True, null=True)
    date_preparation = models.DateTimeField(blank=True, null=True)
    date_prete = models.DateTimeField(blank=True, null=True)
    date_recuperation = models.DateTimeField(blank=True, null=True)
    
    # Notes
    notes_client = models.TextField(blank=True)
    notes_interne = models.TextField(blank=True)

    # code de verification
    code_recuperation = models.CharField(max_length=4, null=True, blank=True)
    
    class Meta:
        ordering = ['-date_commande']
        
    def __str__(self):
        return f"Commande {self.numero_commande}"
    
    def get_statut_display_class(self):
        """Retourne la classe CSS Bootstrap pour le statut"""
        classes = {
            'payee': 'info',
            'en_preparation': 'warning',
            'prete': 'success',
            'recuperee': 'secondary',
            'annulee': 'danger' 
        }
        return classes.get(self.statut, 'secondary')

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            # Générer un numéro de commande unique
            date_str = timezone.now().strftime('%Y%m%d')
            # Compter les commandes du jour
            count = Commande.objects.filter(
                date_commande__date=timezone.now().date()
            ).count() + 1
            self.numero_commande = f"{date_str}-{count:04d}"
        super().save(*args, **kwargs)
    
    def get_statut_display_class(self):
        """Retourne la classe CSS pour le badge de statut"""
        classes = {
            'en_attente': 'warning',
            'payee': 'info',
            'en_preparation': 'primary',
            'prete': 'success',
            'recuperee': 'secondary',
            'annulee': 'danger'
        }
        return classes.get(self.statut, 'secondary')

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('Produit', on_delete=models.SET_NULL, null=True)
    
    # Copie des infos produit au moment de la commande
    nom_produit = models.CharField(max_length=200)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.CharField(max_length=100)
    
    quantite = models.PositiveIntegerField()
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantite}x {self.nom_produit}"

class NotificationCommande(models.Model):
    """Pour notifier le gérant des nouvelles commandes"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(default=timezone.now)
    vue = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_creation']

# profile -> telephone dans table user

class Profile(models.Model):
    """Profil étendu pour tous les utilisateurs avec téléphone"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def get_user_group(self):
        """Retourne le groupe principal de l'utilisateur"""
        if self.user.is_superuser:
            return "Superuser"
        elif self.user.groups.filter(name='Gerants').exists():
            return "Gérant"
        elif self.user.groups.filter(name='Personnel').exists():
            return "Personnel"
        elif self.user.groups.filter(name='Clients').exists():
            return "Client"
        return "Sans groupe"


# Signaux pour créer automatiquement un profil
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()