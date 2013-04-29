__author__ = 'goktan'
from LogManagers.Log import Log
from DataManager.models import Momend
from DataManager.models import RawData
from DataManager.models import DataEnrichmentScenarioItem
from DataManager.models import Provider
import importlib


class DataEnrichManager(object):
    def __init__(self, user, raw_data_arr, scenario):
        self.user = user
        self.scenario = scenario
        self.enriched_data_groups = []
        self.raw_data_groups = []
        for i in range(len(RawData.DATA_TYPE)):  # Group RawData by type
            self.enriched_data_groups.append([])
            self.raw_data_groups.append([])
        for _raw in raw_data_arr:
            tmp = TemporaryEnrichedObjectHolder(raw=_raw)
            self.enriched_data_groups[_raw.type].append(tmp)
            self.raw_data_groups[_raw.type].append(_raw)

    def filter_user_data(self, filter_to_apply):
        if len(filter_to_apply) == 0:
            return
        _provider_raw_data_group = []
        for i in range(len(RawData.DATA_TYPE)):
            _provider_raw_data_group.append({})
        _provider_workers = dict()
        for _provider in Provider.objects.all():
            _provider_workers[_provider.id] = _provider.instantiate_provider_worker()
            for _type in _provider_raw_data_group:
                _type[_provider.id] = []

        for index, _type in enumerate(self.raw_data_groups):
            if len(_type) > 0:
                for _raw in _type:
                    _provider_raw_data_group[index][_raw.provider_id].append(_raw)

        for _type in _provider_raw_data_group:
            for _provider_group in _type:
                if len(_type[_provider_group]) > 0:
                    if 'friends' in filter_to_apply and filter_to_apply['friends']:
                        Log.info('Applying friend filter')
                        _type[_provider_group] = _provider_workers[_provider_group].filter_for_friends(_type[_provider_group], filter_to_apply['friends'])

        _filtered_raw_data = []
        _enriched_raw_data = []
        for i in range(len(RawData.DATA_TYPE)):
            _filtered_raw_data.append([])
            _enriched_raw_data.append([])
        for index, _type in enumerate(_provider_raw_data_group):
            for _provider_group in _type:
                _filtered_raw_data[index] = _filtered_raw_data[index] + _type[_provider_group]
                for _raw in _type[_provider_group]:
                    _enriched_raw_data[index].append(TemporaryEnrichedObjectHolder(_raw))

        self.raw_data_groups = _filtered_raw_data
        self.enriched_data_groups = _enriched_raw_data

    def get_enriched_user_raw_data(self):
        """get list of user raw data smartly according to its relevance to user.
        Returns:
            an array of ordered raw data (aka. enriched data) in groups
            i.e. [
                    [0] - > [photo1, photo2]
                    [1] - > [status1, status2]
                    ...
                 ]
        """
        _items_of_scenario = DataEnrichmentScenarioItem.objects.filter(scenario=self.scenario).order_by('order')
        for _enhancement_item in _items_of_scenario:
            _worker_model = _enhancement_item.worker
            _worker_instance = None  # Stays None until first needed

            for _type in range(len(RawData.DATA_TYPE)):
                if len(self.raw_data_groups[_type]) > 0:  # If there is data for this type
                    if not _worker_model.applicable_to or _worker_model.applicable_to == _type:  # Whether worker is applicable to every type, or this type
                        if not _worker_instance:
                            _worker_instance = DataEnrichManager._instantiate_enrich_worker(_worker_model.worker_name)
                        _results = _worker_instance.enrich(self.raw_data_groups[_type], _type, _worker_model.compatible_with.all())  # Base class'es enrich function delegates the call to right function according to _type parameter
                                                                                        # Also sending the compatible providers, so it won't process them
                        if not _results:
                            continue
                        for i in range(len(_results)):
                            if _results[i] is not None:  # If the worker processed this item
                                self.enriched_data_groups[_type][i].criteria.append(_worker_model.name)
                                self.enriched_data_groups[_type][i].multiplier.append(_enhancement_item.multiplier)
                                self.enriched_data_groups[_type][i].priority.append(_results[i])

        Log.debug('Enrich results: ' + str(self.enriched_data_groups))
        for _layer in self.enriched_data_groups:  # Merging layers of enrichment results
            for _item in _layer:
                _weight = sum(_item.multiplier)
                if _weight > 0:
                    _weight += 0.0  # To make float division
                    _total = 0
                    if type(_item.priority) == float:
                        _total = _item.priority
                    else:
                        for i, _score in enumerate(_item.priority):  # To calculate weighted priority (i.e. if total weight was 50 and total score was 35, then score will be 70)
                            _total += _score * (_item.multiplier[i] / _weight)

                    _item.priority = _total
                    _item.criteria = ','.join(_item.criteria)
                else:  # There wasn't any enrichment for this data
                    _item.priority = 0
                    _item.criteria = 'No matching criteria'
        return self._sort_by_priority()

    @staticmethod
    def _instantiate_enrich_worker(name):
        mod = importlib.import_module('DataManager.DataEnrich.DataEnrichWorkers.' + name, name)
        cl = getattr(mod, name)
        return cl()

    def _sort_by_priority(self):
        _sorted_data = []
        for _type_arr in self.enriched_data_groups:
            _sorted_data.append(sorted(_type_arr, key=lambda obj: obj.priority, reverse=True))
        return _sorted_data

    @staticmethod
    def get_related_momends(momend, max_count, get_private=True):
        """get list of top momends for a specific user
        Args:
            momend: momend to set reference for related momends
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated related momends
        """
        _obj = Momend.objects.filter(owner=momend.owner)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('?').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]

    @staticmethod
    def get_top_user_momends(user, max_count, get_private=True):  # TODO (goktan): here we need an algorithm
        """get list of top momends for a specific user
        Args:
            user: user to get momend
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated top user momends
        """
        _obj = Momend.objects.filter(owner=user)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('?').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]

    @staticmethod
    def get_top_public_momends(max_count):
        """get lit of top public moments
        Args:
            max_count: maximum momend number to return

        Returns:
            an array of curated top public momends
        """
        _obj = Momend.objects.filter(privacy=Momend.PRIVACY_CHOICES['Public']).order_by('create_date').reverse()

        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]

    @staticmethod
    def get_latest_user_momends(user, max_count, get_private=True):
        """get list of users latest momends
        Args:
            user: user to get momend
            max_count: maximum momend number to return
            get_private: if True, then include the private momends to the result

        Returns:
            an array of curated top user momends
        """
        _obj = Momend.objects.filter(owner=user)
        if not get_private:
            _obj = _obj.filter(privacy=Momend.PRIVACY_CHOICES['Public'])
        _obj = _obj.order_by('create_date').reverse()
        return _obj if (_obj.count() < max_count) else _obj[_obj.count() - max_count:]


class TemporaryEnrichedObjectHolder(object):
    def __init__(self, raw):
        self.raw = raw
        self.criteria = []
        self.multiplier = []
        self.priority = []

    def __str__(self):
        return str(self.raw) + '=' + str(self.criteria) + ':' + str(self.priority)

    def __repr__(self):
        return self.__str__()
