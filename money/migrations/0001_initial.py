# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Account'
        db.create_table('money_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sort_code', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('money', ['Account'])

        # Adding model 'Transaction'
        db.create_table('money_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Account'], null=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('memo', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('money', ['Transaction'])

        # Adding M2M table for field tags on 'Transaction'
        db.create_table('money_transaction_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('transaction', models.ForeignKey(orm['money.transaction'], null=False)),
            ('tag', models.ForeignKey(orm['money.tag'], null=False))
        ))
        db.create_unique('money_transaction_tags', ['transaction_id', 'tag_id'])

        # Adding model 'Tag'
        db.create_table('money_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('money', ['Tag'])

        # Adding model 'Payment'
        db.create_table('money_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payee', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('day_of_month', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('money', ['Payment'])


    def backwards(self, orm):
        
        # Deleting model 'Account'
        db.delete_table('money_account')

        # Deleting model 'Transaction'
        db.delete_table('money_transaction')

        # Removing M2M table for field tags on 'Transaction'
        db.delete_table('money_transaction_tags')

        # Deleting model 'Tag'
        db.delete_table('money_tag')

        # Deleting model 'Payment'
        db.delete_table('money_payment')


    models = {
        'money.account': {
            'Meta': {'object_name': 'Account'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'sort_code': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'money.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'day_of_month': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payee': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'money.tag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'money.transaction': {
            'Meta': {'ordering': "('-date', '-memo')", 'object_name': 'Transaction'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Account']", 'null': 'True'}),
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['money.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['money']
