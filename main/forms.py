from django import forms
from .models import Categorie, Produit

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