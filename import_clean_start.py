#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'import avec nettoyage complet et correction des accents
Supprime toutes les données existantes avant l'import
"""

import csv
import os
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery.settings')
django.setup()

from main.models import Produit, Categorie

# Mapping des catégories avec accents corrects
CATEGORIES_MAPPING = {
    1: "Boissons",
    2: "Menus",
    3: "Pains",
    4: "Pâtisseries",  # Avec accent
    5: "Snacks salés",  # Avec accent et "salés"
    6: "Viennoiseries"
}

# Dictionnaire de correction des accents pour les produits
CORRECTIONS_ACCENTS = {
    'Eclair': 'Éclair',
    'The': 'Thé',
    'Cafe': 'Café',
    'vegetarienne': 'végétarienne',
    'legumes': 'légumes',
    'cereales': 'céréales',
    'Feuillete': 'Feuilleté',
    'roule': 'roulé',
    'patissier': 'pâtissier',
    'pates': 'pâtes',
    'Pates': 'Pâtes',
    ' a la ': ' à la ',
    ' a l\'': ' à l\'',
}

def corriger_accents(texte):
    """Corrige les accents manquants dans un texte"""
    if not texte:
        return texte
    
    for sans_accent, avec_accent in CORRECTIONS_ACCENTS.items():
        texte = texte.replace(sans_accent, avec_accent)
    
    return texte

def nettoyer_base():
    """Supprime toutes les données existantes"""
    print("🗑️  Nettoyage de la base de données...")
    
    # Compter avant suppression
    nb_produits = Produit.objects.count()
    nb_categories = Categorie.objects.count()
    
    if nb_produits > 0 or nb_categories > 0:
        print(f"   - {nb_produits} produits à supprimer")
        print(f"   - {nb_categories} catégories à supprimer")
        
        # Demander confirmation
        print("\n⚠️  ATTENTION : Cette action va supprimer TOUS les produits et catégories !")
        confirmation = input("Êtes-vous sûr de vouloir continuer ? (tapez 'OUI' pour confirmer) : ")
        
        if confirmation.upper() == 'OUI':
            # Supprimer d'abord les produits (foreign key)
            Produit.objects.all().delete()
            print("   ✓ Produits supprimés")
            
            # Puis les catégories
            Categorie.objects.all().delete()
            print("   ✓ Catégories supprimées")
            
            print("   ✓ Base de données nettoyée !\n")
            return True
        else:
            print("   ❌ Annulation du nettoyage")
            return False
    else:
        print("   ℹ️  Base déjà vide\n")
        return True

def creer_categories():
    """Crée toutes les catégories avec les bons accents"""
    print("📁 Création des catégories...")
    categories = {}
    
    for cat_id, cat_nom in CATEGORIES_MAPPING.items():
        categorie = Categorie.objects.create(
            nom=cat_nom,
            ordre=cat_id
        )
        categories[cat_id] = categorie
        print(f"   ✓ {cat_nom} (ordre: {cat_id})")
    
    print(f"   ✓ {len(categories)} catégories créées\n")
    return categories

def import_produits(categories):
    """Importe les produits avec correction des accents"""
    print("📦 Import des produits...")
    count = 0
    erreurs = []
    
    try:
        with open('import_produit.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            for ligne_num, row in enumerate(reader, 2):  # 2 car ligne 1 = headers
                try:
                    # Nettoyer et corriger les données
                    nom_original = row['nom'].strip()
                    nom_corrige = corriger_accents(nom_original)
                    
                    description = row['description'] if row['description'] != 'NULL' else ''
                    description = corriger_accents(description)
                    
                    prix = Decimal(str(row['prix']).replace(',', '.'))
                    categorie_id = int(row['categorie_id'])
                    
                    # Récupérer la catégorie
                    categorie = categories.get(categorie_id)
                    if not categorie:
                        erreurs.append(f"Ligne {ligne_num}: Catégorie {categorie_id} non trouvée pour '{nom_original}'")
                        continue
                    
                    # Créer le produit
                    Produit.objects.create(
                        nom=nom_corrige,
                        description=description,
                        prix=prix,
                        categorie=categorie
                    )
                    count += 1
                    
                    # Afficher la progression
                    if count % 10 == 0:
                        print(f"   ... {count} produits importés")
                    
                except Exception as e:
                    erreurs.append(f"Ligne {ligne_num}: {str(e)}")
    
    except FileNotFoundError:
        print("   ❌ Fichier 'import_produit.csv' non trouvé !")
        print("   Assurez-vous que le fichier est dans le même dossier que ce script.")
        return 0, ["Fichier CSV non trouvé"]
    
    return count, erreurs

def afficher_resume():
    """Affiche un résumé de l'import"""
    print("\n📊 Résumé de la base de données :")
    print("=" * 50)
    
    total_produits = 0
    for categorie in Categorie.objects.all().order_by('ordre'):
        produits = categorie.produits.all()
        count = produits.count()
        total_produits += count
        
        print(f"\n{categorie.nom} ({count} produits) :")
        # Afficher quelques exemples
        for produit in produits[:3]:
            print(f"  - {produit.nom}: {produit.prix}€")
        if count > 3:
            print(f"  ... et {count - 3} autres")
    
    print("\n" + "=" * 50)
    print(f"TOTAL : {total_produits} produits dans {Categorie.objects.count()} catégories")

def main():
    """Fonction principale"""
    print("🚀 IMPORT DES PRODUITS AVEC NETTOYAGE COMPLET")
    print("=" * 60)
    print("Ce script va :")
    print("1. Supprimer TOUTES les catégories et produits existants")
    print("2. Créer 6 nouvelles catégories avec les bons accents")
    print("3. Importer tous les produits du fichier CSV")
    print("=" * 60)
    
    # Étape 1 : Nettoyer
    if not nettoyer_base():
        print("\n❌ Import annulé")
        return
    
    # Étape 2 : Créer les catégories
    categories = creer_categories()
    
    # Étape 3 : Importer les produits
    count, erreurs = import_produits(categories)
    
    # Afficher le résultat
    print(f"\n✅ Import terminé : {count} produits importés")
    
    if erreurs:
        print(f"\n⚠️  {len(erreurs)} erreurs rencontrées :")
        for erreur in erreurs[:5]:  # Afficher max 5 erreurs
            print(f"   - {erreur}")
        if len(erreurs) > 5:
            print(f"   ... et {len(erreurs) - 5} autres erreurs")
    
    # Afficher le résumé
    afficher_resume()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Import interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()