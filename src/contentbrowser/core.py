from django.conf import settings
from django.contrib.contenttypes.models import ContentType

class ContentBrowser(object):
	_cached_types = []
	_querysets = {}

	def __init__(self, custom_types=None):
		if not custom_types:
			self._registered_types = getattr(
				settings, 'CONTENT_BROWSER_TYPES', None)
		else:
			self._registered_types = custom_types

	def get_types(self, flush=False):
		"""
		Returns a list of dictionaries, containing the contenttype reference,
		and the verbose name of the Model.

		``flush`` can be used to force the cache to be cleared

		returns:
			[{'contenttype': 'app.model', 'verbose_name': '', 'verbose_name_plural': ''}, ... ]
		"""
		if not self._cached_types or flush:
			for ctype in self._registered_types:
				self._cached_types = []

				app, model_name = ctype.split('.')
				ct = ContentType.objects.get(app_label=app, model=model_name)	
				ct_model = ct.model_class()

				self._cached_types.append({
					'contenttype': ctype,
					'verbose_name': ct_model._meta.verbose_name.title(),
					'verbose_name_plural': ct_model._meta.verbose_name_plural.title(),
				})
		return self._cached_types

	def get_model_for(self, ctype):
		"""
		Returns a django queryset for ``ctype``
		"""
		app, model_name = ctype.split('.')
		ct = ContentType.objects.get(app_label=app, model=model_name)
		return ct.model_class()

	def get_items_for(self, ctype):
		"""
		Returns a django queryset, containing all the valid items for ``ctype``
		"""
		if ctype not in self._querysets:
			app, model_name = ctype.split('.')
			ct = ContentType.objects.get(app_label=app, model=model_name)
			ct_model = ct.model_class()
			self._querysets[ctype] = ct_model.objects.all()

		return self._querysets[ctype]


	def set_queryset_for(self, ctype, queryset):
		self._querysets[ctype] = queryset
