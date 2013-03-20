# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Momend'
        db.create_table('DataManager_momend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('thumbnail', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('cryptic_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('momend_start_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('momend_end_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('privacy', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('DataManager', ['Momend'])

        # Adding model 'MomendStatus'
        db.create_table('DataManager_momendstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Momend'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('log_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['MomendStatus'])

        # Adding model 'DeletedMomend'
        db.create_table('DataManager_deletedmomend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('thumbnail', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('momend_start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('momend_end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('privacy', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('play_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['DeletedMomend'])

        # Adding model 'MomendScore'
        db.create_table('DataManager_momendscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['DataManager.Momend'], unique=True)),
            ('provider_score', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('DataManager', ['MomendScore'])

        # Adding model 'AnimationLayer'
        db.create_table('DataManager_animationlayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Momend'])),
            ('layer', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_interaction', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('DataManager', ['AnimationLayer'])

        # Adding model 'Provider'
        db.create_table('DataManager_provider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('package_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('module_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('worker_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['Provider'])

        # Adding model 'RawData'
        db.create_table('DataManager_rawdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('original_path', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('original_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('thumbnail', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('tags', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Provider'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('fetch_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('like_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('share_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('DataManager', ['RawData'])

        # Adding unique constraint on 'RawData', fields ['owner', 'original_id', 'provider']
        db.create_unique('DataManager_rawdata', ['owner_id', 'original_id', 'provider_id'])

        # Adding model 'DataEnrichmentWorker'
        db.create_table('DataManager_dataenrichmentworker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('applicable_to', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('worker_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['DataEnrichmentWorker'])

        # Adding M2M table for field compatible_with on 'DataEnrichmentWorker'
        db.create_table('DataManager_dataenrichmentworker_compatible_with', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataenrichmentworker', models.ForeignKey(orm['DataManager.dataenrichmentworker'], null=False)),
            ('provider', models.ForeignKey(orm['DataManager.provider'], null=False))
        ))
        db.create_unique('DataManager_dataenrichmentworker_compatible_with', ['dataenrichmentworker_id', 'provider_id'])

        # Adding model 'DataEnrichmentScenario'
        db.create_table('DataManager_dataenrichmentscenario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['DataEnrichmentScenario'])

        # Adding model 'DataEnrichmentScenarioItem'
        db.create_table('DataManager_dataenrichmentscenarioitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.DataEnrichmentScenario'])),
            ('worker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.DataEnrichmentWorker'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('multiplier', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('DataManager', ['DataEnrichmentScenarioItem'])

        # Adding unique constraint on 'DataEnrichmentScenarioItem', fields ['scenario', 'worker']
        db.create_unique('DataManager_dataenrichmentscenarioitem', ['scenario_id', 'worker_id'])

        # Adding model 'OutData'
        db.create_table('DataManager_outdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.AnimationLayer'])),
            ('raw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.RawData'], null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('selection_criteria', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('theme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Theme'], null=True, blank=True)),
            ('final_data_path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('animation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.CoreAnimationData'], null=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['OutData'])

        # Adding model 'CoreAnimationData'
        db.create_table('DataManager_coreanimationdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.AnimationGroup'])),
            ('order_in_group', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('used_object_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('used_theme_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.ThemeData'], null=True, blank=True)),
            ('extended_animation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('delay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('easing', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('pre', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('anim', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('waitPrev', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('triggerNext', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('force', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('click_animation', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='click_animation', null=True, to=orm['DataManager.UserInteractionAnimationGroup'])),
            ('hover_animation', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='hover_animation', null=True, to=orm['DataManager.UserInteractionAnimationGroup'])),
            ('shadow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.DynamicShadow'], null=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['CoreAnimationData'])

        # Adding model 'DynamicShadow'
        db.create_table('DataManager_dynamicshadow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('max_x', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_y', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('blur', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('spread', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('color', self.gf('django.db.models.fields.CharField')(default='rgba(0, 0, 0, 0.8)', max_length=50)),
            ('inset', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('DataManager', ['DynamicShadow'])

        # Adding model 'ImageEnhancement'
        db.create_table('DataManager_imageenhancement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('script_path', self.gf('django.db.models.fields.TextField')()),
            ('parameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('example_path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['ImageEnhancement'])

        # Adding model 'PostEnhancement'
        db.create_table('DataManager_postenhancement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('filepath', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('used_object_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['PostEnhancement'])

        # Adding model 'AppliedPostEnhancement'
        db.create_table('DataManager_appliedpostenhancement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('outdata', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.OutData'])),
            ('filepath', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parameters', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['AppliedPostEnhancement'])

        # Adding model 'EnhancementGroup'
        db.create_table('DataManager_enhancementgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('enhancement_functions', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=255, null=True, blank=True)),
            ('post_enhancement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('applicable_to', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('DataManager', ['EnhancementGroup'])

        # Adding model 'Theme'
        db.create_table('DataManager_theme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['Theme'])

        # Adding M2M table for field enhancement_groups on 'Theme'
        db.create_table('DataManager_theme_enhancement_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('theme', models.ForeignKey(orm['DataManager.theme'], null=False)),
            ('enhancementgroup', models.ForeignKey(orm['DataManager.enhancementgroup'], null=False))
        ))
        db.create_unique('DataManager_theme_enhancement_groups', ['theme_id', 'enhancementgroup_id'])

        # Adding model 'ThemeData'
        db.create_table('DataManager_themedata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('theme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Theme'])),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('data_path', self.gf('django.db.models.fields.TextField')()),
            ('parameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['ThemeData'])

        # Adding model 'Scenario'
        db.create_table('DataManager_scenario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['Scenario'])

        # Adding M2M table for field compatible_themes on 'Scenario'
        db.create_table('DataManager_scenario_compatible_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scenario', models.ForeignKey(orm['DataManager.scenario'], null=False)),
            ('theme', models.ForeignKey(orm['DataManager.theme'], null=False))
        ))
        db.create_unique('DataManager_scenario_compatible_themes', ['scenario_id', 'theme_id'])

        # Adding model 'AnimationGroup'
        db.create_table('DataManager_animationgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Scenario'], null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('needed_bg', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('needed_music', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('needed_photo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('needed_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('needed_location', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('DataManager', ['AnimationGroup'])

        # Adding model 'UserInteractionAnimationGroup'
        db.create_table('DataManager_userinteractionanimationgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('stop_current_animation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('clear_further_animations', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disable_further_interaction', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('animations', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.AnimationGroup'])),
        ))
        db.send_create_signal('DataManager', ['UserInteractionAnimationGroup'])

        # Adding model 'AnimationPlayStat'
        db.create_table('DataManager_animationplaystat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Momend'], null=True, blank=True)),
            ('interaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.UserInteraction'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('redirect_url', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('DataManager', ['AnimationPlayStat'])

        # Adding model 'UserInteraction'
        db.create_table('DataManager_userinteraction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DataManager.Momend'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('interaction', self.gf('django.db.models.fields.TextField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('cryptic_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('DataManager', ['UserInteraction'])

        # Adding model 'DeletedUserInteraction'
        db.create_table('DataManager_deleteduserinteraction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('momend_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('creator_id', self.gf('django.db.models.fields.IntegerField')()),
            ('momend_owner_deleted', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('delete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('DataManager', ['DeletedUserInteraction'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataEnrichmentScenarioItem', fields ['scenario', 'worker']
        db.delete_unique('DataManager_dataenrichmentscenarioitem', ['scenario_id', 'worker_id'])

        # Removing unique constraint on 'RawData', fields ['owner', 'original_id', 'provider']
        db.delete_unique('DataManager_rawdata', ['owner_id', 'original_id', 'provider_id'])

        # Deleting model 'Momend'
        db.delete_table('DataManager_momend')

        # Deleting model 'MomendStatus'
        db.delete_table('DataManager_momendstatus')

        # Deleting model 'DeletedMomend'
        db.delete_table('DataManager_deletedmomend')

        # Deleting model 'MomendScore'
        db.delete_table('DataManager_momendscore')

        # Deleting model 'AnimationLayer'
        db.delete_table('DataManager_animationlayer')

        # Deleting model 'Provider'
        db.delete_table('DataManager_provider')

        # Deleting model 'RawData'
        db.delete_table('DataManager_rawdata')

        # Deleting model 'DataEnrichmentWorker'
        db.delete_table('DataManager_dataenrichmentworker')

        # Removing M2M table for field compatible_with on 'DataEnrichmentWorker'
        db.delete_table('DataManager_dataenrichmentworker_compatible_with')

        # Deleting model 'DataEnrichmentScenario'
        db.delete_table('DataManager_dataenrichmentscenario')

        # Deleting model 'DataEnrichmentScenarioItem'
        db.delete_table('DataManager_dataenrichmentscenarioitem')

        # Deleting model 'OutData'
        db.delete_table('DataManager_outdata')

        # Deleting model 'CoreAnimationData'
        db.delete_table('DataManager_coreanimationdata')

        # Deleting model 'DynamicShadow'
        db.delete_table('DataManager_dynamicshadow')

        # Deleting model 'ImageEnhancement'
        db.delete_table('DataManager_imageenhancement')

        # Deleting model 'PostEnhancement'
        db.delete_table('DataManager_postenhancement')

        # Deleting model 'AppliedPostEnhancement'
        db.delete_table('DataManager_appliedpostenhancement')

        # Deleting model 'EnhancementGroup'
        db.delete_table('DataManager_enhancementgroup')

        # Deleting model 'Theme'
        db.delete_table('DataManager_theme')

        # Removing M2M table for field enhancement_groups on 'Theme'
        db.delete_table('DataManager_theme_enhancement_groups')

        # Deleting model 'ThemeData'
        db.delete_table('DataManager_themedata')

        # Deleting model 'Scenario'
        db.delete_table('DataManager_scenario')

        # Removing M2M table for field compatible_themes on 'Scenario'
        db.delete_table('DataManager_scenario_compatible_themes')

        # Deleting model 'AnimationGroup'
        db.delete_table('DataManager_animationgroup')

        # Deleting model 'UserInteractionAnimationGroup'
        db.delete_table('DataManager_userinteractionanimationgroup')

        # Deleting model 'AnimationPlayStat'
        db.delete_table('DataManager_animationplaystat')

        # Deleting model 'UserInteraction'
        db.delete_table('DataManager_userinteraction')

        # Deleting model 'DeletedUserInteraction'
        db.delete_table('DataManager_deleteduserinteraction')


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
            'Meta': {'unique_together': "(('owner', 'original_id', 'provider'),)", 'object_name': 'RawData'},
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