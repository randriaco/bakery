from django.db import models

class Boulangerie(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    telephone = models.CharField(max_length=10, default="0123456789")

    def __str__(self):
        return self.nom
    
class Contact(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message de {self.nom}"
    
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.nom