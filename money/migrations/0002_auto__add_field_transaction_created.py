# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Transaction.created'
        db.add_column('money_transaction', 'created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, default=datetime.date(2012, 3, 16), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Transaction.created'
        db.delete_column('money_transaction', 'created')


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
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['money.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['money']
