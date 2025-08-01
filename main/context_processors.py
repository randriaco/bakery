# main/context_processors.py

# from datetime import timezone
from django.utils import timezone
from .models import Commande

def pretes_count(request):
    """
    Ajoute en contexte le nombre de commandes 'prete' pour l'utilisateur connecté.
    """
    count = 0
    if request.user.is_authenticated:
        count = Commande.objects.filter(
            client=request.user,
            statut='prete'
        ).count()
    return {
        'pretes_count': count
    }

# Personnel

def personnel_context(request):
    """Context processor pour le personnel"""
    context = {}
    
    if request.user.is_authenticated and request.user.groups.filter(name='Personnel').exists():
        # Compter les commandes en attente
        commandes_en_attente = Commande.objects.filter(
            date_collecte=timezone.now().date(),
            statut='payee'
        ).count()
        
        # Compter les notifications non lues (si vous avez un système de notifications)
        # notifications_count = NotificationPersonnel.objects.filter(
        #     destinataire=request.user,
        #     lue=False
        # ).count()
        
        context = {
            'commandes_en_attente_count': commandes_en_attente,
            'notifications_count': 0,  # À remplacer par le vrai compte quand vous aurez les notifications
        }
    
    return context


# N'oubliez pas d'ajouter ce context processor dans settings.py :
# Dans TEMPLATES -> OPTIONS -> context_processors, ajoutez :
# 'main.context_processors.personnel_context',
