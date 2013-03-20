# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'RawData', fields ['owner', 'original_id', 'provider']
        db.delete_unique('DataManager_rawdata', ['owner_id', 'original_id', 'provider_id'])

        # Adding unique constraint on 'RawData', fields ['original_id', 'provider']
        db.create_unique('DataManager_rawdata', ['original_id', 'provider_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'RawData', fields ['original_id', 'provider']
        db.delete_unique('DataManager_rawdata', ['original_id', 'provider_id'])

        # Adding unique constraint on 'RawData', fields ['owner', 'original_id', 'provider']
        db.create_unique('DataManager_rawdata', ['owner_id', 'original_id', 'provider_id'])


    models = {
        'DataManager.animationgroup': {
            'Meta': {'object_name': 'AnimationGroup'},
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'needed_bg': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'needed_location': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'needed_music': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'needed_photo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'needed_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Scenario']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'DataManager.animationlayer': {
            'Meta': {'object_name': 'AnimationLayer'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_interaction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'layer': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'momend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Momend']"})
        },
        'DataManager.animationplaystat': {
            'Meta': {'object_name': 'AnimationPlayStat'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.UserInteraction']", 'null': 'True', 'blank': 'True'}),
            'momend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Momend']", 'null': 'True', 'blank': 'True'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'DataManager.appliedpostenhancement': {
            'Meta': {'object_name': 'AppliedPostEnhancement'},
            'filepath': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'outdata': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.OutData']"}),
            'parameters': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.coreanimationdata': {
            'Meta': {'object_name': 'CoreAnimationData'},
            'anim': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'click_animation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'click_animation'", 'null': 'True', 'to': "orm['DataManager.UserInteractionAnimationGroup']"}),
            'delay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'easing': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'extended_animation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'force': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.AnimationGroup']"}),
            'hover_animation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'hover_animation'", 'null': 'True', 'to': "orm['DataManager.UserInteractionAnimationGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order_in_group': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pre': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shadow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.DynamicShadow']", 'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'triggerNext': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'used_object_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'used_theme_data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.ThemeData']", 'null': 'True', 'blank': 'True'}),
            'waitPrev': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'DataManager.dataenrichmentscenario': {
            'Meta': {'object_name': 'DataEnrichmentScenario'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.dataenrichmentscenarioitem': {
            'Meta': {'unique_together': "(('scenario', 'worker'),)", 'object_name': 'DataEnrichmentScenarioItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiplier': ('django.db.models.fields.IntegerField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.DataEnrichmentScenario']"}),
            'worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.DataEnrichmentWorker']"})
        },
        'DataManager.dataenrichmentworker': {
            'Meta': {'object_name': 'DataEnrichmentWorker'},
            'applicable_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'compatible_with': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['DataManager.Provider']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'worker_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.deletedmomend': {
            'Meta': {'object_name': 'DeletedMomend'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'momend_end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'momend_start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'play_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'privacy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'})
        },
        'DataManager.deleteduserinteraction': {
            'Meta': {'object_name': 'DeletedUserInteraction'},
            'creator_id': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'momend_id': ('django.db.models.fields.IntegerField', [], {}),
            'momend_owner_deleted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'DataManager.dynamicshadow': {
            'Meta': {'object_name': 'DynamicShadow'},
            'blur': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'color': ('django.db.models.fields.CharField', [], {'default': "'rgba(0, 0, 0, 0.8)'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'max_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'spread': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'DataManager.enhancementgroup': {
            'Meta': {'object_name': 'EnhancementGroup'},
            'applicable_to': ('django.db.models.fields.IntegerField', [], {}),
            'enhancement_functions': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post_enhancement': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'DataManager.imageenhancement': {
            'Meta': {'object_name': 'ImageEnhancement'},
            'example_path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'script_path': ('django.db.models.fields.TextField', [], {})
        },
        'DataManager.momend': {
            'Meta': {'object_name': 'Momend'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cryptic_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'momend_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'momend_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'privacy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'})
        },
        'DataManager.momendscore': {
            'Meta': {'object_name': 'MomendScore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'momend': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['DataManager.Momend']", 'unique': 'True'}),
            'provider_score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'DataManager.momendstatus': {
            'Meta': {'object_name': 'MomendStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'log_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'momend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Momend']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'DataManager.outdata': {
            'Meta': {'object_name': 'OutData'},
            'animation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.CoreAnimationData']", 'null': 'True', 'blank': 'True'}),
            'final_data_path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.AnimationLayer']"}),
            'parameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'raw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.RawData']", 'null': 'True', 'blank': 'True'}),
            'selection_criteria': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Theme']", 'null': 'True', 'blank': 'True'})
        },
        'DataManager.postenhancement': {
            'Meta': {'object_name': 'PostEnhancement'},
            'filepath': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parameters': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'used_object_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'DataManager.provider': {
            'Meta': {'object_name': 'Provider'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'package_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'worker_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.rawdata': {
            'Meta': {'unique_together': "(('original_id', 'provider'),)", 'object_name': 'RawData'},
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'fetch_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'original_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'original_path': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Provider']"}),
            'share_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'DataManager.scenario': {
            'Meta': {'object_name': 'Scenario'},
            'compatible_themes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['DataManager.Theme']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.theme': {
            'Meta': {'object_name': 'Theme'},
            'enhancement_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['DataManager.EnhancementGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'DataManager.themedata': {
            'Meta': {'object_name': 'ThemeData'},
            'data_path': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Theme']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'DataManager.userinteraction': {
            'Meta': {'object_name': 'UserInteraction'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'cryptic_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interaction': ('django.db.models.fields.TextField', [], {}),
            'momend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.Momend']"})
        },
        'DataManager.userinteractionanimationgroup': {
            'Meta': {'object_name': 'UserInteractionAnimationGroup'},
            'animations': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['DataManager.AnimationGroup']"}),
            'clear_further_animations': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disable_further_interaction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'stop_current_animation': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['DataManager']