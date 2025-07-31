from django import forms
from .models import Categorie, Produit
from .models import FrequenceCollecte, HoraireHebdomadaire, FermetureSpecifique, FermetureMultiJours
from django.core.exceptions import ValidationError
from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.validators import RegexValidator

from django.contrib.auth.forms import PasswordChangeForm
from .models import Boulangerie

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'ordre']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control input-ombre',
                'placeholder': 'Nom de la catégorie'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control input-ombre',
                'placeholder': 'Ordre d\'affichage'
            })
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['categorie', 'image', 'nom', 'description', 'prix']
        widgets = {
            'categorie': forms.Select(attrs={
                'class': 'form-control input-ombre'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control input-ombre'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control input-ombre',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control input-ombre',
                'placeholder': 'Description du produit',
                'style': 'height: 150px'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control input-ombre',
                'placeholder': 'Prix',
                'step': '0.01'
            })
        }

# ============== ajout horaires click and collect ==================

class FrequenceForm(forms.ModelForm):
    class Meta:
        model = FrequenceCollecte
        fields = ['intervalle']
        widgets = {
            'intervalle': forms.Select(attrs={
                'class': 'form-select shadow',
            })
        }

class HoraireHebdomadaireForm(forms.ModelForm):
    class Meta:
        model = HoraireHebdomadaire
        fields = ['statut', 'ouverture_matin', 'fermeture_matin', 'ouverture_soir', 'fermeture_soir']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select shadow'}),
            'ouverture_matin': forms.TimeInput(attrs={
                'class': 'form-control shadow',
                'type': 'time'
            }),
            'fermeture_matin': forms.TimeInput(attrs={
                'class': 'form-control shadow',
                'type': 'time'
            }),
            'ouverture_soir': forms.TimeInput(attrs={
                'class': 'form-control shadow',
                'type': 'time'
            }),
            'fermeture_soir': forms.TimeInput(attrs={
                'class': 'form-control shadow',
                'type': 'time'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        statut = cleaned_data.get('statut')
        
        # Validation des horaires selon le statut
        if statut in ['ouvert', 'ferme_soir']:
            ouverture_matin = cleaned_data.get('ouverture_matin')
            fermeture_matin = cleaned_data.get('fermeture_matin')
            if ouverture_matin and fermeture_matin and ouverture_matin >= fermeture_matin:
                raise ValidationError("L'heure d'ouverture du matin doit être avant l'heure de fermeture.")
        
        if statut in ['ouvert', 'ferme_matin']:
            ouverture_soir = cleaned_data.get('ouverture_soir')
            fermeture_soir = cleaned_data.get('fermeture_soir')
            if ouverture_soir and fermeture_soir and ouverture_soir >= fermeture_soir:
                raise ValidationError("L'heure d'ouverture du soir doit être avant l'heure de fermeture.")
        
        return cleaned_data

class FermetureSpecifiqueForm(forms.ModelForm):
    class Meta:
        model = FermetureSpecifique
        fields = ['date', 'type_fermeture', 'motif', 'notifier_clients']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control shadow',
                'type': 'date',
                'placeholder': 'jj/mm/aaaa'
            }),
            'type_fermeture': forms.Select(attrs={
                'class': 'form-select shadow'
            }),
            'motif': forms.TextInput(attrs={
                'class': 'form-control shadow',
                'placeholder': 'Raison de la fermeture'
            }),
            'notifier_clients': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'date': 'Date',
            'type_fermeture': 'Type de fermeture',
            'motif': 'Motif',
            'notifier_clients': 'Notifier les clients'
        }
        help_texts = {
            'notifier_clients': 'Un email sera envoyé aux clients ayant une commande prévue ce jour-là'
        }

class FermetureMultiJoursForm(forms.ModelForm):
    class Meta:
        model = FermetureMultiJours
        fields = ['date_debut', 'date_fin', 'motif', 'notifier_clients']
        widgets = {
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control shadow',
                'type': 'date',
                'placeholder': 'jj/mm/aaaa'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control shadow',
                'type': 'date',
                'placeholder': 'jj/mm/aaaa'
            }),
            'motif': forms.TextInput(attrs={
                'class': 'form-control shadow',
                'placeholder': 'Ex: Congés annuels, Travaux...'
            }),
            'notifier_clients': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'motif': 'Motif de la fermeture',
            'notifier_clients': 'Notifier les clients'
        }
        help_texts = {
            'notifier_clients': 'Les clients seront informés par email de cette période de fermeture'
        }

# formulaire inscription
class InscriptionForm(forms.Form):
    """Formulaire d'inscription pour les clients"""
    nom = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    prenom = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    email_confirm = forms.EmailField(required=True)
    telephone = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone',
            'pattern': '[0-9]{10}',
            'title': 'Entrez un numéro à 10 chiffres'
        })
    )
    password = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe (6 chiffres)',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
    )
    password_confirm = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password.isdigit():
            raise forms.ValidationError("Le mot de passe doit contenir uniquement des chiffres.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data


# class InscriptionForm(forms.Form):
#     nom = forms.CharField(max_length=100, required=True)
#     prenom = forms.CharField(max_length=100, required=True)
#     telephone = forms.CharField(max_length=20, required=True)
#     email = forms.EmailField(required=True)
#     email_confirm = forms.EmailField(required=True)
    
#     # Validation pour exactement 6 chiffres
#     password_validator = RegexValidator(
#         regex=r'^\d{6}$',
#         message='Le mot de passe doit contenir exactement 6 chiffres'
#     )
    
#     password = forms.CharField(
#         validators=[password_validator],
#         widget=forms.PasswordInput,
#         required=True
#     )
#     password_confirm = forms.CharField(
#         validators=[password_validator],
#         widget=forms.PasswordInput,
#         required=True
#     )
    
#     def clean(self):
#         cleaned_data = super().clean()
#         email = cleaned_data.get('email')
#         email_confirm = cleaned_data.get('email_confirm')
#         password = cleaned_data.get('password')
#         password_confirm = cleaned_data.get('password_confirm')
        
#         # Vérifier que les emails correspondent
#         if email and email_confirm and email != email_confirm:
#             raise forms.ValidationError('Les adresses email ne correspondent pas')
        
#         # Vérifier que les mots de passe correspondent
#         if password and password_confirm and password != password_confirm:
#             raise forms.ValidationError('Les mots de passe ne correspondent pas')
        
#         # Vérifier que le mot de passe contient exactement 6 chiffres
#         if password and (len(password) != 6 or not password.isdigit()):
#             raise forms.ValidationError('Le mot de passe doit contenir exactement 6 chiffres')
        
#         return cleaned_data

# formulaire connexion
class ConnexionForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control shadow',
        'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control shadow password-field',
        'placeholder': 'Mot de passe',
        'readonly': 'readonly'
    }))

# Gerant - informations générales et mot de passe
class BoulangerieInfoForm(forms.ModelForm):
    """Formulaire pour modifier les informations de la boulangerie"""
    class Meta:
        model = Boulangerie
        fields = ['nom', 'adresse', 'code', 'ville', 'telephone']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la boulangerie'
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code postal',
                'maxlength': '10'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone',
                'maxlength': '10'
            }),
        }
        labels = {
            'nom': 'Nom de la boulangerie',
            'adresse': 'Adresse',
            'code': 'Code postal',
            'ville': 'Ville',
            'telephone': 'Téléphone'
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulaire personnalisé pour changer le mot de passe"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les widgets
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe actuel'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe (6 chiffres)',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
        
        # Personnaliser les labels
        self.fields['old_password'].label = 'Mot de passe actuel'
        self.fields['new_password1'].label = 'Nouveau mot de passe'
        self.fields['new_password2'].label = 'Confirmer le mot de passe'

# Gerant - informations générales et mot de passe

class GerantInfoForm(forms.Form):
    """Formulaire pour modifier les informations du gérant avec téléphone"""
    first_name = forms.CharField(
        max_length=150,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa; cursor: not-allowed;'
        })
    )
    telephone = forms.CharField(
        max_length=10,
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone',
            'pattern': '[0-9]{10}',
            'title': 'Entrez un numéro à 10 chiffres'
        })
    )
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        if telephone and not telephone.isdigit():
            raise forms.ValidationError("Le téléphone doit contenir uniquement des chiffres.")
        return telephone

class CreerPersonnelForm(forms.Form):
    """Formulaire pour créer un compte personnel par le gérant"""
    nom = forms.CharField(
        max_length=150,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    
    prenom = forms.CharField(
        max_length=150,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    
    telephone = forms.CharField(
        max_length=10,
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone',
            'pattern': '[0-9]{10}',
            'title': 'Entrez un numéro à 10 chiffres'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    email_confirm = forms.EmailField(
        label='Confirmer l\'email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer l\'email'
        })
    )
    
    password = forms.CharField(
        max_length=6,
        min_length=6,
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe (6 chiffres)',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'title': '6 chiffres exactement'
        })
    )
    
    password_confirm = forms.CharField(
        max_length=6,
        min_length=6,
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        if telephone and not telephone.isdigit():
            raise forms.ValidationError("Le téléphone doit contenir uniquement des chiffres.")
        if telephone and len(telephone) != 10:
            raise forms.ValidationError("Le téléphone doit contenir exactement 10 chiffres.")
        return telephone
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password.isdigit():
            raise forms.ValidationError("Le mot de passe doit contenir uniquement des chiffres.")
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email_confirm = cleaned_data.get('email_confirm')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Vérifier que les emails correspondent
        if email and email_confirm and email != email_confirm:
            raise forms.ValidationError("Les emails ne correspondent pas.")
        
        # Vérifier que les mots de passe correspondent
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data