from . import views
from django.urls import path
from .views import (
    CategorieListView, CategorieCreateView, CategorieUpdateView, CategorieDeleteView,
    ProduitListView, ProduitCreateView, ProduitUpdateView, ProduitDeleteView,
    DashboardGerantView, DashboardClientView 
)

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'), 
    path('commander/', views.commander, name='commander'),
    path('panier/', views.panier, name='panier'),
    
    # API
    path('api/produits/', views.api_produits, name='api_produits'),
    path('api/creneaux-disponibles/', views.api_creneaux_disponibles, name='api_creneaux_disponibles'),
    
    # Pages gérant - Dashboard
    path('gerant/', DashboardGerantView.as_view(), name='dashboard_gerant'),

     # Pages Client - Dashboard
    path('client/', DashboardClientView.as_view(), name='dashboard_client'),

    # Pages gérant - Horaires
    path('gerant/frequence/', views.frequence_collecte, name='frequence_collecte'),
    path('gerant/horaires/', views.horaires_hebdomadaires, name='horaires_hebdomadaires'),
    path('gerant/fermetures/', views.fermetures_specifiques, name='fermetures_specifiques'),
    path('gerant/fermetures/<int:pk>/supprimer/', views.supprimer_fermeture_specifique, name='supprimer_fermeture_specifique'),
    path('gerant/fermetures-multi/', views.fermetures_multi_jours, name='fermetures_multi_jours'),
    path('gerant/fermetures-multi/<int:pk>/supprimer/', views.supprimer_fermeture_multi_jours, name='supprimer_fermeture_multi_jours'),
    
    # Pages gérant - Produits
    path('gerant/categories/', CategorieListView.as_view(), name='liste_categories'),
    path('gerant/categorie/nouvelle/', CategorieCreateView.as_view(), name='nouvelle_categorie'),
    path('gerant/categorie/<int:pk>/modifier/', CategorieUpdateView.as_view(), name='modifier_categorie'),
    path('gerant/categorie/<int:pk>/supprimer/', CategorieDeleteView.as_view(), name='supprimer_categorie'),
    path('gerant/produits/', ProduitListView.as_view(), name='liste_produits'),
    path('gerant/produit/nouveau/', ProduitCreateView.as_view(), name='nouveau_produit'),
    path('gerant/produit/<int:pk>/modifier/', ProduitUpdateView.as_view(), name='modifier_produit'),
    path('gerant/produit/<int:pk>/supprimer/', ProduitDeleteView.as_view(), name='supprimer_produit'),

    # Stripe
    path('paiement/creer-session/', views.creer_session_paiement, name='creer_session_paiement'),
    path('paiement/succes/', views.paiement_succes, name='paiement_succes'),

    # Authentification
    # Page de connexion personnalisée
    path('main/auth/connexion/', views.connexion, name='login'),

    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('mot-de-passe-oublie/', views.mot_de_passe_oublie, name='mot_de_passe_oublie'),
    path('reinitialiser-mot-de-passe/<str:token>/', views.reinitialiser_mot_de_passe, name='reinitialiser_mot_de_passe'),
    path('ajax/connexion/', views.ajax_connexion, name='ajax_connexion'),
    path('ajax/inscription/', views.ajax_inscription, name='ajax_inscription'),
    path('verification-code/', views.verification_code, name='verification_code'),
    path('renvoyer-code/', views.renvoyer_code, name='renvoyer_code'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Commandes client
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<str:numero_commande>/', views.detail_commande, name='detail_commande'),
    path('commande/<str:numero_commande>/facture/', views.telecharger_facture, name='telecharger_facture'),
    path('commande/<str:numero_commande>/annuler/', views.annuler_commande, name='annuler_commande'),

    # API
    path('vider-panier/', views.vider_panier_api, name='vider_panier_api'),
    path('changer-statut-commande/<int:commande_id>/', views.changer_statut_commande, name='changer_statut_commande'),
    path('api/commande/<int:commande_id>/details/', views.api_commande_details, name='api_commande_details'),
    path('api/stats-commandes/', views.api_stats_commandes, name='api_stats_commandes'),
    path('api/export-commandes/', views.api_export_commandes, name='api_export_commandes'),

    # Dashboard gérant
    path('connexion-pro/', views.connexion_pro, name='connexion_pro'),
    path('gerant/parametres-boulangerie/', views.parametres_boulangerie, name='parametres_boulangerie'),
    path('gerant/parametres-gerant/', views.parametres_gerant, name='parametres_gerant'),
    path('gerant/commandes/', views.dashboard_gerant_commandes, name='dashboard_gerant_commandes'),
    path('gerant/creer-personnel/', views.creer_personnel, name='creer_personnel'),
    # Gestion du personnel
    path('gerant/creer-personnel/', views.creer_personnel, name='creer_personnel'),
    path('gerant/modifier-personnel/<int:personnel_id>/', views.modifier_personnel, name='modifier_personnel'),
    path('gerant/supprimer-personnel/<int:personnel_id>/', views.supprimer_personnel, name='supprimer_personnel'),

    # Webhook Stripe
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
       
    # statut et code recuperation
    path('valider-code-recuperation/<int:commande_id>/', views.valider_code_recuperation, name='valider_code_recuperation'),
    path('api/commande/<int:commande_id>/statut/', views.api_commande_statut, name='api_commande_statut'),
    path('gerant/preparation-commandes/', views.liste_commande_a_preparer, name='liste_commande_a_preparer'),

    # Pages Personnel
    path('personnel/', views.dashboard_personnel, name='dashboard_personnel'),
    path('personnel/parametres/', views.parametres_personnel, name='parametres_personnel'),
    path('personnel/notifications/', views.notifications_personnel, name='notifications_personnel'),
    path('personnel/historique-commandes/', views.historique_commandes_personnel, name='historique_commandes_personnel'),
    
]