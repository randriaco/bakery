# Generated by Django 5.1.6 on 2025-07-16 15:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_tokenreinitialisationmotdepasse'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='frequencecollecte',
            options={'verbose_name': 'Fréquence de collecte', 'verbose_name_plural': 'Fréquence de collecte'},
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_commande', models.CharField(editable=False, max_length=20, unique=True)),
                ('date_commande', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_collecte', models.DateField()),
                ('heure_collecte', models.TimeField()),
                ('statut', models.CharField(choices=[('en_attente', 'En attente de paiement'), ('payee', 'Payée'), ('en_preparation', 'En préparation'), ('prete', 'Prête'), ('recuperee', 'Récupérée'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('sous_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('frais_service', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stripe_session_id', models.CharField(blank=True, max_length=200, null=True)),
                ('stripe_payment_intent', models.CharField(blank=True, max_length=200, null=True)),
                ('email_confirmation_envoye', models.BooleanField(default=False)),
                ('facture_envoyee', models.BooleanField(default=False)),
                ('date_paiement', models.DateTimeField(blank=True, null=True)),
                ('date_preparation', models.DateTimeField(blank=True, null=True)),
                ('date_prete', models.DateTimeField(blank=True, null=True)),
                ('date_recuperation', models.DateTimeField(blank=True, null=True)),
                ('notes_client', models.TextField(blank=True)),
                ('notes_interne', models.TextField(blank=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_commande'],
            },
        ),
        migrations.CreateModel(
            name='LigneCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_produit', models.CharField(max_length=200)),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('categorie', models.CharField(max_length=100)),
                ('quantite', models.PositiveIntegerField()),
                ('sous_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='main.commande')),
                ('produit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.produit')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now)),
                ('vue', models.BooleanField(default=False)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.commande')),
            ],
            options={
                'ordering': ['-date_creation'],
            },
        ),
    ]
