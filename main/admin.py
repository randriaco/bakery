from django.contrib import admin
from .models import (
    Boulangerie, Contact, Categorie, Produit,
    FrequenceCollecte, HoraireHebdomadaire, 
    FermetureSpecifique, FermetureMultiJours
)

from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Commande, LigneCommande, NotificationCommande

# Configuration existante...
admin.site.register(Boulangerie)
admin.site.register(Contact)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre')
    list_editable = ('ordre',)
    ordering = ('ordre', 'nom')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'date_creation')
    list_filter = ('categorie', 'date_creation')
    search_fields = ('nom', 'description')
    ordering = ('categorie', 'nom')

# Nouvelles configurations pour les horaires
@admin.register(FrequenceCollecte)
class FrequenceCollecteAdmin(admin.ModelAdmin):
    list_display = ('intervalle', 'date_modification')

@admin.register(HoraireHebdomadaire)
class HoraireHebdomadaireAdmin(admin.ModelAdmin):
    list_display = ('get_jour_display', 'statut', 'ouverture_matin', 'fermeture_matin', 'ouverture_soir', 'fermeture_soir')
    list_editable = ('statut', 'ouverture_matin', 'fermeture_matin', 'ouverture_soir', 'fermeture_soir')
    ordering = ('jour',)

@admin.register(FermetureSpecifique)
class FermetureSpecifiqueAdmin(admin.ModelAdmin):
    list_display = ('date', 'type_fermeture', 'motif', 'notifier_clients')
    list_filter = ('type_fermeture', 'notifier_clients')
    date_hierarchy = 'date'
    ordering = ('date',)

@admin.register(FermetureMultiJours)
class FermetureMultiJoursAdmin(admin.ModelAdmin):
    list_display = ('date_debut', 'date_fin', 'motif', 'nombre_jours', 'notifier_clients')
    list_filter = ('notifier_clients',)
    ordering = ('date_debut',)

# système de paiement

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('nom_produit', 'prix_unitaire', 'categorie', 'quantite', 'sous_total')
    can_delete = False

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'numero_commande', 
        'client_info', 
        'date_commande_format', 
        'date_collecte_format',
        'total_format',
        'statut_badge',
        'actions_buttons'
    ]
    
    list_filter = [
        'statut',
        'date_commande',
        'date_collecte',
        ('client', admin.RelatedOnlyFieldListFilter)
    ]
    
    search_fields = [
        'numero_commande',
        'client__email',
        'client__first_name',
        'client__last_name'
    ]
    
    readonly_fields = [
        'numero_commande',
        'date_commande',
        'date_paiement',
        'date_preparation',
        'date_prete',
        'date_recuperation',
        'stripe_session_id',
        'stripe_payment_intent',
        'email_confirmation_envoye',
        'facture_envoyee'
    ]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_commande', 'client', 'statut')
        }),
        ('Dates et horaires', {
            'fields': (
                'date_commande',
                'date_collecte',
                'heure_collecte',
                'date_paiement',
                'date_preparation',
                'date_prete',
                'date_recuperation'
            )
        }),
        ('Montants', {
            'fields': ('sous_total', 'frais_service', 'total')
        }),
        ('Paiement Stripe', {
            'fields': ('stripe_session_id', 'stripe_payment_intent'),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('email_confirmation_envoye', 'facture_envoyee')
        }),
        ('Notes', {
            'fields': ('notes_client', 'notes_interne'),
            'classes': ('wide',)
        })
    )
    
    inlines = [LigneCommandeInline]
    
    def client_info(self, obj):
        return format_html(
            '{}<br><small>{}</small>',
            obj.client.get_full_name() or obj.client.username,
            obj.client.email
        )
    client_info.short_description = 'Client'
    
    def date_commande_format(self, obj):
        return obj.date_commande.strftime('%d/%m/%Y %H:%M')
    date_commande_format.short_description = 'Date commande'
    
    def date_collecte_format(self, obj):
        return format_html(
            '{}<br><small>{}</small>',
            obj.date_collecte.strftime('%d/%m/%Y'),
            obj.heure_collecte.strftime('%H:%M')
        )
    date_collecte_format.short_description = 'Collecte'
    
    def total_format(self, obj):
        return format_html('<strong>{}€</strong>', obj.total)
    total_format.short_description = 'Total'
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ffc107',
            'payee': '#17a2b8',
            'en_preparation': '#007bff',
            'prete': '#28a745',
            'recuperee': '#6c757d',
            'annulee': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    def actions_buttons(self, obj):
        buttons = []
        
        # Bouton voir sur le site
        url = reverse('detail_commande', args=[obj.numero_commande])
        buttons.append(f'<a href="{url}" class="button" target="_blank">Voir</a>')
        
        # Bouton facture
        if obj.statut != 'en_attente':
            url = reverse('telecharger_facture', args=[obj.numero_commande])
            buttons.append(f'<a href="{url}" class="button" target="_blank">Facture</a>')
        
        return format_html(' '.join(buttons))
    actions_buttons.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        # Si le statut change, mettre à jour les timestamps
        if change and 'statut' in form.changed_data:
            if obj.statut == 'en_preparation' and not obj.date_preparation:
                obj.date_preparation = timezone.now()
            elif obj.statut == 'prete' and not obj.date_prete:
                obj.date_prete = timezone.now()
                # Envoyer notification au client
                from .views import envoyer_notification_commande_prete
                envoyer_notification_commande_prete(obj)
            elif obj.statut == 'recuperee' and not obj.date_recuperation:
                obj.date_recuperation = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client').prefetch_related('lignes')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(NotificationCommande)
class NotificationCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'date_creation', 'vue']
    list_filter = ['vue', 'date_creation']
    readonly_fields = ['commande', 'date_creation']
    
    def has_add_permission(self, request):
        return False
    
# ajout - système groupe 

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

# Inline pour afficher le profil dans l'admin User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['telephone']

# Étendre UserAdmin pour inclure le profil
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups', 'get_telephone')
    
    def get_groups(self, obj):
        """Affiche les groupes de l'utilisateur"""
        return ', '.join([g.name for g in obj.groups.all()]) or 'Aucun groupe'
    get_groups.short_description = 'Groupes'
    
    def get_telephone(self, obj):
        """Affiche le téléphone depuis le profil"""
        return obj.profile.telephone if hasattr(obj, 'profile') else '-'
    get_telephone.short_description = 'Téléphone'

# Ré-enregistrer UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Admin pour Profile séparé (optionnel)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telephone', 'get_user_group', 'get_user_email']
    list_filter = ['user__groups']
    search_fields = ['user__username', 'user__email', 'telephone']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    
    def get_user_group(self, obj):
        return obj.get_user_group()
    get_user_group.short_description = 'Type de compte'
