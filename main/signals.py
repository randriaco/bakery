from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Commande, NotificationCommande
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def add_user_to_client_group(sender, instance, created, **kwargs):
    """Ajoute automatiquement les nouveaux utilisateurs au groupe Clients"""
    if created:
        clients_group, _ = Group.objects.get_or_create(name='Clients')
        instance.groups.add(clients_group)

@receiver(pre_save, sender=Commande)
def update_commande_timestamps(sender, instance, **kwargs):
    """Met à jour automatiquement les timestamps selon les changements de statut"""
    if instance.pk:  # Si la commande existe déjà
        try:
            old_instance = Commande.objects.get(pk=instance.pk)
            
            # Si le statut change
            if old_instance.statut != instance.statut:
                from django.utils import timezone
                
                if instance.statut == 'payee' and not instance.date_paiement:
                    instance.date_paiement = timezone.now()
                    
                elif instance.statut == 'en_preparation' and not instance.date_preparation:
                    instance.date_preparation = timezone.now()
                    
                elif instance.statut == 'prete' and not instance.date_prete:
                    instance.date_prete = timezone.now()
                    
                elif instance.statut == 'recuperee' and not instance.date_recuperation:
                    instance.date_recuperation = timezone.now()
                    
        except Commande.DoesNotExist:
            pass

@receiver(post_save, sender=Commande)
def handle_commande_status_change(sender, instance, created, **kwargs):
    """Gère les actions après changement de statut"""
    if not created:  # Si c'est une mise à jour
        # Si la commande vient de passer à "prête"
        if instance.statut == 'prete' and instance.date_prete:
            # Envoyer une notification au client
            send_commande_ready_notification(instance)

def send_commande_ready_notification(commande):
    """Envoie une notification quand la commande est prête"""
    try:
        from .views import get_boulangerie
        boulangerie = get_boulangerie()
        
        subject = f'Votre commande est prête ! - {boulangerie.nom}'
        message = f"""
        Bonjour {commande.client.first_name},

        Bonne nouvelle ! Votre commande n°{commande.numero_commande} est prête.
        
        Vous pouvez venir la récupérer dès maintenant.
        Heure de retrait prévue : {commande.heure_collecte.strftime('%H:%M')}
        
        À tout de suite !
        L'équipe {boulangerie.nom}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [commande.client.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Erreur envoi notification: {str(e)}")

# Pour activer les signals, ajoutez dans votre apps.py :
"""
from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
    def ready(self):
        import main.signals
"""