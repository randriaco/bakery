# Créez ce fichier : main/management/commands/create_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile

class Command(BaseCommand):
    help = 'Crée les profils manquants pour les utilisateurs existants'

    def handle(self, *args, **kwargs):
        # Créer les profils pour tous les utilisateurs existants
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0

        for user in users_without_profile:
            Profile.objects.create(user=user)
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Profil créé pour : {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal : {count} profils créés"))

        # Afficher les statistiques
        total_users = User.objects.count()
        total_profiles = Profile.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Utilisateurs totaux : {total_users}"))
        self.stdout.write(self.style.SUCCESS(f"Profils totaux : {total_profiles}"))