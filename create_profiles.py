from django.contrib.auth.models import User
from main.models import Profile

# Créer les profils pour tous les utilisateurs existants
users_without_profile = User.objects.filter(profile__isnull=True)
count = 0

for user in users_without_profile:
    Profile.objects.create(user=user)
    count += 1
    print(f"Profil créé pour : {user.username}")

print(f"\nTotal : {count} profils créés")

# Afficher les statistiques
total_users = User.objects.count()
total_profiles = Profile.objects.count()
print(f"Utilisateurs totaux : {total_users}")
print(f"Profils totaux : {total_profiles}")