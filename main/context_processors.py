# main/context_processors.py

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
