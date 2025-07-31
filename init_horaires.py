from main.models import FrequenceCollecte, HoraireHebdomadaire, Boulangerie
from datetime import time

def initialiser_horaires():
    """Initialise les données de base pour les horaires"""
    
    print("🚀 Initialisation des horaires...")
    
    # 1. Créer la fréquence par défaut (30 minutes)
    frequence, created = FrequenceCollecte.objects.get_or_create(
        pk=1,
        defaults={'intervalle': 30}
    )
    if created:
        print("✓ Fréquence créée : 30 minutes")
    else:
        print("- Fréquence existante : {} minutes".format(frequence.intervalle))
    
    # 2. Créer les horaires hebdomadaires pour les 7 jours
    jours_semaine = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    print("\n📅 Création des horaires hebdomadaires...")
    
    for jour_num, jour_nom in jours_semaine:
        horaire, created = HoraireHebdomadaire.objects.get_or_create(
            jour=jour_num,
            defaults={
                'statut': 'ouvert',
                'ouverture_matin': time(7, 0),
                'fermeture_matin': time(15, 0),
                'ouverture_soir': time(15, 0),
                'fermeture_soir': time(20, 0),
            }
        )
        
        if created:
            print(f"  ✓ {jour_nom} : 7h00-15h00 / 15h00-20h00")
        else:
            print(f"  - {jour_nom} : horaires existants")
    
    # 3. Vérifier/créer la boulangerie si elle n'existe pas
    if not Boulangerie.objects.exists():
        Boulangerie.objects.create(
            nom="La Boulangerie Dorée",
            adresse="123 rue du Pain",
            code="75001",
            ville="Paris",
            telephone="0123456789"
        )
        print("\n✓ Boulangerie créée")
    
    print("\n✅ Initialisation terminée !")
    print("\nVous pouvez maintenant :")
    print("  - Aller sur /gerant/frequence/ pour modifier la fréquence")
    print("  - Aller sur /gerant/horaires/ pour modifier les horaires")
    print("  - Aller sur /gerant/fermetures/ pour ajouter des fermetures")

# Après avoir défini la fonction, exécutez-la
initialiser_horaires()