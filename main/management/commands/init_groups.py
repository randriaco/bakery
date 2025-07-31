from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Crée les groupes utilisateurs et leurs permissions'

    def handle(self, *args, **kwargs):
        # Création des groupes
        groups_data = {
            'Clients': {
                'description': 'Clients de la boulangerie',
                'permissions': [
                    # Permissions pour les clients
                    'view_produit',
                    'add_commande',
                    'view_commande',
                    'change_commande',  # Pour annuler leurs commandes
                ]
            },
            'Gerants': {
                'description': 'Gérants de la boulangerie',
                'permissions': [
                    # Toutes les permissions sur les modèles principaux
                    'add_produit', 'change_produit', 'delete_produit', 'view_produit',
                    'add_categorie', 'change_categorie', 'delete_categorie', 'view_categorie',
                    'add_commande', 'change_commande', 'delete_commande', 'view_commande',
                    'add_boulangerie', 'change_boulangerie', 'delete_boulangerie', 'view_boulangerie',
                    'view_user', 'change_user',  # Pour voir et modifier les utilisateurs
                    'add_horairehebdomadaire', 'change_horairehebdomadaire', 'view_horairehebdomadaire',
                    'add_fermeturespecifique', 'change_fermeturespecifique', 'delete_fermeturespecifique', 'view_fermeturespecifique',
                ]
            },
            'Personnel': {
                'description': 'Personnel de la boulangerie',
                'permissions': [
                    # Permissions limitées pour le personnel
                    'view_produit',
                    'view_categorie',
                    'view_commande',
                    'change_commande',  # Pour changer le statut des commandes
                ]
            }
        }

        for group_name, group_info in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Groupe "{group_name}" créé'))
            else:
                self.stdout.write(self.style.WARNING(f'Groupe "{group_name}" existe déjà'))
            
            # Effacer les permissions existantes
            group.permissions.clear()
            
            # Ajouter les permissions
            for perm_codename in group_info['permissions']:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permission "{perm_codename}" non trouvée'))
            
            self.stdout.write(self.style.SUCCESS(f'Permissions mises à jour pour "{group_name}"'))

        # Note sur le groupe Superuser
        self.stdout.write(self.style.SUCCESS('\nNote: Les superusers ont toutes les permissions par défaut dans Django'))
        self.stdout.write(self.style.SUCCESS('Groupes créés: Clients, Gerants, Personnel'))
        self.stdout.write(self.style.SUCCESS('Le groupe Superuser est géré automatiquement par Django avec is_superuser=True'))	