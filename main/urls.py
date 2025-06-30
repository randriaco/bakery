from . import views
from django.urls import path
from .views import (
    CategorieListView, CategorieCreateView, CategorieUpdateView, CategorieDeleteView,
    ProduitListView, ProduitCreateView, ProduitUpdateView, ProduitDeleteView,
    DashboardGerantView
)

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('gerant/', DashboardGerantView.as_view(), name='dashboard_gerant'),
    path('gerant/categories/', CategorieListView.as_view(), name='liste_categories'),
    path('gerant/categorie/nouvelle/', CategorieCreateView.as_view(), name='nouvelle_categorie'),
    path('gerant/categorie/<int:pk>/modifier/', CategorieUpdateView.as_view(), name='modifier_categorie'),
    path('gerant/categorie/<int:pk>/supprimer/', CategorieDeleteView.as_view(), name='supprimer_categorie'),
    path('gerant/produits/', ProduitListView.as_view(), name='liste_produits'),
    path('gerant/produit/nouveau/', ProduitCreateView.as_view(), name='nouveau_produit'),
    path('gerant/produit/<int:pk>/modifier/', ProduitUpdateView.as_view(), name='modifier_produit'),
    path('gerant/produit/<int:pk>/supprimer/', ProduitDeleteView.as_view(), name='supprimer_produit'),

    # ======================================================
	path('commander/', views.commander, name='commander'),
    path('panier/', views.panier, name='panier'),
	
	# API
    path('api/produits/', views.api_produits, name='api_produits'),
]